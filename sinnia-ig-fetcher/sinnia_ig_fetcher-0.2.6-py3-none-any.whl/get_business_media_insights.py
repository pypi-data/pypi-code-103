import sys, os, requests, logging
import pymysql
from datetime           import time, timedelta, datetime, tzinfo, date
from ig.instagram_utils import InstagramUtils
#from alerts_pb2 import InternalAlert

#https://developers.facebook.com/docs/instagram-api/reference/media/insights

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='logs/get_business_media_insights.log', level=logging.DEBUG, format=LOG_FORMAT)

class BusinessMediaInsightsFetcher:

  DF = "%Y-%m-%d"

  def __init__(self):
    self.utils = InstagramUtils()
    self.logger = logging.getLogger()
    self.logger.setLevel(logging.DEBUG)


  def process_all(self, args):
    exec_start_time = datetime.now()
    try:    
      if args == None or len(args) == 0:
        self.logger.debug("Initializing with defaults")
        conf_file = "ig/conf/get_business_media_insights.yaml"
        self.utils.init(conf_file, True)
      elif len(args) == 1:
        self.logger.debug("Initializing with params")
        conf_file = args[0]
        self.utils.init(conf_file, True)
      else:
        self.logger.exception('Error executing script: incorrect parameters. \
        Provide either no arguments, or [config_file]')
        return None
      self.logger.debug("Set conf_file '%s'" % (conf_file))

      conn = self.utils.get_conn('ig')
      media = self.get_media(conn)
      for item in media:
        user_id = item[0]
        media_id = item[1]
        media_type = item[2]
        media_story = item[3]
        access_token = item[4]
        self.process_business_media_insights(conn, user_id, media_id, media_type, access_token)
        if media_story == 1:
          self.process_business_media_insights(conn, user_id, media_id, 'story', access_token)
      conn.close()
    except:
      self.logger.exception('Error executing script')
    finally:
      self.logger.info('Total time: %s' % (datetime.now() - exec_start_time))

    
  def get_path(self, media_type):
    return {
        'image':          'request_image_path',
        'video':          'request_video_path',
        'carousel':       'request_carousel_album_path',
        'carousel_album': 'request_carousel_album_path',
        'story':          'request_story_path',
    }.get(media_type,'')


  def request_data(self, request_path, media_id, access_token):
    host = self.utils.from_config('graph_api.host')
    path = self.utils.from_config('graph_api.%s' % request_path).format(**locals())
    url = '%s%s'%(host,path)
    payload = {'access_token': access_token}
    if self.utils.has_trace_enabled():
      self.logger.debug('Url: %s' % url)
    response = requests.get('%s%s'%(host,path), params=payload)
    response_as_json = self.utils.response_as_json(response)
    return response_as_json 


  def get_media(self, conn):
    media = list()
    try:
      query = self.utils.from_config("queries.get_media")
      if self.utils.has_trace_enabled():
        self.logger.debug("query: %s" % query)
      cursor = conn.cursor(pymysql.cursors.SSCursor)
      cursor.execute(query)
      users = list()
      while (1):
        row = cursor.fetchone()
        if not row:
            break
        user_id = row[0].decode('UTF-8')
        media_id = row[1].decode('UTF-8')
        media_type = row[2].decode('UTF-8')
        media_story = row[3]
        access_token = row[4].decode('UTF-8')
        media.append((user_id, media_id, media_type, media_story, access_token))
      cursor.close()
      self.logger.debug("Added %s media "%(len(media)))
    except:
      cursor.close()
      self.logger.exception("Error while getting media")
    return media


  def parse_and_insert(self, conn, user_id, media_id, metrics):  
    cursor = conn.cursor()  
    common_fields = {"user_id":  user_id,
                     "media_id": media_id,
                     "end_time": date.strftime(date.today()-timedelta(days=1),self.DF),
                     "date":         str(datetime.now().isoformat(' ')),
                     "fetched_time": str(datetime.utcnow())}
    for item in metrics:
      metric_name = item.get("name")
      metric_value = item.get("values")[0].get("value") 
      fields = {"metric_name": metric_name,
                "metric_value": metric_value}
      fields.update(common_fields)
      self.logger.debug("insert with fields: %s" % str(fields))
      command = self.utils.from_config('queries.insert_insights').format(**fields)
      if self.utils.has_trace_enabled():
          self.logger.debug("insert command: %s" % command)
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


  def process_business_media_insights(self, conn, user_id, media_id, media_type, access_token):
    path = self.get_path(media_type)
    if path == '':
      self.logger.debug('media type unrecognised for %s: %s'%(media_id,media_type))
      return
    response = self.request_data(path, media_id, access_token)
    if response:
      try:
          self.parse_and_insert(conn, user_id, media_id, response.get('data'))
      except:
          self.logger.exception("Error while parsing or inserting")
    
  
if __name__ == '__main__':
  fetcher = BusinessMediaInsightsFetcher()
  fetcher.process_all(sys.argv[1:])
