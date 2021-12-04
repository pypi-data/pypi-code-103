import glob
import os
import urllib.request

from ucode.helpers.clog import CLog


def download_all_scratch_submission(folder):
    sub_folders = glob.glob(folder + "/*")
    print(sub_folders)
    has_scratch_online = []
    for sub_folder in sub_folders:
        if not os.path.isdir(sub_folder):
            continue
        print(sub_folder)
        files = glob.glob(sub_folder + "/*.txt")
        for file in files:
            path, name = os.path.split(file)
            name, extension = os.path.splitext(name)
            with open(file, "r") as f:
                url = f.read()
                downloaded_file = os.path.join(path, name + ".sb3")
                print(url, downloaded_file)
                if "scratch.mit.edu" in url:
                    downloaded_file = os.path.join(path, name + "-ERROR-scratch-online.err")
                    CLog.error(f"Scratch online: {downloaded_file}")
                    _, student = os.path.split(path)
                    has_scratch_online.append(student)
                urllib.request.urlretrieve(url, downloaded_file)
    print(len(has_scratch_online))
    print(*sorted(has_scratch_online), sep="\n")
    has_scratch_online = set(has_scratch_online)
    print((len(has_scratch_online)))
    print(*sorted(has_scratch_online), sep="\n")


if __name__ == "__main__":
    # folder = r"D:\Tin học tre\So khao Quoc gia 2021\Ket_qua_bang_A_final"
    folder = r"D:\Tin học tre\So khao Quoc gia 2021\test"
    download_all_scratch_submission(folder)