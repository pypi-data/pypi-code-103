import os.path
import subprocess
import tempfile
import time

import PySide2.scripts


def create_py_from_qrc(qrc_file):
    fd, filename = tempfile.mkstemp(".py", "qrc-", text=True)

    pyside_dir = os.path.dirname(PySide2.__file__)
    rcc = os.path.join(pyside_dir, "rcc")
    args = [rcc, '-g', 'python', os.path.abspath(qrc_file), '-o', filename]

    try:
        os.close(fd)

        subprocess.run(args, capture_output=False, check=True)

        with open(filename, "r", encoding="utf-8") as f:
            return f.read()
    finally:
        # delete temporary files
        try:
            os.unlink(filename)
        except PermissionError:
            time.sleep(1)
            try:
                os.unlink(filename)
            except Exception:
                pass


def compare_and_update(filename, new_contents):
    with open(filename, 'r', encoding="utf-8") as f:
        old_lines = f.readlines()
    new_lines = new_contents.splitlines(keepends=True)

    new_uncommented = [l for l in new_lines if not l.startswith("#")]
    old_uncommented = [l for l in old_lines if not l.startswith("#")]

    if new_uncommented == old_uncommented:
        print("No Change: {}".format(os.path.basename(filename)))
        return
    else:
        with open(filename, 'w', encoding="utf-8") as f:
            f.write(new_contents)
        print("Updated: {}".format(os.path.basename(filename)))


def update_qrc(qrc_file):
    # pull off the .qrc
    root, _ext = os.path.splitext(qrc_file)
    if _ext != ".qrc":
        root = qrc_file

    # add _rc.py to the end
    output_file = root + "_rc.py"

    new_contents = create_py_from_qrc(qrc_file)
    compare_and_update(output_file, new_contents)


def main():
    for root, dirs, files in os.walk("."):
        # skip hidden files and folders
        files = [f for f in files if not f[0] == '.']
        dirs[:] = [d for d in dirs if not d[0] == '.']

        # skip build directory
        if 'build' in dirs:
            dirs.remove('build')

        for file in files:
            if file.endswith('.qrc'):
                update_qrc(os.path.join(root, file))


if __name__ == "__main__":
    main()
