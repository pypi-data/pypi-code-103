import os
from shutil import copyfile


def convert_file_lines_into_array(path):
    file = open(path, 'r')
    lines = file.readlines()
    arr = []
    for i in lines:
        arr.append(i.split('\n')[0])
    return arr


class FileManager:
    found_files = []
    search_list = []
    search_paths = []
    copy_path = []
    not_found = []
    found_objects = []
    not_found_search_list = []

    def search_file_without_extension_utlilty(self, root_dir):
        for file_or_dir in os.scandir(root_dir):
            if file_or_dir.is_dir():
                self.search_file_without_extension_utlilty(file_or_dir)
            else:
                if file_or_dir.name.split('.')[0] in self.not_found_search_list:
                    file2 = open("dummy.txt", "w+")
                    file2.write(os.getcwd() + '/' + file_or_dir.path)
                    file2.close()
                    file2 = open("dummy.txt", "r")
                    file_path = file2.readlines()[0]
                    self.found_objects.append({'file_name': file_or_dir.name.split('.')[0], 'file_path': file_path})
                    self.found_files.append(file_or_dir.name.split('.')[0])
                    self.not_found_search_list.remove(file_or_dir.name.split('.')[0])

    def search_file_and_copy_without_extension_utlilty(self, root_dir):
        for file_or_dir in os.scandir(root_dir):
            if file_or_dir.is_dir():
                self.search_file_and_copy_without_extension_utlilty(file_or_dir)
            else:
                if file_or_dir.name.split('.')[0] in self.not_found_search_list:
                    file2 = open("dummy.txt", "w+")
                    file2.write(os.getcwd() + '/' + file_or_dir.path)
                    file2.close()
                    file2 = open("dummy.txt", "r")
                    file_path = file2.readlines()[0]
                    self.found_objects.append({'file_name': file_or_dir.name.split('.')[0], 'file_path': file_path, 'copy_path': self.copy_path + file_or_dir.name})
                    self.found_files.append(file_or_dir.name.split('.')[0])
                    copyfile(file_path, self.copy_path + file_or_dir.name)
                    self.not_found_search_list.remove(file_or_dir.name.split('.')[0])

    def search_file_with_extension_utlilty(self, root_dir):
        for file_or_dir in os.scandir(root_dir):
            if file_or_dir.is_dir():
                self.search_file_without_extension_utlilty(file_or_dir)
            else:
                if file_or_dir.name in self.not_found_search_list:
                    file2 = open("dummy.txt", "w+")
                    file2.write(os.getcwd() + '/' + file_or_dir.path)
                    file2.close()
                    file2 = open("dummy.txt", "r")
                    file_path = file2.readlines()[0]
                    self.found_objects.append({'file_name': file_or_dir.name, 'file_path': file_path})
                    self.found_files.append(file_or_dir.name)
                    self.not_found_search_list.remove(file_or_dir.name)

    def search_file_and_copy_with_extension_utlilty(self, root_dir):
        for file_or_dir in os.scandir(root_dir):
            if file_or_dir.is_dir():
                self.search_file(self, file_or_dir)
            else:
                if file_or_dir.name in self.not_found_search_list:
                    file2 = open("dummy.txt", "w+")
                    file2.write(os.getcwd() + '/' + file_or_dir.path)
                    file2.close()
                    file2 = open("dummy.txt", "r")
                    file_path = file2.readlines()[0]
                    self.found_objects.append({'file_name': file_or_dir.name, 'file_path': file_path})
                    self.found_files.append(file_or_dir.name)
                    copyfile(file_path, self.copy_path + file_or_dir.name)
                    self.not_found_search_list.remove(file_or_dir.name)

    def search_file_without_extension(self, search_files, search_paths):
        '''
            search_files should be an arr
            search_paths should be an arr
        '''
        self.search_list = search_files
        self.search_paths = search_paths
        self.not_found_search_list = search_files

        for path in search_paths:
            self.search_file_without_extension_utlilty(path)

        return self.found_objects

    def search_file_and_copy_without_extension(self, search_files, search_paths, copy_path):
        '''
            copy_path should be string path ending with /
            search_files should be an arr
            search_paths should be an arr
        '''
        self.search_list = search_files
        self.search_paths = search_paths
        self.copy_path = copy_path
        self.not_found_search_list = search_files

        for path in search_paths:
            self.search_file_and_copy_without_extension_utlilty(path)

        return self.found_objects

    def search_file_with_extension(self, search_files, search_paths):
        '''
            search_files should be an arr
            search_paths should be an arr
        '''
        self.search_list = search_files
        self.search_paths = search_paths
        self.not_found_search_list = search_files

        for path in search_paths:
            self.search_file_with_extension_utlilty(path)

        return self.found_objects

    def search_file_and_copy_with_extension(self, search_files, search_paths, copy_path):
        """
            copy_path should be string path ending with /
            search_files should be an arr
            search_paths should be an arr
        """
        self.search_list = search_files
        self.search_paths = search_paths
        self.copy_path = copy_path
        self.not_found_search_list = search_files

        for path in search_paths:
            self.search_file_and_copy_with_extension_utlilty(path)

        return self.found_objects

    def find_files_not_found(self):
        self.not_found = set(self.search_list) - set(self.found_files)
        if self.not_found:
            return self.not_found
        else:
            self.not_found
