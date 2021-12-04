import requests
import selenium
import bs4
import schoolopy
import random
import time

def schoology_api(key, secret, user_name):
  #Get your key and secret from https://app.schoology.com/api or <DOMAIN>.schoology.com/api
  sc = schoolopy.Schoology(schoolopy.Auth(key, secret))
  sc.limit = 10 
  consumer_key = key
  consumer_secret = secret
  auth  = 'OAuth realm="Schoology API",'
  auth += 'oauth_consumer_key="%s",' % consumer_key
  auth += 'oauth_token="%s",' % ('')
  auth += 'oauth_nonce="%s",' % ''.join([str(random.randint(0, 9)) for i in range(8)])
  auth += 'oauth_timestamp="%d",' % time.time()
  auth += 'oauth_signature_method="PLAINTEXT",'
  auth += 'oauth_version="1.0",'
  auth += 'oauth_signature="%s%%26%s"' % (consumer_secret, '')
  headers = {'Accept': 'application/json',
      'Host': 'api.schoology.com',
      'Content-Type': 'application/json',
      'Authorization': auth}
  data =requests.get(f'https://api.schoology.com/v1/search?keywords={user_name}&type=user&limit=5', headers=headers) 
  data.raise_for_status()
  data = data.json()

  if len(data) == 0:
    return {}

  data = data['users']['search_result'][0]
  school = data['school']
  uid = data["uid"]
  data = sc.get_user(uid)
  try:
    if data["gender"] == 'M':
      gender = "Male"
    else:
      gender = "Female"
  except:
    gender="Unknown"

  primary_email = data["primary_email"]
  try:
    username = data["username"]
  except:
    username = "Unknown"
  try:
    grad = data["grad_year"]
  except:
    grad = "Unknown"
  try:
    tz = data["tz_name"]
  except:
    tz = "Unknown"
  return data
  
