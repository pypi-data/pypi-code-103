import os

base_file_path = os.getcwd() + os.sep + "data"
print(base_file_path)


def write_local_file(file_name, df):
    if not os.path.exists(base_file_path):
        os.mkdir(base_file_path)
    with open(base_file_path + os.sep + file_name, 'w') as f: f.write(df)
