import sys, os, logging, requests, copy
import pymysql
import time
from datetime import timedelta, datetime, tzinfo, date

from shared.utils import Utils
from alerts_pb2 import InternalAlert

utils = Utils()

# Sinnia Performance Test
APP_ACCESS_TOKEN = '278531633073506|GjrBzRFhujSFBnKQweki8Wn7seE'

# Sinnia Performance
#APP_ACCESS_TOKEN = '688606308143567|_pWzZxB2K5ZbTNJm74aAQJM2aoA'

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
logging.basicConfig(filename='logs/validate_tokens.log', level = logging.DEBUG, format = LOG_FORMAT)
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
logging.getLogger('urllib3').setLevel('WARNING')
logging.getLogger('shared').setLevel('INFO')


def request_status(check_token):
  host = utils.from_config('graph_api.host')
  path = utils.from_config('graph_api.debug_path').format(**locals())
  url = '%s%s'%(host,path)
  payload = {'access_token': APP_ACCESS_TOKEN}
  if utils.has_trace_enabled():
      logger.debug('Url: %s' % url)
  response = requests.get('%s'%(url), params=payload)
  response_as_json = utils.response_as_json(response)
  logger.debug('Response: %s' % response_as_json)
  return response_as_json 


# def request_info(id, access_token):
#   host = utils.from_config('graph_api.host')
#   path = utils.from_config('graph_api.info_path').format(**locals())
#   url = '%s%s'%(host,path)
#   payload = {'access_token': access_token}
#   if utils.has_trace_enabled():
#       logger.debug('Url: %s' % url)
#   response = requests.get('%s'%(url), params=payload)
#   response_as_json = utils.response_as_json(response)
#   logger.debug('Response: %s' % response_as_json)
#   return response_as_json 


def get_pages(conn):
  pages = list()
  try:
    query = utils.from_config("queries.get_users")
    cursor = conn.cursor(pymysql.cursors.SSCursor)
    cursor.execute(query)
    while (1):
      row = cursor.fetchone()
      if not row:
        break
      facebook_id = row[0].decode('UTF-8')
      instagram_id = row[1].decode('UTF-8')
      access_token = row[2].decode('UTF-8')
      data_access_until = row[3]
      alias = row[4].decode('UTF-8')
      pages.append((facebook_id, instagram_id, access_token, data_access_until, alias))
      logger.debug("Adding ids %s||%s"%(facebook_id,instagram_id))
    cursor.close()
    logger.debug("Added %s pages "%(len(pages)))
  except:
      logger.exception("Error while getting token")
  return pages


