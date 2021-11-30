import os
import re

# Filter files according to inclusion and exclusion rules. These rules follow a pattern similar to multiple grep commands piped together.
# Inclusions and exclusions follow the commutative property. If there are multiple inclusions, each one must match to accept.
# A single matching exclusion means no match.
class Find:

  def __init__(self):
    pass

  def _check_match(self, matcher, matcher_filter_exclude_list, matcher_filter_include_list):

    for matcher_filter_token in matcher_filter_exclude_list:
      token = matcher_filter_token.get_token()
      is_regex = matcher_filter_token.is_regex()
      if(is_regex):
        if(re.match(token, matcher)):
          return False
      elif token in matcher:
        return False

    if(len(matcher_filter_include_list) == 0):
      return True

    for matcher_filter_token in matcher_filter_include_list:
      token = matcher_filter_token.get_token()
      is_regex = matcher_filter_token.is_regex()
      if(is_regex):
        if(not re.match(token, matcher)):
          return False
      elif token not in matcher:
        return False

    return True

  # Recursively walk through filesystem and either include/exclude files and directories based on user input
  #
  # scan_dir - A path to the directory to recursively walk through
  # file_filter_tokens - A list of file_filter_token objects which describe how to include/exclude files based on input patterns
  # only_files - Set true to only yield files and exclude all directories from output
  def find(self, scan_dir, file_filter_tokens, only_files=False):

    if(scan_dir.endswith("/")):
      scan_dir = scan_dir[:-1]

    # Organize the file filter tokens into a map based on file or directory matching and inclusive or exclusive rules
    filter_map = {}
    filter_map["path"] = {}
    filter_map["filename"] = {}
    for key in filter_map:
      filter_map[key]["inclusive"] = []
      filter_map[key]["exclusive"] = []
    for file_filter_token in file_filter_tokens:

      # All filter tokens, 'filename_only' and 'path' are added to the inclusive 'path' check
      if(file_filter_token.is_inclusive()):
        filter_map["path"]["inclusive"].append(file_filter_token)
      if(not file_filter_token.is_filename_only() and not file_filter_token.is_inclusive()):
        filter_map["path"]["exclusive"].append(file_filter_token)

      if(file_filter_token.is_filename_only()):
        if(file_filter_token.is_inclusive()):
          filter_map["filename"]["inclusive"].append(file_filter_token)
        else:
          filter_map["filename"]["exclusive"].append(file_filter_token)

    # Track which directories have already been visited to prevent infinite loops
    directory_map = {}

    # Note 'topdown' must be true if excluding directories when using the os.walk function
    for root, dirs, files in os.walk(scan_dir, topdown=True, followlinks=True):

      # Skip the first set of files if we are including specific directories
      for name in files:
        match = self._check_match(name, filter_map["filename"]["exclusive"], filter_map["filename"]["inclusive"])
        if(match):
          match = self._check_match(root + os.path.sep + name, filter_map["path"]["exclusive"], filter_map["path"]["inclusive"])
          if(match):
            yield root + os.path.sep + name

      keep_dirs = []
      for name in dirs:
        path = root + os.path.sep + name

        # Ensure the directory has not been visited before
        abs_dirpath = os.path.realpath(path)
        if(abs_dirpath in directory_map):
          continue
        else:
          directory_map[abs_dirpath] = None

        # First check exclusions only because further checking is not required if the directly is excluded.
        match = self._check_match(path, filter_map["path"]["exclusive"], [])
        if(match):
          keep_dirs.append(name)
          if(not only_files):
            # Next check inclusions only, and yield on a match
            match = self._check_match(path, [], filter_map["path"]["inclusive"])
            # Do not output any directories if matching inclusive filenames only
            if(match and len(filter_map["filename"]["inclusive"]) == 0):
              yield root + os.path.sep + name + "/"

      dirs.clear()
      for name in keep_dirs:
        dirs.append(name)
