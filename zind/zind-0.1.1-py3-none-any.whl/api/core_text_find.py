import os
import re

class TextFind:

  def __init__(self):
    pass

  # Read a file line by line and yield matching results.
  #
  # scan_file - A path to the file to process
  # text_tokens - A list of text_token objects which describe which lines to match on
  def scan(self, scan_file, text_tokens):

    # Organize the text tokens into a map based on inclusive or exclusive rules
    text_map = {}
    text_map["inclusive"] = []
    text_map["exclusive"] = []
    for text_token in text_tokens:
      if(text_token.is_inclusive()):
        text_map["inclusive"].append(text_token)
      else:
        text_map["exclusive"].append(text_token)

    try:
      with open(scan_file, "r") as input_fd:

        lines = input_fd.readlines()
        for line in lines:

          # First check for exclusions
          skip = False
          for text_token in text_map["exclusive"]:
            case_sensitive = text_token.is_case_sensitive()
            regex = text_token.is_regex()
            check_token = text_token.get_token()
            check_line = line
            if(not case_sensitive):
              check_line = line.lower()
              check_token = check_token.lower()

            if(not regex):
              if(check_token in check_line):
                skip = True
                break
            else:
              if(re.match(check_token, check_line)):
                skip = True
                break

          if(skip):
            continue

          # Next check all inclusions
          all_match = True
          for text_token in text_map["inclusive"]:
            case_sensitive = text_token.is_case_sensitive()
            regex = text_token.is_regex()
            check_token = text_token.get_token()
            check_line = line
            if(not case_sensitive):
              check_line = line.lower()
              check_token = check_token.lower()

            if(not regex):
              if(check_token not in check_line):
                all_match = False
                break
            else:
              if(not re.match(check_token, check_line)):
                all_match = False
                break

          if(all_match):
            yield line
    except UnicodeDecodeError:
      pass
