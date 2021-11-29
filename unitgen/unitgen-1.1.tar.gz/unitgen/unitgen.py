from .args_checker_parser import ArgsCheckerAndParser
from .test_files_generator import TestFilesGenerator

def check_and_get_files():
    args_checker_parser = ArgsCheckerAndParser()
    args_checker_parser.inital_checker()
    return args_checker_parser.get_files_list()


def generate_test_files(files_list):
    test_files_generator = TestFilesGenerator()
    for file in files_list:
        test_files_generator.generate_test_file(file)

def main():
    files_list = check_and_get_files()
    generate_test_files(files_list)

if __name__ == '__main__':
    main()
