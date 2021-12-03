import sys, os, requests, copy, logging
import pymysql
import pkg_resources 
from datetime           import time, timedelta, datetime, tzinfo, date
from ig.instagram_utils import InstagramUtils
#from alerts_pb2 import InternalAlert

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
is_imported = None

class CompetitorsMediaFetcher:

  SOURCE_DF = "%Y-%m-%dT%H:%M:%S"
  TARGET_DF = "%Y-%m-%d %H:%M:%S"

  ### Build CompetitorsMediaFetcher according to how it's being used
  def __init__(self, args = None):
    try:
      if is_imported:
        print('CompetitorsMediaFetcher init as module')
        logger, conf_file = config_fetcher_as_module()
        self.logger = logger
        self.utils = InstagramUtils()
        self.utils.init(conf_file, True)
      else:
        print('CompetitorsMediaFetcher init as main')
        logger = config_fetcher_as_main()
        self.logger = logger
        if args == None or len(args) == 0:
          self.logger.debug("Initializing with defaults")
          conf_file = "ig/conf/get_business_competitors_media.yaml"
          self.utils = InstagramUtils()
          self.utils.init(conf_file, True) 
        elif len(args) == 1:
          self.logger.debug("Initializing with params")
          conf_file = args[0]
          self.utils = InstagramUtils()
          self.utils.init(conf_file, True)
        else:
          msg = 'Error executing script: incorrect parameters. \
          Provide either no arguments, or [config_file]'
          self.logger.exception(msg)
          raise Exception(msg)
        self.logger.debug("Set conf_file '%s'" % (conf_file))
    except:
      self.logger.exception('Error initializing CompetitorsMediaFetcher')


  ### Process all competitors from database
  def process_all(self):
    try:
      # pagination exists but doesnt work, only returns first page
      exec_start_time = datetime.now()
      conn = self.utils.get_conn('ig')
      users = self.get_users(conn)
      for item in users:
        user_id = item[0]
        competitor_name = item[1]
        access_token = item[2]
        self.process_competitors_media(conn, user_id, competitor_name, access_token)
      conn.close()
    except:
      self.logger.exception("Error while preparing to process all")
    finally:
      self.logger.info('Total time: %s' % (datetime.now() - exec_start_time))


  def request_data(self, user_id, competitor_name, access_token):
    host = self.utils.from_config('graph_api.host')
    path = self.utils.from_config('graph_api.request_path').format(**locals())
    url = '%s%s'%(host,path)
    payload = {'access_token': access_token}
    if self.utils.has_trace_enabled():
      self.logger.debug('Url: %s' % url)
      self.logger.debug('Payload: %s' % payload)
    response = requests.get(url, params=payload)
    response_as_json = self.utils.response_as_json(response)
    return response_as_json 


  ### Get users from database
  def get_users(self, conn):
    users = list()
    try:
      query = self.utils.from_config("queries.get_users")
      cursor = conn.cursor(pymysql.cursors.SSCursor)
      cursor.execute(query)
      while (1):
        row = cursor.fetchone()
        if not row:
          break
        user_id = row[0].decode('UTF-8')
        competitor_name = row[1].decode('UTF-8')
        access_token = row[2].decode('UTF-8')
        users.append((user_id, competitor_name, access_token))
        self.logger.debug("Adding pair %s, %s"%(user_id, competitor_name))
      cursor.close()
      self.logger.debug("Added %s pairs "%(len(users)))
    except:
      self.logger.exception("Error while getting users")
    return users


  ### Parse and insert a page of results
  def parse_and_insert(self, conn, base_user_id, competitor_name, data):
    competitor_id = data.get("id")
    user_values = {"id": competitor_id,
                   "username": data.get("username"),
                   "media_count": data.get("media_count"),
                   "followers_count": data.get("followers_count"),
                   "follows_count": data.get("follows_count")}
    command =self.utils.from_config('queries.insert_user').format(**user_values)
    self.logger.debug("insert_user command: %s" % command)
    cursor = conn.cursor() 
    cursor.execute(command)
    conn.commit()
    cursor.close()

    comp_values = {"instagram_competitor_id": competitor_id,
                   "instagram_id": base_user_id,
                   "competitor_name": competitor_name}
    command = self.utils.from_config('queries.update_competitor').format(**comp_values)
    self.logger.debug("update_competitor command: %s" % command)
    cursor = conn.cursor() 
    cursor.execute(command)
    conn.commit()
    cursor.close()
  
    cursor = conn.cursor()
    cursor.execute('SET character_set_connection=utf8mb4;')
    for item in data.get("media").get("data"):
      created_datetime = datetime.strptime(item.get("timestamp")[:19],self.SOURCE_DF)
      created_at = datetime.strftime(created_datetime, self.TARGET_DF)
      values = {"id" : str(item.get("id")),
                "user_id": str(competitor_id),
                "created_at": str(created_at),
                "fetched_at": str(datetime.utcnow()),
                "type": str(item.get("media_type", '')),
                "caption": str(item.get("caption", '')).replace("'",'"'),
                "url": str(item.get("permalink", '')),
                "likes_count": item.get("like_count", 0),
                "comments_count": item.get("comments_count", 0),
                "image": str(item.get("media_url", ''))}
      command = self.utils.from_config('queries.insert_media').format(**values)
      if self.utils.has_trace_enabled():
          self.logger.debug("insert_media command: %s" % command)
      cursor.execute(command)
    conn.commit()
    cursor.close()

  
  # IP 189.216.115.149/32
