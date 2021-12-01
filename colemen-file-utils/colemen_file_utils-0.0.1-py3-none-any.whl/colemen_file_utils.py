import dir as dir
import file as file
import hashlib
import os
import re
import os.path
import sys
import json
import shutil


# # def get_folders_from_dir(self, **kwargs):
# #     dirArray = []
# #     searchPath = os.getcwd()
# #     ignoreArray = False
# #     recursive = True

# #     if 'SEARCH_PATH' in kwargs:
# #         searchPath = kwargs['SEARCH_PATH']

# #     if 'RECURSIVE' in kwargs:
# #         if kwargs['RECURSIVE'] is False:
# #             recursive = False

# #     if 'IGNORE_ARRAY' in kwargs:
# #         if isinstance(kwargs['IGNORE_ARRAY'], list):
# #             ignoreArray = kwargs['IGNORE_ARRAY']
# #         else:
# #             self.log(f"Invalid ignore list provided [{type(kwargs['IGNORE_ARRAY'])}], must be of type list", COLOR="BLACK", BGCOLOR="YELLOW")

# #     # pylint: disable=unused-variable
# #     for root, folders, files in os.walk(searchPath):
# #         # print(folders)
# #         for d in folders:
# #             fd = {}
# #             fd['dir_name'] = d
# #             fd['file_path'] = os.path.join(root, d)
# #             ignore = False

# #             if ignoreArray is not False:
# #                 for x in ignoreArray:
# #                     if x in fd['file_path']:
# #                         ignore = True

# #             if ignore is False:
# #                 # fd['file_hash'] = generateFileHash(fd['file_path'])
# #                 dirArray.append(fd)

# #         if recursive is False:
# #             break
# #     return dirArray


# # def get_files_from_dir(self, **kwargs):
# #     fileArray = []
# #     searchPath = os.getcwd()
# #     ignoreArray = False
# #     extensionArray = False
# #     notRecursive = False
# #     if 'EXTENSIONS' in kwargs:
# #         if isinstance(kwargs['EXTENSIONS'], list):
# #             extensionArray = kwargs['EXTENSIONS']
# #         else:
# #             self.log(f"Invalid extension list provided [{type(kwargs['EXTENSIONS'])}], must be of type list", COLOR="BLACK", BGCOLOR="YELLOW")
# #     if 'SEARCH_PATH' in kwargs:
# #         searchPath = kwargs['SEARCH_PATH']
# #     if 'NOT_RECURSIVE' in kwargs:
# #         notRecursive = True
# #     if 'IGNORE_ARRAY' in kwargs:
# #         if isinstance(kwargs['IGNORE_ARRAY'], list):
# #             ignoreArray = kwargs['IGNORE_ARRAY']
# #         else:
# #             self.log(f"Invalid ignore list provided [{type(kwargs['IGNORE_ARRAY'])}], must be of type list", COLOR="BLACK", BGCOLOR="YELLOW")

# #     # pylint: disable=unused-variable
# #     for root, folders, files in os.walk(searchPath):
# #         # print(folders)
# #         for file in files:
# #             fd = {}
# #             ext = os.path.splitext(file)
# #             fd['file_name'] = ext[0]
# #             fd['extension'] = ext[1]
# #             fd['file_path'] = os.path.join(root, file)
# #             ignore = False

# #             if extensionArray is not False:
# #                 if fd['extension'] not in extensionArray:
# #                     ignore = True

# #             if ignoreArray is not False:
# #                 for x in ignoreArray:
# #                     if x in fd['file_path']:
# #                         ignore = True

# #             if ignore is False:
# #                 # fd['file_hash'] = generateFileHash(fd['file_path'])
# #                 fileArray.append(fd)

# #         if notRecursive is True:
# #             break
# #     return fileArray


# # def import_project_settings(file_name):
# #     settings_path = file_name
# #     if if_file_exists(settings_path) is False:
# #         settings_path = find_file_by_name(file_name, os.getcwd())
# #         if settings_path is False:
# #             return False
# #     # self.data['settings_file_path'] = settings_path
# #     # print(f"settings_path: {settings_path}")
# #     return read_json_file(settings_path)
# #     # self.settings["cwd"] = os.getcwd()


