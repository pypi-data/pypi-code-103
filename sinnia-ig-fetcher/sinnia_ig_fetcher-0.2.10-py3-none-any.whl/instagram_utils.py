import sys, os, logging, requests, copy
import pymysql
import re
import string
import traceback
from datetime     import time, timedelta, datetime, tzinfo, date
from shared.utils import Utils

DF      = "%Y-%m-%d"
FULL_DF = "%Y-%m-%d %H:%M:%S"

class InstagramUtils(Utils):

  def init(self, conf_file_path, trace_enabled = False):
      Utils.init(self, conf_file_path, trace_enabled)
      self.logger = logging.getLogger(__name__)
      print('InstagramUtils inited logger')
      print(self.logger)

  # def old_init(self, conf_file_path, trace_enabled = False):
  #     Utils.init(self, conf_file_path, trace_enabled)
  #     log_name = self.conf.get("log_name", "root")
  #     print('InstagramUtils init log_name')
  #     print(log_name)
  #     self.logger = Utils.init_logger(self) # logging.getLogger(log_name)
  #     print('InstagramUtils init logger')
  #     print(self.logger)

  # def get_logger(self):
  #     print('InstagramUtils get_logger logger')
  #     print(self.logger)
  #     self.logger.debug('InstagramUtils get_logger logger debug')
  #     return self.logger
    
  def request_data(self, url, access_token):
      payload = {'access_token': access_token}
      if Utils.has_trace_enabled(self):
          self.logger.debug('Url: %s' % url)
      response = requests.get(url, params=payload)
      response_as_json = Utils.response_as_json(self, response)
      return response_as_json 

  ### Parse from source date format to target date format
  def parse_time(self, source_df, target_df, value_str):
    value_datetime = datetime.strptime(value_str[:19], source_df)
    return datetime.strftime(value_datetime, target_df)

  def get_date(self, arg = None):
    if arg == None:
      return self.get_yesterday()
    else:
      try:
        return datetime.strptime(arg, DF).date()
      except:
        try: 
          return datetime.strptime(arg, FULL_DF).date()
        except Exception as e:
          self.logger.exception("Error obtaining date")  
          self.logger.exception(traceback.format_exc())  
          return self.get_yesterday()

  def get_yesterday(self):
    return date.today() - timedelta(days = 1)

  def get_last_week(self):
    return date.today() - timedelta(days = 7)
    
  def get_start_end_delta_str(self, delta):
    date_from, date_to = self.get_start_end_delta_dates(delta)
    return (datetime.strftime(date_from, DF), datetime.strftime(date_to, DF))

  def get_start_end_str(self, str1, str2):
    date_from, date_to = self.get_start_end_dates(str1, str2)
    return (datetime.strftime(date_from, DF), datetime.strftime(date_to, DF))
          
  def get_start_end_delta_dates(self, delta):
    date_from = None
    date_to = None
    try:
      date_to = date.today()
      date_from = date_to - timedelta(days = delta)
      return (date_from, date_to)
    except Exception as e:
      self.logger.exception("Error obtaining start/end delta dates")  
      self.logger.exception(traceback.format_exc())  
      raise e

  def get_start_end_dates(self, str1, str2):
    date_from = None
    date_to = None
    try:
      date_from = datetime.strptime(str1, DF)
      date_to = datetime.strptime(str2, DF)
      if date_from > date_to:
        self.logger.exception("Error: date_from after date_to")
      return (date_from, date_to)
    except Exception as e:
      self.logger.exception("Error obtaining start/end dates") 
      self.logger.exception(traceback.format_exc())  
      raise e

