import sys, os, requests, logging
import pymysql
import pkg_resources 
from datetime           import time, timedelta, datetime, tzinfo, date
from ig.instagram_utils import InstagramUtils

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
is_imported = None

class BusinessMediaFetcher:

  SOURCE_DF = "%Y-%m-%dT%H:%M:%S"
  TARGET_DF = "%Y-%m-%d %H:%M:%S"

  ### Build BusinessMediaFetcher according to how it's being used
  def __init__(self, args = None):
    try:    
      if is_imported:
        print('BusinessMediaFetcher init as module')
        logger, conf_file = config_fetcher_as_module()
        self.logger = logger
        self.utils = InstagramUtils()
        self.utils.init(conf_file, True)
      else:
        print('BusinessMediaFetcher init as main')
        logger = config_fetcher_as_main()
        self.logger = logger
        if args == None or len(args) == 0:
          self.logger.debug("Initializing with defaults")
          conf_file = "ig/conf/get_business_media.yaml"
          self.utils = InstagramUtils()
          self.utils.init(conf_file, True) 
          self.date_limit = self.utils.get_yesterday()
        elif len(args) == 2:
          self.logger.debug("Initializing with params")
          conf_file = args[0]
          self.utils = InstagramUtils()
          self.utils.init(conf_file, True)
          self.date_limit = self.utils.get_date(args[1])
        else:
          msg = 'Error executing script: incorrect parameters. \
          Provide either no arguments, or [config_file, date_limit]'
          self.logger.exception(msg)
          raise Exception(msg)
        self.logger.debug("Set date_limit '%s', conf_file '%s'" %   (self.date_limit, conf_file))
    except Exception as e:
      self.logger.exception('Error initializing BusinessMediaFetcher')
      raise e
      

  ### Utility to build fetching url
  def build_url(self, type, id, access_token, date_limit=None):
    host = self.utils.from_config('graph_api.host')
    path = self.utils.from_config('graph_api.request_%s_path'%type).format(**locals())
    historic = ''
    if (date_limit != None): 
      historic = self.utils.from_config('graph_api.historic_suffix').format(**locals())
    url = '%s%s%s'%(host,path,historic)
    payload = {'access_token': access_token}
    if self.utils.has_trace_enabled():
      self.logger.debug('Url: %s' % url)   
    return url

  
  ### Process all users from database
  def process_all(self):
    try:
      exec_start_time = datetime.now()
      conn = self.utils.get_conn('ig')
      users = self.get_users(conn)
      for item in users:
        user_id = item[0]
        access_token = item[1]
        self.process_business_media(conn,user_id,access_token,self.date_limit)
      conn.close()
    except:
      self.logger.exception("Error while preparing to process all")
    finally:
      self.logger.info('Total time: %s' % (datetime.now() - exec_start_time))


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
        access_token = row[1].decode('UTF-8')
        users.append((user_id, access_token))
        self.logger.debug("Adding user_id %s"%(user_id))
      cursor.close()
      self.logger.debug("Added %s users "%(len(users)))
    except:
      self.logger.exception("Error while getting users")
    return users

  
  ### Parse from source date format to target date format