# # def mirror_test_dir(src, des, **kwargs):
# #     # onerror = None
# #     emptyFiles = True
# #     emptyFileSize = 0
# #     # if EMPTY_FILES is True, it creates a duplicate file with no content.
# #     if 'EMPTY_FILES' in kwargs:
# #         emptyFiles = kwargs['EMPTY_FILES']

# #     if 'EMPTY_FILE_SIZE' in kwargs:
# #         emptyFileSize = kwargs['EMPTY_FILE_SIZE']

# #     src = os.path.abspath(src)
# #     src_prefix = len(src) + len(os.path.sep)
# #     if if_dir_exists(des) is False:
# #         os.makedirs(des)
# #     for root, dirs, files in os.walk(src):
# #         for dirname in dirs:
# #             dirpath = os.path.join(des, root[src_prefix:], dirname)
# #             try:
# #                 os.mkdir(dirpath)
# #             except OSError as e:
# #                 print(e)

# #         for file in files:
# #             filePath = os.path.join(des, root[src_prefix:], file)
# #             if emptyFiles is True:
# #                 if emptyFiles is not False:
# #                     if isinstance(emptyFileSize, int):
# #                         write_file_of_size(filePath, emptyFileSize)
# #                 else:
# #                     write_file(filePath, "EMPTY TEST FILE CONTENT")
# #             # print(filePath)
# #         # break


# # def find_file_by_name(file_name, searchPath):
# #     # pylint: disable=unused-variable
# #     for currentpath, folders, files in os.walk(searchPath):
# #         # print(folders)
# #         for file in files:
# #             extension = os.path.splitext(file)
# #             if file == file_name:
# #                 fullPath = os.path.join(currentpath, file)
# #                 return fullPath
# #     return False


# # def generate_hash(value):
# #     """
# #         Generates a sha256 hash from the string provided.
# #         Parameters
# #         ----------
# #         value : str
# #             The string to calculate the hash on.
# #     """
# #     jsonStr = json.dumps(value).encode('utf-8')
# #     hex_dig = hashlib.sha256(jsonStr).hexdigest()
# #     return hex_dig


# # def generate_file_hash(filePath):
# #     """
# #         Generates a sha256 hash from the file contents.
# #         Parameters
# #         ----------
# #         filePath : str
# #             The path to the file to calculate the hash on.
# #     """
# #     fcd = get_file_content_data(filePath, STRIP_EMPTY_LINES=True)
# #     fs = file_content_data_to_string(fcd)
# #     return generate_hash(fs)


# # def write_file_of_size(des, size):
# #     kbSize = size * (1024 * 1024)
# #     with open(des, "wb") as out:
# #         out.truncate(kbSize)


# # def write_file(des, content):
# #     f = open(des, "w")
# #     f.write(content)
# #     f.close()


# def get_file_content_data(filePath, **kwargs):
#     """
#     Reads a file into a content dict {{line_number:int,raw_content:string}}
#         Parameters
#         ----------
#         filePath : str
#             The file path to the file to read... duh

#         STRIP_EMPTY_LINES : bool, optional
#             if True, remove empty lines from the dataArray
#     """
#     stripEmptyLines = False
#     if 'STRIP_EMPTY_LINES' in kwargs:
#         stripEmptyLines = kwargs['STRIP_EMPTY_LINES']

#     fileContent = read_file_to_array(filePath)
#     dataArray = []
#     for i, line in enumerate(fileContent):
#         data = {}
#         data['line_number'] = i
#         data['raw_content'] = line
#         if len(line) != 0 and stripEmptyLines is True or stripEmptyLines is False:
#             dataArray.append(data)
#     return dataArray


# def file_content_data_to_string(fileContent, **kwargs):
#     """Takes an array of file content and returns the raw_content as a string"""

#     stripEmptyLines = False
#     if 'STRIP_EMPTY_LINES' in kwargs:
#         stripEmptyLines = kwargs['STRIP_EMPTY_LINES']

