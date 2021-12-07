from zipfile import ZipFile
import os
from pypers.core.interfaces.config.pypers_storage import RAW_DOCUMENTS, GBD_DOCUMENTS, IMAGES_BUCKET
from pypers.core.interfaces.db import get_pre_prod_db_history, get_pre_prod_db
from pypers.core.interfaces.storage import get_storage
from gbdmigration.organiser import RAW_DOCUMENTS as RAW_DOCUMENTS_PLACE_HOLDER
from gbdmigration.organiser import GBD_DOCUMENTS as GBD_DOCUMENTS_PLACE_HOLDER
from gbdmigration.organiser import IMAGES_BUCKET as IMAGES_BUCKET_PLACE_HOLDER
from pathlib import Path
import json
import concurrent.futures

copies_db = get_pre_prod_db_history()
preprod_db = get_pre_prod_db()

class AWSApplay:

    def __init__(self, path_to_archive):
        self.load_env()
        self.archive = path_to_archive

    def prepare_upload(self):
        temp = os.path.basename(self.archive).replace('.zip', '')
        with ZipFile(self.archive, 'r') as zipObj:
            # Extract all the contents of zip file in different directory
            zipObj.extractall(temp)
        # get list of appnums
        appnums_path = []
        for root, dirs, files in os.walk(os.path.join(temp, 'tmp')):
            for f in files:
                if f.endswith('.dynamo'):
                    appnums_path.append(root)
                    break
        self._paralel_process(appnums_path)

    def _element_migration(self, el):
        AWSMigrationElement(el).migrate()

    def _sub_arry_offset(self, max_paralel, length, offset):
        if offset + max_paralel < length:
            return offset + max_paralel
        return length

    def _paralel_process(self, tasks_to_do):

        max_parallel = 25
        # Schedule an initial scan for each segment of the table.  We read each
        # segment in a separate thread, then look to see if there are more rows to
        # read -- and if so, we schedule another scan.
        pbar = progress(len(tasks_to_do))

        task_counter = 0
        # Make the list an iterator, so the same tasks don't get run repeatedly.

        with concurrent.futures.ThreadPoolExecutor() as executor:

            # Schedule the initial batch of futures.  Here we assume that
            # max_scans_in_parallel < total_segments, so there's no risk that
            # the queue will throw an Empty exception.
            futures = {
                executor.submit(self._element_migration, el): el
                for el in tasks_to_do[task_counter:self._sub_arry_offset(max_parallel,
                                                                         len(tasks_to_do),
                                                                         task_counter)]
            }
            pbar.start()
            task_counter = len(futures)
            while futures:
                # Wait for the first future to complete.
                done, _ = concurrent.futures.wait(
                    futures, return_when=concurrent.futures.FIRST_COMPLETED
                )
                for fut in done:
                    fut.result()
                    futures.pop(fut)
                pbar.advance_with_step(len(done))
                # Schedule the next batch of futures.  At some point we might run out
                # of entries in the queue if we've finished scanning the table, so
                # we need to spot that and not throw.
                for el in tasks_to_do[task_counter:self._sub_arry_offset(len(done), len(tasks_to_do), task_counter)]:
                    task_counter += 1
                    futures[executor.submit(self._element_migration, el)] = el


    def load_env(self):
        if os.environ.get('GBD_INIT_ENV', None):
            current_path = os.environ.get('GBD_INIT_ENV')
        else:
            current_path = os.getcwd()
        init_files = [f for f in os.listdir(current_path) if f.endswith('.ini')]
        env_vars_to_set = {}
        for init_file in sorted(init_files):
            with open(init_file, 'r') as f:
                for line in f.readlines():
                    if line.startswith('#'):
                        continue
                    tmp = line.split('=')
                    if len(tmp) != 2:
                        continue
                    key = tmp[0].strip()
                    value = tmp[1].strip()
                    if '#' in value:
                        value = value.split('#')[0]
                        value = value.strip()
                    env_vars_to_set[key] = value
        for key, value in env_vars_to_set.items():
            os.environ[key] = value


