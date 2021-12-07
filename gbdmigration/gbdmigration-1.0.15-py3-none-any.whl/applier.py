from zipfile import ZipFile
import os

try:
    from pypers.core.interfaces.config.pypers_storage import RAW_DOCUMENTS, GBD_DOCUMENTS, IMAGES_BUCKET
    from pypers.core.interfaces.db import get_pre_prod_db_history, get_pre_prod_db, get_db_entity, get_done_file_manager
    from pypers.core.interfaces.storage import get_storage
    from pypers.core.interfaces.db import secretsdb
    from pypers.core.interfaces import msgbus
    from pypers.utils.utils import appnum_to_dirs
    copies_db = get_pre_prod_db_history()
    preprod_db = get_pre_prod_db()
    entities_db = get_db_entity()
except Exception as e:
    print(e)
    pass
import shutil
import json
import concurrent.futures



def get_gbd_files_path(run_id, type, collection, st13=None):
    root_path = os.environ.get('GBDFILES_DIR', os.getcwd())
    root_path = os.path.join(root_path, run_id, type, collection)
    if st13:
        root_path = appnum_to_dirs(root_path, st13)
        root_path = os.path.join(root_path, st13)
    os.makedirs(root_path, exist_ok=True)
    return root_path


class AWSApplyEntity:

    def __init__(self, path_to_archive):
        self.archive = path_to_archive

    def prepare_upload(self):
        temp = os.path.basename(self.archive).replace('.zip', '')
        print('extracting...')
        if not os.path.exists(temp):
            with ZipFile(self.archive, 'r') as zipObj:
                # Extract all the contents of zip file in different directory
                zipObj.extractall(temp)
        print("starting importing....")
        folders = os.listdir(temp)
        root = os.path.join(temp, folders[0])
        # tmp/00xxxxxx/file.json
        # get list of appnums
        items = []
        for subdirs in os.listdir(root):
            if os.path.isdir(os.path.join(root, subdirs)):
                for f in os.listdir(os.path.join(root, subdirs)):
                    f_path = os.path.join(root, subdirs, f)
                    items.append(f_path)
        failed_items = entities_db.put_items(items)
        print("failed_items: %s" % '\n'.join(failed_items))


class AWSApplyDone:

    def __init__(self, path_to_file):
        self.done_file = path_to_file
        self.db = get_done_file_manager()

    def prepare_upload(self):
        print("starting importing....")
        with open(self.done_file, 'r') as f, self.db.table.batch_writer() as writer:
            items = json.loads(f.read())
            pbar = Progress(len(items))
            pbar.start()
            for item in items:
                self.db.try_retry(writer.put_item, Item=item)
                pbar.advance_with_step(1)


class AWSApplySecrets:

    def __init__(self, path_to_file):
        self.secrets = path_to_file
        self.sm = secretsdb.get_secrets()

    def prepare_upload(self):
        print("starting importing....")
        with open(self.secrets, 'r') as f:
            items = f.readlines()
            pbar = Progress(len(items))
            pbar.start()
            for item in items:
                key, value = item.strip().split(" ")
                self.sm.put(key, value)
                pbar.advance_with_step(1)


class AWSApply:

    def __init__(self, path_to_archive):
        self.archive = path_to_archive
        self.run_id = '_'.join(os.path.basename(self.archive).split('.')[1:4])
        self.collection = os.path.basename(self.archive)[3]

    def prepare_upload(self):
        temp = os.path.basename(self.archive).replace('.zip', '')
        with ZipFile(self.archive, 'r') as zipObj:
            # Extract all the contents of zip file in different directory
            zipObj.extractall(temp)
        folders = os.listdir(temp)
        # get list of appnums
        appnums_path = []
        for root, dirs, files in os.walk(os.path.join(temp, folders[0])):
            for f in files:
                if f.endswith('.dynamo'):
                    appnums_path.append(root)
                    break
        self._parallel_process(appnums_path)
        print("Triggering indexing...")
        output_dir = os.path.join(os.environ['WORK_DIR'], 'updates')
        pipeline_type = 'brands' if self.collection.endswith('tm') else 'designs'
        msgbus.get_msg_bus().send_message(self.run_id,
                                          collection="index_%s" % self.collection,
                                          type=pipeline_type,
                                          custom_config=['pipeline.output_dir=%s' % output_dir]
                                          )

    @staticmethod
    def _element_migration(el):
        AWSMigrationElement(el).migrate()

    @staticmethod
    def _sub_arry_offset(max_paralel, length, offset):
        if offset + max_paralel < length:
            return offset + max_paralel
        return length

    def _parallel_process(self, tasks_to_do):

        max_parallel = 25
        # Schedule an initial scan for each segment of the table.  We read each
        # segment in a separate thread, then look to see if there are more rows to
        # read -- and if so, we schedule another scan.
        pbar = Progress(len(tasks_to_do))

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


