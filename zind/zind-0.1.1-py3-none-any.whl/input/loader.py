import sys
import logging
from zind.api.file_filter_token import FilterToken
from zind.api.text_token import TextToken

class Loader:

  def __init__(self):
    self._file_filter_tokens = []
    self._text_tokens = []
    self._directory = "."

  def print_arg_error(self, bad_arg):
    print("Error: Unknown input argument: " + bad_arg)

  def print_help(self):
    print("Usage: [-g INCLUSIVE_MATCH ] ")
    print("       [-ge EXCLUSIVE_MATCH ] ")
    print("       [-d directory ] ")

  def run(self):

    # Setup logging
    logging.basicConfig()
    logging.getLogger().setLevel(logging.WARN)

    input_file_key = None
    input_text_key = None
    input_directory = False
    index = 1
    for index in range(1, len(sys.argv)):
      arg = sys.argv[index]

      if(input_file_key != None):
        parsed = self._load_file_filter_token(input_file_key, arg)
        if(not parsed):
          self.print_arg_error(sys.argv[index -1])
          self.print_help()
          return False
        else:
          input_file_key = None
      elif(input_text_key != None):
        parsed = self._load_text_token(input_text_key, arg)
        if(not parsed):
          self.print_arg_error(sys.argv[index -1])
          self.print_help()
          return False
        else:
          input_text_key = None
      elif(input_directory):
        self._directory = arg
        input_directory = False
      elif(arg.startswith('-g')):
        input_file_key = arg[2:]
      elif(arg.startswith('--g')):
        input_file_key = arg[3:]
      elif(arg.startswith('-t')):
        input_text_key = arg[2:]
      elif(arg.startswith('--t')):
        input_text_key = arg[3:]
      elif(arg == '-h' or arg == '--help'):
        self.print_help()
        return False
      # Must check '-vv' before '-v'
      elif(arg.startswith('-vv')):
        logging.getLogger().setLevel(logging.DEBUG)
      elif(arg.startswith('-v')):
        logging.getLogger().setLevel(logging.INFO)
      elif(arg.startswith('-d')):
        input_directory = True
      else:
        self.print_arg_error(arg)
        self.print_help()
        return False
      
    if(input_file_key is not None):
      print("Error: match token must follow expression '" + sys.argv[index] + "'")
      self.print_help()
      return False

    return True
    
  def _load_file_filter_token(self, input_file_key, token):
    input_chars = [char for char in input_file_key]

    inclusive = True
    regex = False
    filename_only = False

    for char in input_chars:
      if(char == "e"):
        inclusive = False
      elif(char == "r"):
        regex = True
      elif(char == "f"):
        filename_only = True
      else:
        return False

    filter_token = FilterToken(token, inclusive, regex, filename_only)
    self._file_filter_tokens.append(filter_token)
    return True

  def _load_text_token(self, input_text_key, token):
    input_chars = [char for char in input_text_key]

    inclusive = True
    regex = False
    case_sensitive = False

    for char in input_chars:
      if(char == "e"):
        inclusive = False
      elif(char == "r"):
        regex = True
      elif(char == "c"):
        case_sensitive = True
      else:
        return False

    text_token = TextToken(token, inclusive, regex, case_sensitive)
    self._text_tokens.append(text_token)
    return True

  def get_file_filter_tokens(self):
    return self._file_filter_tokens

  def get_text_tokens(self):
    return self._text_tokens

  def get_directory(self):
    return self._directory
