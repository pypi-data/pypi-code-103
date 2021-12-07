import os
import subprocess
from gbdmigration.download import Download
from gbdmigration.applier import AWSApply


def exec_cmd(cmd):
    subprocess.call(cmd.split(' '),
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT)


class Export:
    SNAPSHOT_DIR = '/data/brands/export/snapshots'
    PACKAGES_DIR = '/data/brands/export/packages'
    COLLECTION_DIR = '/data/brands/collections'
    INCR_DIR = '/data/brands/releases/'
    SIZE = 2000
    WORKERS = 25

    def __init__(self, collection):
        self.collection = collection

    def run(self):
        col_snapshot_dir = os.path.join(self.SNAPSHOT_DIR, self.collection)
        col_collection_dir = os.path.join(self.COLLECTION_DIR, self.collection)
        # 1. Verify if an initial snapshot exists. If not create one else create from incr
        if self._has_snapshot(col_snapshot_dir):
            # Get increments
            print("Creating increments snapshot")
            exec_cmd("gbd-export-snapincr %s %s %s -o %s" % (col_collection_dir,
                                                             self.collection,
                                                             self.INCR_DIR,
                                                             col_snapshot_dir))
        else:
            print("Creating initial snapshot")
            exec_cmd("gbd-export-snapshot %s %s -o %s" % (col_collection_dir,
                                                          self.collection,
                                                          col_snapshot_dir))
        export_folder = os.path.join(self.PACKAGES_DIR, self.collection)
        if not os.path.exists(export_folder):
            os.makedirs(export_folder)
        # 2. From snapsho, perform zips of 2000
        for snapshot in os.listdir(col_snapshot_dir):
            print("Creating package for %s. It will skip if exists" % snapshot)
            exec_cmd("gbd-export-package %s %s --size %s -w %s -o %s" % (
                os.path.join(col_snapshot_dir, snapshot),
                self.collection,
                self.SIZE,
                self.WORKERS,
                export_folder))
        # 3. Upload the zips.
        print("Uploading packages from %s to s3" % export_folder)
        exec_cmd("gbd-upload-package %s %s" % (export_folder, self.collection))



    def _has_snapshot(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            return False
        files = os.listdir(path)
        for f in files:
            if f.startswith('snapshot.'):
                return True
        return False

class Import:
    MIGRATION_DIR = '/efs-data/migration'

    def __init__(self, collection, bucket):
        self.collection = collection
        self.bucket = bucket

    def run(self):
        migration_folder = os.path.join(self.MIGRATION_DIR, self.collection)
        if not os.path.exists(migration_folder):
            os.makedirs(migration_folder)
        print("Downloading packages")
        upload = Download()
        upload.download_files(self.bucket, self.collection, migration_folder)

        for package in os.listdir(migration_folder):
            print("Importing %s" % package)
            a = AWSApply(os.path.join(migration_folder, package))
            a.prepare_upload()
            os.remove(os.path.join(migration_folder, package))