class AWSMigrationElement:

    def __init__(self, path_to_files):
        self.root = path_to_files
        self.appnum = os.path.basename(self.root)
        if os.environ.get('GBD_STORAGE', 'S3') != 'S3':
            prefix = 'file://' + os.environ.get("GBD_FS_STORAGE_PATH", os.getcwd()) + '/'
        else:
            prefix = 's3://'
        self.IMAGES_BUCKET = prefix + IMAGES_BUCKET
        self.GBD_DOCUMENTS = prefix + GBD_DOCUMENTS
        self.RAW_DOCUMENTS = prefix + RAW_DOCUMENTS
        self.storage = get_storage()
        self.collection = None
        self.type = None


    def migrate(self):
        self.update_content()
        self.migrate_dynamo()
        self.migrate_files()

    def update_content(self):
        to_update = ['copies.dynamo', 'preprod.dynamo']
        p = Path(self.root)
        to_update.extend([f.name for f in p.glob('**/*.json')])
        for tmp in to_update:
            with open(os.path.join(self.root, tmp), 'r') as f:
                file_data = f.read()
                file_data = file_data.replace(
                    IMAGES_BUCKET_PLACE_HOLDER, self.IMAGES_BUCKET).replace(
                    GBD_DOCUMENTS_PLACE_HOLDER, self.GBD_DOCUMENTS).replace(
                    RAW_DOCUMENTS_PLACE_HOLDER, self.RAW_DOCUMENTS)
            with open(os.path.join(self.root, tmp), 'w') as f:
                f.write(file_data)

    def migrate_dynamo(self):
        with open(os.path.join(self.root, 'copies.dynamo'), 'r') as f:
            file_data = json.load(f)
            copies_db.try_retry(copies_db.table.put_item, Item=file_data)
        with open(os.path.join(self.root, 'preprod.dynamo'), 'r') as f:
            file_data = json.load(f)
            self.collection = file_data.get('gbd_collection')
            self.type = 'brands' if self.collection.endswith('tm') else 'designs'
            preprod_db.try_retry(preprod_db.table.put_item, Item=file_data)

    def migrate_files(self):
        for f in os.listdir(self.root):
            if f.endswith('.dynamo'):
                continue
            if f.endswith('.json'):
                res = self._do_store(f, GBD_DOCUMENTS, store_subpath=self.appnum)
            elif f.endswith('.xml'):
                res = self._do_store(f, RAW_DOCUMENTS)
            else:
                res = self._do_store(f, IMAGES_BUCKET)

    def _do_store(self, file, store_root, store_subpath=''):
        # file on disk
        file_disk_path = os.path.join(self.root, file)
        if not os.path.exists(file_disk_path):
            return '<n/a>'

        _, file_name = os.path.split(file)

        # set the location for storage
        if store_subpath:
            store_path = os.path.join(store_subpath, file_name)
        else:
            store_path = os.path.join(self.type, self.collection, file_name)
        backup_path = self.storage.do_store(file_disk_path, store_root, store_path)
        return backup_path


def printProgressBar(iteration, total, prefix = '', suffix = '',
                     decimals=1, length = 100, fill = '█', printEnd = "\r"):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        length      - Optional  : character length of bar (Int)
        fill        - Optional  : bar fill character (Str)
        printEnd    - Optional  : end character (e.g. "\r", "\r\n") (Str)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(length * iteration // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=printEnd)
    # Print New Line on Complete
    if iteration == total:
        print()

class progress:
    def __init__(self, total):
        self.total = total
        self.done  = 0

    def start(self):
        printProgressBar(0, self.total,
                        prefix='Progress:', suffix='Complete', length=50)

    def advance(self, value):
        self.done = value
        printProgressBar(self.done, self.total,
                        prefix='Progress:', suffix='Complete', length=50)

    def advance_with_step(self, value):
        self.done += value
        printProgressBar(self.done, self.total,
                        prefix='Progress:', suffix='Complete', length=50)





if __name__ == '__main__':
    a = AWSApplay('../extract.20210527.0545_krtm.0-None.zip')
    a.prepare_upload()