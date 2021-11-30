from zind.api.core_find import Find
from zind.api.core_text_find import TextFind
from zind.input.loader import Loader
import logging

class Runner:

  def __init__(self):
    pass;

  def run(self):

    loader = Loader()
    continue_run = loader.run()
    if(not continue_run):
      return

    file_filter_tokens = loader.get_file_filter_tokens()
    for file_filter_token in file_filter_tokens:
      logging.debug("File filter token: " + str(file_filter_token))
      

    find = Find()
    text_find = TextFind()

    scan_directory = loader.get_directory()
    file_matches = find.find(scan_directory, file_filter_tokens)

    for file_match in file_matches:
      if(len(loader.get_text_tokens()) == 0):
        print(file_match)
      elif(not file_match.endswith('/')):
        lines = text_find.scan(file_match, loader.get_text_tokens())
        for line in lines:
          print(file_match + ": " + line.rstrip())

def main():
  runner = Runner()
  runner.run()
