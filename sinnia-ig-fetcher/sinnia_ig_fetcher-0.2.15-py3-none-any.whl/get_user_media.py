import sys, os, requests, logging
import pymysql
import pkg_resources 
from datetime           import time, timedelta, datetime, tzinfo, date
from ig.instagram_utils import InstagramUtils
#from alerts_pb2 import InternalAlert

# https://developers.facebook.com/docs/instagram-basic-display-api/reference/user/media

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
is_imported = None

class UserMediaFetcher:

  SOURCE_DF = "%Y-%m-%dT%H:%M:%S"
  TARGET_DF = "%Y-%m-%d %H:%M:%S"

  ### Build UserMediaFetcher according to how it's being used
  def __init__(self):
    try:
      if is_imported:
        print('UserMediaFetcher as module')
        logger, conf_file = config_fetcher_as_module()
      else:
        print('UserMediaFetcher as main')
        logger, conf_file = config_fetcher_as_main()
      self.logger = logger
      self.utils = InstagramUtils()
      self.utils.init(conf_file, True)
    except:
      self.logger.exception('Error initializing UserMediaFetcher')


  def build_user_url(self, user_id, access_token):
    host = self.utils.from_config('graph_api.host')
    path = self.utils.from_config('graph_api.request_user_path').format(**locals())
    return '%s%s'%(host,path)


  def build_media_url(self, user_id, access_token, date_from, date_to):
    host =self.utils.from_config('graph_api.host')
    path =self.utils.from_config('graph_api.request_media_path').format(**locals())
    historic = ''
    if (date_from != None and date_to != None): 
      historic = self.utils.from_config('graph_api.historic_suffix').format(**locals())
    return '%s%s%s'%(host,path,historic)

  def process_all(self, dates_arr):  
    try:
      exec_start_time = datetime.now()
      date_from, date_to = self.utils.get_start_end_str(dates_arr) # signature changed
      conn = self.utils.get_conn('ig')
      users = self.get_users(conn)
      for item in users:
        user_id = item[0]
        access_token = item[1]
        self.process_user_media(conn, user_id, access_token, date_from, date_to)
      conn.close()
    except:
      self.logger.exception('Error preparing to process all')
    finally:
      self.logger.info('Total time: %s' % (datetime.now() - exec_start_time))

    
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
          access_token = row[1].decode('UTF-8')
          users.append((user_id, access_token))
          self.logger.debug("Adding user_id %s"%(user_id))
        cursor.close()
        self.logger.debug("Added %s users "%(len(users)))
    except:
      self.logger.exception("Error while getting users")
    return users


  def parse_and_insert_info(self, conn, user_id, data):
    if len(data) == 0:
      return
    values = {"id": user_id,
            "username": data.get("username"),
            "account_type": data.get("account_type"),
            "media_count": data.get("media_count")}
    command = self.utils.from_config('queries.insert_user').format(**values)
    cursor = conn.cursor()
    if self.utils.has_trace_enabled():
      self.logger.debug("insert user command: %s" % command)
    cursor.execute(command)
    conn.commit()
    cursor.close()
    return user_id


  def parse_and_insert_media(self, conn, user_id, data, is_story=False):
    if len(data) == 0:
      return  
    cursor = conn.cursor()
    cursor.execute('SET character_set_connection=utf8mb4;')
    for item in data:
      created_datetime = datetime.strptime(item["timestamp"][:19], self.SOURCE_DF)
      created_at = datetime.strftime(created_datetime, self.TARGET_DF)
      values = {"id" : str(item["id"]),
                "user_id": str(user_id),
                "created_at": str(created_at),
                "fetched_at": str(datetime.utcnow()),
                "type": str(item.get("media_type",'')),
                "caption": item.get("caption", '').replace("'",'"'),
                "url": str(item.get("permalink", '')),
                "image": str(item.get("media_url", '')),
                "is_story": 1 if is_story else 0}
      min_date = created_at
      command = self.utils.from_config('queries.insert_media').format(**values)
      if self.utils.has_trace_enabled():
        self.logger.debug("insert media command: %s" % command)
      cursor.execute(command)
    conn.commit()
    cursor.close()
    return min_date

  
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


  def process_user_media(self, conn, user_id, access_token, date_from_param = None, date_to_param = None):
    try:
      if date_from_param != None and date_to_param != None:
        date_from, date_to = self.utils.get_start_end_str(date_from_param, date_to_param) 
      else:
        date_from = self.utils.get_yesterday()
        date_to   = date.today()
      self.logger.info("##############################################")
      self.logger.info("UserMediaFetcher process_user_info for %s" % user_id)
      url = self.build_user_url(user_id, access_token)
      response = self.utils.request_data(url, access_token)
      if response:
        self.parse_and_insert_info(conn, user_id, response)
            
      self.logger.info("##############################################")
      self.logger.info("UserMediaFetcher process_user_media for %s" % user_id)
      paginate = True
      url = self.build_media_url(user_id, access_token, date_from, date_to)
      while paginate:
        response = self.utils.request_data(url, access_token)
        if response and response.get('data'):
          data = response.get('data')
          next_url = response.get('paging').get('next')
          self.logger.debug("pagination next_url=%s"%next_url)
          min_date = self.parse_and_insert_media(conn, user_id, data)
          self.logger.debug("pagination min_date=%s"%min_date)
          if min_date < date_from or next_url == None:
            self.logger.debug("pagination stopped: min_date=%s"%min_date)
            paginate = False
          url = next_url
        else:
          paginate = False
    except:
      self.logger.exception("Error while parsing or inserting user or media")

        
### If used as main: set Stream+File log handlers and local config file
def config_fetcher_as_main():
  print('Setting Stream+File log handlers and local config file.')

  # configure root logger
  frmttr = logging.Formatter(LOG_FORMAT)
  logger = logging.getLogger() # root logger 
  logger.setLevel('DEBUG')

  # add console handler
  ch = logging.StreamHandler()
  ch.setFormatter(frmttr)
  logger.addHandler(ch)

  # add file handler
  log_file = 'logs/get_user_media.log'
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
  conf_file = "ig/conf/get_user_media.yaml"
  return (logger, conf_file)


### If used as module: set Stream log handler and packaged config file
def config_fetcher_as_module():
  print('Setting Stream log handler and packaged config file')

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
  resource_path = '/'.join(('conf', 'get_user_media.yaml'))
  conf_file = pkg_resources.resource_filename(resource_package, resource_path)
  return (logger, conf_file)


### Entrypoint

if __name__ == '__main__':
  # Program used as script: run immediately
  fetcher = UserMediaFetcher()
  fetcher.process_all(sys.argv[1:])
else:
  # Program used as import: set flag
  is_imported = True

     
