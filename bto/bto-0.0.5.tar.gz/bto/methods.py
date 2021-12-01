from rich.console import Console
from rich.table import Table
import math
import os
import time
import platform
import psutil
import socket 
from getmac import get_mac_address as mac  

 

def banner():
  print('''
██████╗ ████████╗ ██████╗ 
██╔══██╗╚══██╔══╝██╔═══██╗
██████╔╝   ██║   ██║   ██║
██╔══██╗   ██║   ██║   ██║
██████╔╝   ██║   ╚██████╔╝
╚═════╝    ╚═╝    ╚═════╝ 

[ multi-purpose sys tool ]
''')


# ============================================

def get_ip():
  hostname = socket.gethostname()   
  IPAddr = socket.gethostbyname(hostname)  

  table = Table(title='IP Address')

  table.add_column("Host name")
  table.add_column("IP")
 
  table.add_row(hostname, IPAddr) 

  Console().print(table)


# ============================================

def get_mac():
  hostname = socket.gethostname()   

  table = Table(title='Mac Address')

  table.add_column("Host name")
  table.add_column("MAC")
 
  table.add_row(hostname, mac()) 

  Console().print(table)

# ============================================

def sysinfo():
  
  
  uname = platform.uname()
  ram = psutil.virtual_memory()
  
  table = Table(title='System Information')

  
  table.add_column("Details")
  table.add_column("Data")
  
  table.add_row('OS', str(uname.system))
  table.add_row('System name', str(uname.node))
  table.add_row('Machine type', str(uname.machine))
  table.add_row("Release", str(uname.release))
  table.add_row('Processor', str(platform.processor()))
  table.add_row('Architecture', str(platform.architecture()))
  table.add_row('Kernel', str(platform.platform()))
  table.add_row('Version', str(uname.version))
  table.add_row()
  table.add_row("Total RAM", str(convert_size(ram.total)))
  table.add_row("Available RAM", str(convert_size(ram.available)))
  
  console = Console()
  console.print(table)
  
  
# ============================================

def file_info(filename):
  
  stats = os.stat(filename)

  table = Table(title=filename)

  table.add_column("Details")
  table.add_column("Data")

  table.add_row("Access date", time.ctime(stats.st_atime))
  table.add_row("Last modified date", time.ctime(stats.st_mtime))
  table.add_row("Creation date", time.ctime(stats.st_ctime))
  table.add_row()
  table.add_row("Size", str(convert_size(stats.st_size)))
  table.add_row("Owner id", str(stats.st_uid))
  table.add_row("Group id", str(stats.st_gid))
  table.add_row()
  table.add_row("Type and permissions", str(stats.st_mode))
  table.add_row("Inode number", str(stats.st_ino))
  table.add_row("Device id", str(stats.st_dev))
  table.add_row("No. of hard links", str(stats.st_nlink))

  console = Console()
  console.print(table)



# ============================================
  

def convert_size(size_bytes):
  if size_bytes == 0:
      return "0B"
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size_bytes, 1024)))
  p = math.pow(1024, i)
  s = round(size_bytes / p, 2)
  return "%s %s" % (s, size_name[i])


# ============================================


def datatypes():
  table = Table(title="Tabular Representation of various Memory Sizes")

  table.add_column("Name", style="cyan", no_wrap=True)
  table.add_column("Equal To", style="magenta")
  table.add_column("Size(in bytes)", style="green")
  table.add_column("Shorthand", style="yellow")

  table.add_row('Bit',	'1 Bit',	'0.125', 'b')
  table.add_row('Byte',	'8 Bits',	'1', 'B')
  table.add_row('Kilobyte',	'1024 B',	'1024', 'KB')
  table.add_row('Megabyte',	'1024 KB',	'1048576', 'MB')
  table.add_row('Gigabyte',	'1024 MB',	'1073741824', 'GB')
  table.add_row('Terrabyte',	'1024 GB',	'1099511627776', 'TB')
  table.add_row('Petabyte',	'1024 TB',	'1125899906842624', 'PB')
  table.add_row('Exabyte',	'1024 PB',	'1152921504606846976', 'EB')
  table.add_row('Zettabyte',	'1024 EB',	'1180591620717411303424', 'ZB')
  table.add_row('Yottabyte',	'1024 ZB',	'1208925819614629174706176', 'YB')
  
  console = Console()
  console.print(table)