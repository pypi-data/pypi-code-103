import datetime
import dateutil.relativedelta

def find_today():
  today = datetime.datetime.now()
  return today

def find_last_month(inital_period):
  final_period = inital_period - dateutil.relativedelta.relativedelta(months=1)
  return final_period

def find_last_period(initial_period):
  year = int(initial_period.split('/')[1])
  month = int(initial_period.split('/')[0])
  period = datetime.datetime(year, month, 1)
  last_period = period - dateutil.relativedelta.relativedelta(months=1)
  return last_period
