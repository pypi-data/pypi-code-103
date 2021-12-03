class ProgressBar(object):

 def __init__(self, title,

count=0.0,

run_status=None,

fin_status=None,

total=100.0,

unit='', sep='/',

chunk_size=1.0):

  try:
   super(ProgressBar, self).__init__()
  except:pass

  self.info = "【%s】%s %.2f %s %s %.2f %s"

  self.title = title

  self.total = total

  self.count = count

  self.chunk_size = chunk_size

  self.status = run_status or ""

  self.fin_status = fin_status or " " * len(self.status)

  self.unit = unit

  self.seq = sep
 import time
 def __get_info(self):

# 【名称】状态 进度 单位 分割线 总数 单位

  _info = self.info % (self.title,       self.status,

  self.count/self.chunk_size, self.unit, self.seq, self.total/self.chunk_size, self.unit)

  return _info

 def refresh(self, count=1, status=None):

  self.count += count

  # if status is not None:

  self.status = status or self.status

  end_str = "\r"

  if self.count >= self.total:

   end_str = '\n'

   self.status = status or self.fin_status

  try:
    print (self.__get_info(),  end=end_str);"""
————————————————
版权声明：本文为CSDN博主「张衍军」的原创文章，遵循CC 4.0 BY-SA版权协议，转载请附上原文出处链接及本声明。
原文链接：https://blog.csdn.net/weixin_31312621/article/details/113967526"""
  except:pass
if __name__=="__main__":
  class Self(object):
    def file_name(self):
      return ''
    def __init__(self):
      #__getattribute__()
      self.file_name()
  self=Self()
  content_size=100
  chunk_size=50
  x=ProgressBar(self.file_name(), total=content_size,

unit="KB", chunk_size=chunk_size, run_status="正在下载", fin_status="下载完成")
  for i in range(11):
    progress=x
    progress.refresh(count=i)
    print ("\n")
    ProgressBar.time.sleep(1)