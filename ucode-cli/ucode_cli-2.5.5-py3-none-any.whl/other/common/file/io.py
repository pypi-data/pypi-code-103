import codecs
import csv
import os


def remove_if_exists(file_path: str):
    if os.path.exists(file_path):
        os.remove(file_path)


def write_file(file_path: str, content, write_mode: str = 'a', is_list=False):
    with codecs.open(file_path, write_mode, 'utf-8') as test_cycle:
        if is_list:
            for c in content:
                test_cycle.write(str(c) + '\n')
        else:
            test_cycle.write(content)
        test_cycle.close()


def write_list_simple_object_to_csv(file_path: str, list_object: list):
    with open(file_path, 'w', ) as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Name', 'Link'])
        for player in list_object:
            writer.writerow([player.name, player.link])