#     finalString = ""
#     if isinstance(fileContent, str):
#         return fileContent
#     # print(f"-------fileContent: {fileContent}")
#     for x in fileContent:
#         # print(f"x: {x}")
#         if len(x['raw_content']) != 0 and stripEmptyLines is True or stripEmptyLines is False:
#             finalString += f"{x['raw_content']}\n"
#     return finalString


# # def read_file_to_array(filePath):
# #     with open(filePath, 'r', encoding='utf-8') as file:
# #         try:
# #             return file.read().splitlines()
# #         except UnicodeDecodeError:
# #             print(f"filePath: {filePath}")


# # def read_file(filePath):
# #     if if_file_exists(filePath) is True:
# #         with open(filePath, 'r', encoding='utf-8') as file:
# #             try:
# #                 return file.read()
# #             except UnicodeDecodeError:
# #                 print(f"filePath UnicodeDecodeError: {filePath}", PRESET="WARNING")
# #     else:
# #         print(f"read_file> filePath does not exist: {filePath}", PRESET="WARNING")
# #         return False


# # def read_json_file(filePath):
# #     '''
# #     Read a json file into a dictionary.
# #     strips all comments from file before reading.
# #     '''
# #     filePath = filePath.replace("\\", "/")
# #     fileContents = parse_json_comments(filePath)
# #     job = json.loads(fileContents)
# #     return job


# # def sanitize_windows_file_name(file_name):
# #     return re.sub(r'[<>:"/\|?*]*', "", file_name)


# # def get_content_data_array(filePath):
# #     finalData = []
# #     fileContent = read_file_to_array(filePath)
# #     for i, line in enumerate(fileContent):
# #         data = {}
# #         data['line_number'] = i
# #         data['raw_content'] = line
# #         finalData.append(data)
# #     return finalData


# # def write_to_json_file(dest, content):
# #     jsonStr = json.dumps(content)
# #     f = open(dest, "w")
# #     f.write(jsonStr)
# #     f.close()


# # def write_to_temporary_file(content):
# #     jsonStr = json.dumps(content)
# #     f = open("TempOutput.json", "w")
# #     f.write(jsonStr)
# #     f.close()


# # def parse_json_comments(filePath):
# #     fileArray = get_content_data_array(filePath)
# #     outputArray = []
# #     for l in fileArray:
# #         match = re.search(r'^\s*\/\/', l['raw_content'])
# #         if match is None:
# #             outputArray.append(l)
# #     # print(f"outputArray: {outputArray}")
# #     return file_content_data_to_string(outputArray)


# def file_ready_for_update(fileObj):
#     if fileObj.data['content_hash'] != fileObj.data['fileData']['content_hash']:
#         fileObj.log(f"File hash changed.", BGCOLOR="BLACK", COLOR="WHITE", INCDEC=4)
#         return True
#     return False


# def confirm_leading_period(string):
#     match = re.search(r"^\.", string)
#     if match:
#         return string
#     else:
#         return f".{string}"


# def slice_file_data(fileData, startLine=False, endLine=False):
#     sliceArray = []
#     for line in fileData:
#         if startLine != False:
#             if line['line_number'] >= startLine:
#                 if endLine != False:
#                     if line['line_number'] <= endLine:
#                         sliceArray.append(line)
#                 else:
#                     sliceArray.append(line)
#         else:
#             sliceArray.append(line)

#     return sliceArray


# # def create_dir(path, dirName):
# #     path = os.path.join(path, dirName)
# #     if if_dir_exists(path) is False:
# #         os.mkdir(path)
# #         if if_dir_exists(path) is True:
# #             return True
# #     else:
# #         return True


# # def if_file_exists(filePath):
# #     if os.path.isfile(filePath) is True:
# #         return True
# #     else:
# #         return False


# # def if_dir_exists(filePath):
# #     if os.path.isdir(filePath) is True:
# #         return True
# #     else:
# #         return False


# def collapse_file_array(fileArray):
#     fileContent = ""
#     for x in fileArray:
#         fileContent += f"{x['raw_content']}\n"
#     return fileContent


# # def delete_dir(filePath):
# #     try:
# #         shutil.rmtree(filePath)
# #     except OSError as e:
# #         print("Error: %s : %s" % (filePath, e.strerror))