class AWSMigrationElement:

    def __init__(self, path_to_files):
        self.root = path_to_files
        self.st13 = os.path.basename(self.root)
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

    @staticmethod
    def _rename_file(old_file, new_name):
        """
        helper to rename img files
        123.1.png 123.1-th.jpg
        """
        if not os.path.exists(old_file):
            return old_file
        basepath, basename = os.path.split(old_file)
        name, ext = os.path.splitext(basename)
        renamed = os.path.join(basepath, '%s%s' % (new_name, ext))
        shutil.move(old_file, renamed)
        return renamed

    def migrate(self):
        self.migrate_dynamo()
        self.migrate_files()

    def migrate_dynamo(self):
        with open(os.path.join(self.root, 'copies.dynamo'), 'r') as f:
            file_data = json.load(f)
            copies_db.try_retry(copies_db.table.put_item, Item=file_data)

        with open(os.path.join(self.root, 'preprod.dynamo'), 'r') as f:
            file_data = json.load(f)
            self.collection = file_data.get('gbd_collection')
            self.type = 'brands' if self.collection.endswith('tm') else 'designs'
            run_id = file_data.get('latest_run_id')
            appnum = file_data.get('st13')
        shutil.copy(os.path.join(self.root, 'preprod.dynamo'),
                    os.path.join(get_gbd_files_path(run_id, self.type, self.collection, appnum), 'latest.json'))
        shutil.copy(os.path.join(self.root, 'idx.dynamo'),
                    os.path.join(get_gbd_files_path(run_id, self.type, self.collection, appnum), 'idx.json'))

    def migrate_files(self):
        for f in os.listdir(self.root):
            if f.endswith('.dynamo'):
                continue
            if f.endswith('.json'):
                self._do_store(f, GBD_DOCUMENTS, store_subpath=os.path.join(self.type, self.collection, self.st13))
            elif f.endswith('.xml'):
                tmp = self._rename_file(os.path.join(self.root, f), self.st13)
                self._do_store(os.path.basename(tmp), RAW_DOCUMENTS,
                               store_subpath=os.path.join(self.type, self.collection, '__bsidx1n__'))
            else:
                self._do_store(f, IMAGES_BUCKET, store_subpath=os.path.join(self.type, self.collection, self.st13))

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


def print_progress_bar(iteration, total, prefix='', suffix='',
                       decimals=1, length=100, fill='█', print_end="\r"):
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
    filled_length = int(length * iteration // total)
    bar = fill * filled_length + '-' * (length - filled_length)
    print(f'\r{prefix} |{bar}| {percent}% {suffix}', end=print_end)
    # Print New Line on Complete
    if iteration == total:
        print()


class Progress:
    def __init__(self, total):
        self.total = total
        self.done = 0

    def start(self):
        print_progress_bar(0, self.total,
                           prefix='Progress:', suffix='Complete', length=50)

    def advance(self, value):
        self.done = value
        print_progress_bar(self.done, self.total,
                           prefix='Progress:', suffix='Complete', length=50)

    def advance_with_step(self, value):
        self.done += value
        print_progress_bar(self.done, self.total,
                           prefix='Progress:', suffix='Complete', length=50)