def validate(access_token, page_id, name, data, prev_expiration):
    is_valid = data.get("is_valid")         # true
    if (is_valid == False):
        if (data.get('error')):
            alert_title = "IG Token invalid"
            alert_contents = "Id %s: " % page_id + data.get('error').get('message') 
        else: 
            alert_title = "IG Token invalid"
            alert_contents = "Id %s: " % page_id + data.get('message')
        logger.debug(alert_contents)
        send_alert(alert_contents, alert_title, "SEVERE")
        return
    app_id = data.get("app_id")             # "688606308143567"
    application = data.get("application")   # "Sinnia Performance"    
    token_type = data.get("type")           # "PAGE"
    issued_at = data.get("issued_at")       # 1565287366
    expires_at = data.get("expires_at")*1000# 0
    prev_expiration_millis = prev_expiration.timestamp()*1000
    new_expiration_millis = data.get("data_access_expires_at")*1000 #1577319222
    if (new_expiration_millis > prev_expiration_millis):
      logger.debug("IG Token for id %s is being updated from %s to %s"%(page_id,prev_expiration_millis, new_expiration_millis))
      update_validity(page_id, new_expiration_millis)
    scopes = data.get("scopes")             # "instagram_basic","instagram_manage_insights"
    app_scoped_user_id = data.get("user_id")# "123187318618206"
    #name = ""
    #profile = data.get("profile_id")        # "267181177213742"
    #user_id = data.get("user_id")           # "267181177213742"
    #if (profile) :
    #    logger.debug("profile is a Page")
    #    name = request_info(profile, access_token).get("name")
    #else:
    #    logger.debug("profile is a User")
    #    name = request_info(user_id, APP_ACCESS_TOKEN).get("name")    

    if (new_expiration_millis != 0):
        days = 86400000 * 2 # two days in milliseconds
        now_millis = int(round(time.time() * 1000))
        if (new_expiration_millis > now_millis
            and new_expiration_millis - now_millis > days):
            logger.debug("IG Token for '%s' (ID %s) will lose data access on %s. No notification needed." % (name, page_id,datetime.fromtimestamp(new_expiration_millis/1000.0)))
        elif (new_expiration_millis > now_millis
              and new_expiration_millis - now_millis <= days):
            alert_title = "IG data access will expire soon"
            alert_contents = "IG Token for '%s' (ID %s) will lose data access on %s. Please reauthenticate at https://instagram.sinniaws.com" % (name, page_id,datetime.fromtimestamp(new_expiration_millis/1000.0))
            logger.debug(alert_contents)
            send_alert(alert_contents, alert_title, "WARN")
        elif (new_expiration_millis <= now_millis):
            alert_title = "IG data access has expired"
            alert_contents = "IG Token for '%s' (ID %s) no longer has data access. Please reauthenticate at https://instagram.sinniaws.com or deactivate." % (name, page_id)
            logger.debug(alert_contents)
            send_alert(alert_contents, alert_title, "SEVERE")
        else:
            logger.debug("IG Token for id %s is still valid"%(page_id))
    else:
        logger.debug("IG Token for id %s will never expire"%(page_id))


def update_validity(id, until):
  conn = utils.get_conn('ig')
  cursor = conn.cursor()  
  until_date = datetime.fromtimestamp(until/1000.0)
  fields = {"data_access_until": until_date,
            "instagram_id": id}
  command = utils.from_config('queries.update_validity').format(**fields)
  logger.debug("updating: %s"%command)
  cursor.execute(command)
  conn.commit()
  cursor.close()

  
def send_alert(alert_contents, alert_title, alert_priority):
  alert = InternalAlert()
  alert.priority = alert_priority    # {INFO, WARN, SEVERE}
  alert.type = "IG_VALIDATE_TOKENS"
  alert.project = alert_title
  alert.text = alert_contents
  alert.created_at = int((datetime.utcnow()-datetime(1970,1,1)).total_seconds())*1000
  body = alert.SerializeToString()
  url='http://trb-message-exchange-hrd.appspot.com/alert/internal'
  logger.debug('alert url: %s' % url)
  logging.debug('alert body: %s...' % body[:250])
  r = requests.post(url, body)

  
def main(args):  
  conf_file = "ig/conf/validate_tokens.yaml"
  utils.init(conf_file, True)
  exec_start_time = datetime.now()
  try:
    conn = utils.get_conn('ig')
    pages = get_pages(conn)
    for item in pages:
      facebook_id = item[0]
      instagram_id = item[1]
      access_token = item[2]
      prev_expiration = item[3]
      name = item[4]
      page_id = "%s || %s || %s" % (facebook_id, instagram_id, name)
      logger.info("##############################################")
      logger.info("Validating %s" % page_id)
      response = request_status(access_token)
      if response:
        try:
          if (response.get('error')):
              logger.error("Error while validating id %s: %s" % (page_id, response.get('error').get('message')))
              return
          validate(access_token, instagram_id, name, response.get('data'), prev_expiration)
        except:
          logger.exception("Error while parsing or alerting")
      else:
          logger.error("Error while validating id %s (maybe app mismatch)" % (page_id))
  except:
    logger.exception('Error executing script')
  finally:
    logger.info('Total time: %s' % (datetime.now() - exec_start_time))

    
if __name__ == '__main__':
     main(sys.argv[1:])

     
