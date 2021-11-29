from termcolor import colored
import random
import sys
 

def main():

  # try-except blocks
  try:
    try:
      size_bytes = int(sys.argv[1])
    except ValueError:
      if (sys.argv[1] == 't'):
        datatypes()
      else:
        print(colored('[-] Wrong datatype entered !', 'red'))
      exit()

  except IndexError:
    try:
      size_bytes = int(input('[+] Bytes : '))
    except ValueError:
      if (sys.argv[1] == 't'):
        datatypes()
      else:
        print(colored('[-] Wrong datatype entered !', 'red'))
      exit()

  converted_size = convert_size(size_bytes)

  # Printing output
  color_list = [ 'magenta', 'green', 'white', 'blue' ]

  print(colored('[=] '+ str(converted_size), random.choice(color_list)))


main()