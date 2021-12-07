from path import Path
from fs.copy import copy_fs
from fs.zipfs import ZipFS
from fs.osfs import OSFS
import zipfile as z
import typing as t


# =============================== File finders functions ===============================
# Tested it works
def walk(path: str, pattern: str):
    return Path(path).walk(pattern)


# Tested it works
def list_all(path: str):
    # clean up.
    return Path(path).listdir()


# Tested ,It works
def find(path: str, pattern: str, **kwd):
    return Path(path).listdir(pattern)


# =============================== CRUD(files&dirs) functions ===============================
# ╭─────────────────────────────────────────────╮
# │ >>>>>>> Create(files&dirs) functions <<<<<< │
# ╰─────────────────────────────────────────────╯
# Tested it works
def create(path: str, **kwd):
    # Considering when dir not exist
    return Path(path).touch()


def create_folder(path: str, **kwd):
    p = Path(path)
    p.mkdir()


# ╭─────────────────────────────────────────────╮
# │ >>>>>>> Delete(files&dirs) functions <<<<<< │
# ╰─────────────────────────────────────────────╯

# Tested it works(Almost perfect)
def smart_delete(path: str):
    p = Path(path)
    if p.isdir():
        p.rmtree()
    elif p.isfile():
        p.remove()


# Tested it works(But feel... a litte weird?)
def delete(path: str, **kwd):
    p = Path(path)
    if p.isdir():
        # must be an exist dir
        print(
            f"The '{p}' is a dir(folder), and will not be deleted, if you want to"
            " delete a folder try to use delete_folder"
        )
        return
    p.remove()


def rmdir(path: str):
    p = Path(path)
    p.rmtree_p()


def rmdir_all(f_list: t.List[Path]):
    for p in f_list:
        rmdir(p)


# Tested ,it works
def _delete_all(f_list: list):
    for f in f_list:
        smart_delete(f)


# ╭─────────────────────────────────────────────╮
# │ >>>>>>> Rename(files&dirs) functions <<<<<< │
# ╰─────────────────────────────────────────────╯
#  Status:It works(Not done yet)
def rename(
    path: str, new_name: str = None, with_suffix: str = None, with_prefix: str = None
):
    if new_name:
        if with_suffix or with_prefix:
            raise ValueError(
                "You don't need to do that, considering in this"
                " way: 'prefix-newname.suffix'"
            )
        suffix = Path(path).ext
        _new_name = Path(path).dirname() / new_name + suffix
    elif with_suffix and with_prefix:
        # if new_name exists... wow...
        _new_name = Path(path).dirname() / with_prefix + Path(path).stem + with_suffix
    elif with_suffix:
        if new_name:
            raise ValueError("You can just pass 'newname.suffix' to new_name ")
        _new_name = Path(path).with_suffix(with_suffix)
    elif with_prefix:
        if new_name:
            raise ValueError("You can just pass 'prefix-newname.suffix' to new_name ")
        _new_name = Path(path).dirname() / with_prefix + Path(path).name

    else:
        raise ValueError("Need to pass at least one argument")

    Path(path).rename(_new_name)


def _rename_all(f_list: t.List[Path], with_prefix: str = None, with_suffix: str = None):

    if not with_prefix and not with_prefix:
        raise ValueError("To change files name, Must have a prefix or suffix ")

    for f in f_list:
        rename(f, with_suffix=with_suffix, with_prefix=with_prefix)


# ╭─────────────────────────────────────────────╮
# │ >>>>>>> Delete(files&dirs) functions <<<<<< │
# ╰─────────────────────────────────────────────╯
# Fixed, then test it.
def move(src: str, dst: str):
    p = Path(src)
    p.move(dst)


def _move_all(f_list: t.List[Path], dst: str):
    for f in f_list:
        f.move(dst)


# =============================== Zip archieves functions ===============================
# ╭─────────────────────────────────────────────╮
# │ >>>>>>> OldZip(files&dirs) functions <<<<<< │
# ╰─────────────────────────────────────────────╯
# Tested ,it works(first appear in lesson 13)
def zip(src: str, dst: str):
    src, dst = Path(src), Path(dst)
    ffs = copy_fs(OSFS(dst), ZipFS(src))

    return ffs


def _zip_all(f_list: t.List[Path]):
    for f in f_list:
        ...


def unzip(src: str, dst: str):
    src, dst = Path(src), Path(dst)
    ffs = copy_fs(ZipFS(src), OSFS(dst, create=True))
    return ffs


def _upzip_all(f_list: t.List[Path]):
    for f in f_list:
        unzip(f, f.stem)


# ╭─────────────────────────────────────────────╮
# │ >>>>>>> NewZip(files&dirs) functions <<<<<< │
# ╰─────────────────────────────────────────────╯
# Not tested yet(replace the old)
exclude = [".DS_Store", "__MACOSX", "__pycache__"]


def zip_files(folder_path: str, /, without_dir=False):
    if not Path(folder_path).isdir():
        raise ValueError(f"{folder_path} is not a dir(folder)")

    # could make it better here, but not this time
    # count = len(same_name)
    # name = f"{name}({count})"

    dir_name = Path(folder_path).abspath().basename()
    ac_path = Path(folder_path).abspath() / dir_name + ".zip"
    files = [f for f in Path(folder_path).files() if not f.basename() in exclude]

    with z.ZipFile(ac_path, compression=z.ZIP_DEFLATED, mode='w') as zp:
        if without_dir:
            for f in files:
                zp.write(f.abspath(), f.name)
            return

        for f in files:
            zp.write(f)


def _zip_files(f_list: t.List[Path], with_folder=False, **kwd):

    first = f_list[0]
    default_tar = first.parent / "archive.zip"

    with z.ZipFile(default_tar, compression=z.ZIP_DEFLATED, mode='w') as zp:
        if with_folder:
            for f in f_list:
                zp.write(f.abspath(), f.parent.basename() / f.name)
                # Filename:file location  Arcname:file struct in zipfile
            return
        for f in f_list:
            zp.write(f.abspath(), f.name)


def zipit(f_path: str):
    assert Path(f_path).isfile()

    parent_dir, file_name = (Path(f_path).abspath().parent, Path(f_path).abspath().stem)
    ac_path = parent_dir / file_name + ".zip"
    with z.ZipFile(ac_path, compression=z.ZIP_DEFLATED, mode="w") as zp:
        zp.write(Path(f_path), Path(f_path).name)


def unzipit(ac_path: str, target: t.Union[Path, str] = Path("./")):

    import shutil

    shutil.unpack_archive(ac_path, target)


# =============================== FS utils functions ===============================


def empty_check(f_list: t.List[Path], **kwd):

    if not f_list:
        raise ValueError("No files found")

    return locals()


def hidden_check(f_list: t.List[Path], **kwd):
    return dict(f_list=[f for f in f_list if not f.basename() in exclude]).update(kwd)
