from datetime import datetime

class LogWriter():
    def __init__(self, filepath, encoding):
        self.filepath = filepath
        self.encoding = encoding
        self.create_logfile()

    def create_logfile(self):
        with open(self.filepath, "x", encoding=self.encoding) as f:
            f.write("")
    
    def append(self, string):
        with open(self.filepath, "a", encoding=self.encoding) as f:
            f.write("[%s] %s\n" % (datetime.now().strftime("%Y/%m/%d %H:%M:%S"), string))

def get_datetime_now():
  return datetime.now().strftime("%Y/%m/%d %H:%M:%S")

def log(string):
    print("[log] - %s\n%s\n" % (get_datetime_now(), string))

def info(string):
    print("[info] - %s\n%s\n" % (get_datetime_now(), string))

def begin(string):
    print("[begin] - %s\n%s\n" % (get_datetime_now(), string))

def end():
    print("[end] - %s\n" % get_datetime_now())

def error(string):
    print("[error] - %s\n%s\n" % (get_datetime_now(), string))

def warning(string):
    print("[warning] - %s\n%s\n" % (get_datetime_now(), string))

def success(string):
    print("[success] - %s\n%s\n" % (get_datetime_now(), string))
