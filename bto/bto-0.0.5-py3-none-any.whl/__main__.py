import bto
from optparse import OptionParser
from termcolor import colored
import random
import sys
import os
 

def parser():

  usage = "usage: bto -b -t"
  parser = OptionParser(usage=usage)
  

  parser.add_option("-b", "--bytes",
                    type = 'int', metavar = "BYTES",
                    dest = "size_bytes",
                    help = "Converts bytes to suitable memory size")

  parser.add_option("-t", "--table",
                    action = "store_true", 
                    dest = "table", default = False,
                    help = "Tabular representation of various memory sizes")

  parser.add_option("-f", "--filesize",
                    dest = "filename", metavar = "FILENAME",
                    help = "Details of the file specified")

  parser.add_option("-s", "--sysinfo",
                    action = "store_true",
                    dest = "sys", default = False,
                    help = "System info, regardless OS (Win/Linux)")

  parser.add_option("-i", "--ip",
                    action = "store_true",
                    dest = "ip", default = False,
                    help = "Get your IP Address")

  parser.add_option("-m", "--mac",
                    action = "store_true",
                    dest = "mac", default = False,
                    help = "Get your MAC Address")
    
  
  return parser.parse_args()

# ============================================


def main():

  (options, args) = parser()

  banner_var = True

  if options.table:
    bto.datatypes()

    banner_var = False


  if (bool(options.size_bytes) == True):
    converted_size = bto.convert_size(int(options.size_bytes))
    color_list = [ 'magenta', 'green', 'white', 'blue' ]
    print(colored('[=] '+ str(converted_size), random.choice(color_list)))

    banner_var = False


  if (bool(options.filename) == True):
    if os.path.exists(options.filename):
      bto.file_info(options.filename)
    else:
      print('[-] File not found !!')

    banner_var = False


  if options.sys:
    bto.sysinfo()
    banner_var = False
  
  if options.ip:
    bto.get_ip()
    banner_var = False

  if options.mac:
    bto.get_mac()
    banner_var = False


  if banner_var:
    bto.banner()
  


# ============================================
if __name__ == '__main__':
  main()