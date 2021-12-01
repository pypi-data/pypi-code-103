import logging
from pytz import timezone
from datetime import datetime, timedelta

from ig.instagram_utils import InstagramUtils
from ig.get_user_media import UserMediaFetcher
from ig.get_business_media import BusinessMediaFetcher
from ig.get_business_competitors_media import CompetitorsMediaFetcher
from ig.get_hashtag_media import HashtagsMediaFetcher

# Sinnia Performance Test
APP_ID = '278531633073506'
APP_SECRET = 'f02bb02138bfc48faec13b1f4ce575ef'
APP_ACCESS_TOKEN = '278531633073506|GjrBzRFhujSFBnKQweki8Wn7seE'

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
frmttr = logging.Formatter(LOG_FORMAT)
logger = logging.getLogger()
logger.setLevel('DEBUG')
ch = logging.StreamHandler()
ch.setFormatter(frmttr)
ch.setLevel('DEBUG')
logger.addHandler(ch)
print('Controllers inited logger')
print(logger)

def getHashtagsData(hashtag, accessToken):
  utils = InstagramUtils()
  print('inited utils')
  utils.init("ig/conf/get_hashtag_media_ondemand.yaml", True)
  print('configged utils')
  conn = utils.get_conn("ig")
  print('got conn' + str(conn))
  fetcher = HashtagsMediaFetcher()
  hashtag_id = None
  data_found = fetcher.process_hashtag_media(conn, id, hashtag, hashtag_id, accessToken)
  logger.info("APPLOG getHashtagsData for %s: %s" % (str(id),str(data_found)))
  conn.commit()
  utils.close_conn("ig")

if __name__ == '__main__':
  # Program used as script: run immediately
  try:
    getHashtagsData('mowery', 'EAAD9UrMMTWIBAE2PdPLD9pktTmxCIfE5ZA32mghWlhXB0Vzv8gQmRJSmWLPJgrGZAoH9tQjnrqoeG1CcYtSfZAYckOITGeBLitS2LdcPYyqMeBbwlVNczzDsZAAKvEsvu1UXRIuwT8KrPTtVMoJKAU3DxTFwhjrQTVxY7HeEAghTt7x59SFG5MZBXRGOuu2kZD')
  except Exception as e:
    print('Error initializing HTtester')
    print(e)
  