#  def parse_time(self, value_str):
#    value_datetime = datetime.strptime(value_str[:19], self.SOURCE_DF)
#    return datetime.strftime(value_datetime, self.TARGET_DF)

  
  ### Parse and insert a page of media
  def parse_and_insert(self, conn, user_id, data, access_token, is_story=False):
    if len(data) == 0:
      return
    media_ids = []
    user_values = {"id": user_id, "username": data[0]["username"]}
    command = self.utils.from_config('queries.insert_empty_user').format(**user_values)
    cursor = conn.cursor() 
    cursor.execute(command)
    conn.commit()
    cursor.close()
    
    cursor = conn.cursor()
    min_date = None
    cursor.execute('SET character_set_connection=utf8mb4;')
    for item in data:
      created_at = self.utils.parse_time(self.SOURCE_DF, self.TARGET_DF, item["timestamp"])
      media_id = str(item["id"])
      media_ids.append(media_id)
      url_long = item.get("permalink", '')
      url = url_long if len(url_long)<=500 else url_long[:500]
      media_url_long = item.get("media_url", '')
      media_url = media_url_long if len(media_url_long)<=700 else media_url_long[:700]
      values = {"id" : media_id,
                "user_id": str(user_id),
                "created_at": str(created_at),
                "fetched_at": str(datetime.utcnow()),
                "type": str(item.get("media_type",'')),
                "caption": item.get("caption", '').replace("'",'"'),
                "url": str(url),
                "likes_count": item.get("like_count", 0),
                "comments_count": item.get("comments_count", 0),
                "image": str(media_url),
                "is_story": 1 if is_story else 0}
      min_date = self.utils.get_date(created_at)
      command = self.utils.from_config('queries.insert_media').format(**values)
      if self.utils.has_trace_enabled():
          self.logger.debug("insert_media values: %s" % values)
      cursor.execute(command)
    conn.commit()
    cursor.close()

    for media_id in media_ids:
      self.process_business_comments(conn, media_id, access_token)

    return min_date

  
  ### Parse and insert a page of comments
  def parse_and_insert_comments(self, conn, media_id, data):
    if len(data) == 0:
      return
    self.logger.debug("Parsing comments for %s" % media_id)
    
    cursor = conn.cursor()
    cursor.execute('SET character_set_connection=utf8mb4;')
    for item in data:
      created_at = self.utils.parse_time(self.SOURCE_DF, self.TARGET_DF, item["timestamp"])
      comment_id = str(item["id"])
      
      values = {"id" : comment_id,
                "media_id" : media_id,
                "parent_comment_id" : None,
                "username": item.get("username"), # No userid, only username
                "created_at": str(created_at),
                "fetched_at": str(datetime.utcnow()),
                "text": item.get("text", '').replace("'",'"'),
                "likes_count": item.get("like_count", 0)}
      command=self.utils.from_config('queries.insert_comments').format(**values)
      if self.utils.has_trace_enabled():
        # self.logger.debug("insert_comments command: %s" % command)
        self.logger.debug("insert_comments values: %s" % values)
      cursor.execute(command)
      conn.commit()

      replies = item.get('replies')
      if replies and replies.get('data'):
        self.logger.debug("Parsing comment replies for %s" % comment_id)  
        for reply in replies.get('data'):
          created_at = self.utils.parse_time(self.SOURCE_DF, self.TARGET_DF, reply["timestamp"])
          subcomment_id = str(reply["id"])
          values = {"id" : subcomment_id,
                    "media_id" : media_id,
                    "parent_comment_id" : comment_id, # Append parent comment id
                    "username":reply.get("username"), # No userid, only username
                    "created_at": str(created_at),
                    "fetched_at": str(datetime.utcnow()),
                    "text": reply.get("text", '').replace("'",'"'),
                    "likes_count": reply.get("like_count", 0)}
          command=self.utils.from_config('queries.insert_comments').format(**values)
          if self.utils.has_trace_enabled():
            #self.logger.debug("insert_comments_replies command: %s" % command)
            self.logger.debug("insert_comments_replies values: %s" % values)
          cursor.execute(command)
          conn.commit()
        
    cursor.close()
    return True

  
  def process_business_comments(self, conn, media_id, access_token):
    try:
        self.logger.info("##############################################")
        self.logger.info("Getting comments for %s" % media_id)  
        paginate = True
        url = self.build_url('comments', media_id, access_token)
        while paginate:
          response = self.utils.request_data(url, access_token)
          if response and response.get('data'):
            data = response.get('data')
            paging = response.get('paging')
            
            self.parse_and_insert_comments(conn, media_id, data)

            if paging:
              next_url = paging.get('next')
              self.logger.debug("comments pagination next_url=%s"%next_url)
              if next_url == None:
                self.logger.debug("comments pagination stopped")
                paginate = False
              url = next_url
            else:
              paginate = False
              
          else:
            paginate = False
    except:
        self.logger.exception("Error while parsing or inserting %s"%media_id)


  ### Main function
  def process_business_media(self, conn, user_id, access_token, date_limit = None):
    try:
        if date_limit is None:
          date_limit=self.utils.get_yesterday()
        self.logger.info("##############################################")
        self.logger.info("Getting media for %s until %s" % (user_id,str(date_limit)))
        paginate = True
        page_number = 1
        url = self.build_url('media',user_id,access_token,date_limit)
        has_data = False
        while paginate:
          response = self.utils.request_data(url, access_token)
          if response and response.get('data'):
            has_data = True
            data = response.get('data')
            next_url = response.get('paging').get('next')
            self.logger.debug("pagination next_url=%s"%next_url)
            min_date = self.parse_and_insert(conn, user_id, data, access_token)
            self.logger.debug("pagination min_date=%s"%min_date)
            if min_date < date_limit or next_url == None:
              self.logger.debug("pagination stopped: min_date=%s"%min_date)
              paginate = False
            url = next_url
            page_number += 1
          else:
            paginate = False
                  
        self.logger.info("##############################################")
        self.logger.info("Getting stories for %s" % user_id)
        url = self.build_url('stories',user_id,access_token)
        response = self.utils.request_data(url, access_token)
        if response and response.get('data'):
          has_data = True
          self.parse_and_insert(conn, user_id, response.get('data'), access_token, True)
        return has_data
    except:
        self.logger.exception("Error while parsing or inserting %s"%user_id)


  
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

        
        
### If used as main: set Stream+File log handlers and local config file
def config_fetcher_as_main():
  print('BusinessMediaFetcher setting Stream+File log handlers.')

  # configure root logger
  frmttr = logging.Formatter(LOG_FORMAT)
  logger = logging.getLogger() # root logger 
  logger.setLevel('DEBUG')

  # add console handler
  ch = logging.StreamHandler()
  ch.setFormatter(frmttr)
  logger.addHandler(ch)

  # add file handler
  log_file = 'logs/get_business_media.log'
  d = os.path.dirname(log_file)
  if not os.path.exists(d) and d != '':
    os.makedirs(d)
  fh = logging.FileHandler(log_file)
  fh.setFormatter(frmttr)
  logger.addHandler(fh)

  # configure other loggers
  logging.getLogger('urllib3').setLevel('WARNING')
  logging.getLogger('shared').setLevel('INFO')

  return (logger)  


### If used as module: set Stream log handler and packaged config file
def config_fetcher_as_module():
  print('BusinessMediaFetcher setting Stream log handler and packaged config file')

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
  resource_path = '/'.join(('conf', 'get_business_media.yaml'))
  conf_file = pkg_resources.resource_filename(resource_package, resource_path)
  return (logger, conf_file)


### Entrypoint

if __name__ == '__main__':
  # Program used as script: run immediately
  try:
    fetcher = BusinessMediaFetcher(sys.argv[1:])
    fetcher.process_all()
  except:
     print('Error initializing BusinessMediaFetcher')
else:
  # Program used as import: set flag
  is_imported = True
  


