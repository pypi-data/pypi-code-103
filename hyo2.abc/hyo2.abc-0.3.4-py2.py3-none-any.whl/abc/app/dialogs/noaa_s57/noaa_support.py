import ctypes
import os
import shutil
import traceback
import zipfile
import logging

from hyo2.abc.lib.progress.cli_progress import CliProgress
from hyo2.abc.lib.lib_info import LibInfo
from hyo2.abc.app.app_info import AppInfo
from hyo2.abc.lib.helper import Helper
from hyo2.abc.lib.ftp import Ftp

logger = logging.getLogger(__name__)


class NOAASupport:

    media = os.path.join(os.path.dirname(__file__), "media")
    caris_root = "C:\\CARIS"
    support_version = "2022.1"

    @classmethod
    def v_version(cls):
        return cls.support_version.replace(".", "v")

    def __init__(self, lib_info: LibInfo, app_info: AppInfo, progress=CliProgress()):
        self._li = lib_info
        self._ai = app_info
        self.progress = progress
        self.local_zip_path = os.path.abspath(os.path.join(Helper(lib_info=self._li).package_folder(),
                                                           "Caris_Support_Files_%s.zip" % self.v_version()))
        self.local_batch_file = None

    # internal zip

    def internal_zip_path(self):
        for item in os.listdir(self.media):
            candidate_path = os.path.join(self.media, item)
            if (("Caris_Support_Files_%s" % self.v_version()) in item) \
                    and (os.path.splitext(candidate_path)[-1] == ".zip"):
                return candidate_path
        return str()

    def internal_zip_path_exists(self):
        return self.internal_zip_path() != ""

    def unzip_internal_zip(self):

        if not self.delete_local_noaa_support_files():
            return False

        try:
            z = zipfile.ZipFile(self.internal_zip_path(), "r")
            unzip_path = Helper(lib_info=self._li).package_folder()

            logger.debug("unzipping %s to %s" % (self.internal_zip_path(), unzip_path))

            name_list = z.namelist()
            file_nr = len(name_list)
            self.progress.start(title="Unzipping")

            file_count = 0
            for item in name_list:
                # print(item)
                z.extract(item, unzip_path)
                file_count += 1
                pct = int((file_count / file_nr) * 100.0)
                self.progress.update(value=pct)

            z.close()
            self.progress.end()
            return True

        except Exception as e:
            logger.warning("unable to unzip the file: %s, %s" % (self.internal_zip_path(), e))
            return False

    # download

    def download_from_noaa(self):
        """try to download the data set"""
        logger.debug('downloading NOAA Caris Support Files from NOAA FTP')

        if not self.delete_local_noaa_support_files():
            return False

        try:
            # ftp.ocsftp.ncd.noaa.gov
            ftp = Ftp("205.156.4.84", show_progress=True, debug_mode=False,
                      progress=self.progress)
            data_zip_src = "HSD/Customization_Files/CARIS/Caris_Support_Files_%s.zip" % self.v_version()
            ftp.get_file(data_zip_src, self.local_zip_path, unzip_it=True)
            return self.local_noaa_support_folder_present()

        except Exception as e:
            traceback.print_exc()
            logger.error('during download and unzip: %s' % e)
            return False

    def download_from_unh(self):
        """try to download the data set"""
        logger.debug('downloading NOAA Caris Support Files from UNH FTP')

        if not self.delete_local_noaa_support_files():
            return False

        try:
            ftp = Ftp("ftp.ccom.unh.edu", show_progress=True, debug_mode=False,
                      progress=self.progress)
            data_zip_src = "fromccom/hydroffice/Caris_Support_Files_%s.zip" % self.v_version()
            ftp.get_file(data_zip_src, self.local_zip_path, unzip_it=True)
            return self.local_noaa_support_folder_present()

        except Exception as e:
            logger.error('during WOA09 download and unzip: %s' % e)
            return False

    # local folder

    def local_noaa_support_folder(self):
        ret = str()
        for folder in sorted(os.listdir(Helper(lib_info=self._li).package_folder())):
            # logger.debug("folder: %s" % folder)
            if ("Caris_Support_Files" in folder) and (len(folder) > 24):
                ret = os.path.join(Helper(lib_info=self._li).package_folder(), folder)

        return ret

    def local_noaa_support_folder_version(self):
        if not self.local_noaa_support_folder_present():
            return str()
        noaa_support_basename = os.path.split(self.local_noaa_support_folder())[-1]
        return noaa_support_basename.replace("Caris_Support_Files_", "").replace("_", ".")

    def local_noaa_support_folder_present(self):
        return os.path.basename(self.local_noaa_support_folder()) == "Caris_Support_Files_%s" % self.v_version()

    def delete_local_noaa_support_files(self):

        try:
            if os.path.exists(self.local_zip_path):
                os.remove(self.local_zip_path)

        except Exception as e:
            logger.error('during cleaning zip archive: %s' % e)
            return False

        for folder in os.listdir(Helper(lib_info=self._li).package_folder()):

            candidate_path = os.path.join(Helper(lib_info=self._li).package_folder(), folder)
            if os.path.isfile(candidate_path):
                continue

            if ("Caris_Support_Files_%s" % self.v_version()) in folder:

                try:
                    # remove all the content
                    for root, dirs, files in os.walk(candidate_path, topdown=False):
                        for name in files:
                            os.remove(os.path.join(root, name))
                        for name in dirs:
                            os.rmdir(os.path.join(root, name))

                    os.rmdir(candidate_path)

                except Exception as e:
                    logger.error('during cleaning folder %s: %s' % (candidate_path, e))
                    return False

        return True

    def check_local_batch_file_exists(self):
        if not self.local_noaa_support_folder_present():
            return False

        for item in os.listdir(self.local_noaa_support_folder()):

            candidate_path = os.path.join(self.local_noaa_support_folder(), item)
            if os.path.isdir(candidate_path):
                continue

            if ("Caris_Support_Files_%s" % self.v_version()) in item:

                if os.path.splitext(candidate_path)[-1] == ".txt":
                    logger.debug("copy and rename .txt to .bat")
                    txt_path = candidate_path
                    candidate_path = os.path.splitext(candidate_path)[0] + ".bat"
                    shutil.copyfile(txt_path, candidate_path)

                self.local_batch_file = candidate_path
                return True

        return False

    def open_local_noaa_support_folder(self):
        if self.local_noaa_support_folder_present():
            Helper.explore_folder(self.local_noaa_support_folder())
            return

        Helper(lib_info=self._li).explore_package_folder()

    # system folder

    @classmethod
    def system_noaa_support_folder(cls):
        if not os.path.exists(cls.caris_root):
            os.makedirs(cls.caris_root)
            if not os.path.exists(cls.caris_root):
                return str()

        for folder in os.listdir(cls.caris_root):
            # logger.debug("folder: %s" % folder)
            if ("Caris_Support_Files_%s" % cls.v_version()) in folder:
                return os.path.join(cls.caris_root, folder)

        return str()

    @classmethod
    def system_noaa_support_folder_version(cls):
        if not cls.system_noaa_support_folder_present():
            return str()
        noaa_support_basename = os.path.split(cls.system_noaa_support_folder())[-1]
        return noaa_support_basename.replace("Caris_Support_Files_", "").replace("_", ".")

    @classmethod
    def system_noaa_support_folder_present(cls):
        return cls.system_noaa_support_folder() != ""

    def delete_system_noaa_support_files(self):

        if not self.system_noaa_support_folder_present():
            logger.debug("nothing to delete")
            return False

        try:
            # remove all the content
            for root, dirs, files in os.walk(self.system_noaa_support_folder(), topdown=False):
                for name in files:
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))

            os.rmdir(self.system_noaa_support_folder())

        except Exception as e:
            logger.error('during cleaning folder %s: %s' % (self.system_noaa_support_folder(), e))
            return False

        return True

    def copy_local_to_system(self):

        if not self.local_noaa_support_folder_present():
            logging.warning("unable to find the local NOAA support folder")
            return False

        if self.system_noaa_support_folder_present():
            self.delete_system_noaa_support_files()
            if self.system_noaa_support_folder_present():
                logging.warning("unable to delete the system NOAA support folder")
                return False

        src = self.local_noaa_support_folder()
        dst = os.path.join(self.caris_root, os.path.basename(src))
        shutil.copytree(src, dst)

        return self.system_noaa_support_folder_present()

    def system_batch_file(self):
        if not self.system_noaa_support_folder_present():
            return False

        for item in os.listdir(self.system_noaa_support_folder()):

            candidate_path = os.path.join(self.system_noaa_support_folder(), item)
            if os.path.isdir(candidate_path):
                continue

            if ("Caris_Support_Files_%s" % self.v_version()) in item:

                if os.path.splitext(candidate_path)[-1] == ".txt":
                    logger.debug("copy and rename .txt to .bat")
                    txt_path = candidate_path
                    candidate_path = os.path.splitext(candidate_path)[0] + ".bat"
                    shutil.copyfile(txt_path, candidate_path)

                return candidate_path

        return str()

    def system_batch_file_exists(self):
        return self.system_batch_file() != ""

    @classmethod
    def open_system_noaa_support_folder(cls):
        if cls.system_noaa_support_folder_present():
            Helper.explore_folder(cls.system_noaa_support_folder())
            return

    # execute batch
    def exec_system_batch(self):
        if not self.system_batch_file_exists():
            logger.warning("The batch file does not exist! Did you unzip and copy the support files?")
            return False

        logger.info("The batch file must be executed as administrator with all other users logged off the system!")

        if Helper.is_user_admin():
            os.system(self.system_batch_file())
            return True
        else:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", self.system_batch_file(), "", None, 1)
            return True

    def __repr__(self):
        msg = "<%s>\n" % self.__class__.__name__
        msg += "  <local zip: %s>\n" % self.local_zip_path
        return msg