# def send_alert(alert_text, alert_type, alert_priority):
#   alert = InternalAlert()
#   alert.priority = alert_priority    # {INFO, WARN, SEVERE}
#   alert.type = "IG_FETCH_MEDIA"
#   alert.project = alert_type
#   alert.text = alert_text
#   alert.created_at = int((datetime.utcnow()-datetime(1970,1,1)).total_seconds())*1000
#   body = alert.SerializeToString()
#   url='http://trb-message-exchange-hrd.appspot.com/alert/internal'
#   self.logger.debug('alert url: %s' % url)
#   self.logger.debug('alert body: %s...' % body[:250])
#   r = requests.post(url, body)


  ### Main function
  def process_competitors_media(self, conn, user_id, competitor, access_token):
    try:
      self.logger.info("##############################################")
      self.logger.info("Getting media for %s,%s" % (user_id,competitor))
      response = self.request_data(user_id,competitor,access_token)
      if response:
        self.parse_and_insert(conn, user_id, competitor,
                              response.get('business_discovery'))
    except:
      self.logger.exception("Error while parsing or inserting %s" % competitor)

      

### If used as main: set Stream+File log handlers and local config file
def config_fetcher_as_main():
  print('CompetitorsMediaFetcher setting Stream+File log handlers and local config file.')

  # configure root logger
  frmttr = logging.Formatter(LOG_FORMAT)
  logger = logging.getLogger() # root logger 
  logger.setLevel('DEBUG')

  # add console handler
  ch = logging.StreamHandler()
  ch.setFormatter(frmttr)
  logger.addHandler(ch)

  # add file handler
  log_file = 'logs/get_business_competitors_media.log'
  d = os.path.dirname(log_file)
  if not os.path.exists(d) and d != '':
    os.makedirs(d)
  fh = logging.FileHandler(log_file)
  fh.setFormatter(frmttr)
  logger.addHandler(fh)

  # configure other loggers
  logging.getLogger('urllib3').setLevel('WARNING')
  logging.getLogger('shared').setLevel('INFO')

  # initialize Fetcher with local file
  return (logger)


### If used as module: set Stream log handler and packaged config file
def config_fetcher_as_module():
  print('CompetitorsMediaFetcher setting Stream log handler and packaged config file')

  # configure module logger
  frmttr = logging.Formatter(LOG_FORMAT)
  logger = logging.getLogger(__name__) # module logger
  logger.setLevel('DEBUG')

  # add console handler
  ch = logging.StreamHandler()
  ch.setFormatter(frmttr)
  logger.addHandler(ch)

  # configure other loggers
  logging.getLogger('urllib3').setLevel('WARNING')
  logging.getLogger('shared').setLevel('INFO')

  # initialize Fetcher with packaged file
  resource_package = __name__
  resource_path = '/'.join(('conf', 'get_business_competitors_media.yaml'))
  conf_file = pkg_resources.resource_filename(resource_package, resource_path)
  return (logger, conf_file)


### Entrypoint

if __name__ == '__main__':
  # Program used as script: run immediately
  try:
    fetcher = CompetitorsMediaFetcher(sys.argv[1:])
    fetcher.process_all()
  except:
     print('Error initializing CompetitorsMediaFetcher')
else:
  # Program used as import: set flag
  is_imported = True


     
