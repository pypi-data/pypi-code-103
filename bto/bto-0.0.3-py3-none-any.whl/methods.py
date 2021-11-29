from rich.console import Console
from rich.table import Table
import math


def convert_size(size_bytes):
  if size_bytes == 0:
      return "0B"
  size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
  i = int(math.floor(math.log(size_bytes, 1024)))
  p = math.pow(1024, i)
  s = round(size_bytes / p, 2)
  return "%s %s" % (s, size_name[i])


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