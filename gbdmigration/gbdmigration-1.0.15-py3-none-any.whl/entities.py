import os
import json
import time
import math
from pymongo import MongoClient
from bson.objectid import ObjectId
from gbdtransformation.parser import Parser, EmptyNoneMunch
from munch import munchify
from zipfile import ZipFile
import shutil
from multiprocessing import Process, Queue, Pool, Manager

class EntityMigration:

    mappings = {
        'APP': 'emap',
        'REP': 'emrp'
    }

    search_key = {
        'APP': {
            0: 'Applicant',
            1: 'ApplicantIdentifier'

        },
        'REP': {
            0: 'Representative',
            1: 'RepresentativeIdentifier'
        }
    }

    parsers = {}

    nb_records_per_subdir = 10000
    pool_size = 15

    def __init__(self, collection_name, dest_root='./'):
        self.collection_name = collection_name
        self.db_url = 'mongodb://localhost:27017/'
        self.db_name = 'commons'
        self.dest_root = os.path.join(dest_root, 'tmp')
        os.makedirs(self.dest_root, exist_ok=True)
        # left pad subdirs
        self.pd_subdir = 10
        for tip in self.search_key.keys():
            self.parsers[tip] = Parser(self.mappings.get(tip))
        self.select_unique()
        m = Manager()
        q = m.Queue(2 * self.pool_size)
        Process(target=self.db_read, args=(q,)).start()
        p = Pool(self.pool_size)
        readers = []
        for i in range(self.pool_size):
            readers.append(p.apply_async(self.disk_write, (q,)))
        # Wait for the asynchrounous reader threads to finish
        [r.get() for r in readers]
        print("Zipping results")
        # Zip the results
        zip_path = 'entities_export.zip'
        with ZipFile(zip_path, 'w') as ziph:
            # Iterate over all the files in directory
            for root, dirs, files in os.walk(self.dest_root):
                for file in files:
                    ziph.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(self.dest_root, '..')))
        shutil.rmtree(self.dest_root)

    def select_unique(self):
        # Process records
        snapshot_file = os.path.join(self.dest_root, 'snapshot.txt')
        if os.path.exists(snapshot_file):
            return
        snapshot_id = {}
        self.connection = getattr(MongoClient(self.db_url), self.db_name)
        for mapping_key in self.mappings.keys():
            snapshot_id[mapping_key] = {}
            print("Creating snapshot %s%s from Mongo....." % (self.collection_name, mapping_key))
            coll = self.mappings.get(mapping_key)
            primary_search_key = self.search_key[mapping_key][0]
            secondary_search_key = self.search_key[mapping_key][1]
            _skip_fields = {'run_id': 0, 'uid': 0}
            docs = self.connection.get_collection(coll).find(
                {}, _skip_fields)
            raw_data = {}
            pbar = Progress(self.connection.get_collection(coll).count())
            for doc in docs:
                pbar.advance_with_step(1)
                if doc[primary_search_key]['@operationCode'] != 'Insert':
                    continue
                if raw_data.get(doc[primary_search_key][secondary_search_key], None):
                    if doc['archive'] < raw_data[doc[primary_search_key][secondary_search_key]]:
                        continue
                raw_data[doc[primary_search_key][secondary_search_key]] = doc['archive']
                snapshot_id[mapping_key][doc[primary_search_key][secondary_search_key]] = str(doc['_id'])
        buffer = []
        for mapping_key in self.mappings.keys():
            for key in snapshot_id[mapping_key].keys():
                buffer.append("%s,%s" % (mapping_key, snapshot_id[mapping_key][key]))
        with open(snapshot_file, 'w') as f:
            f.write('\n'.join(buffer))

    def db_read(self, q):
        # Process records
        print("\n\nProcessing snapshot")
        self.get_db_raw_data(q)
        for _ in range(self.pool_size):
            q.put({'done': True})

    def disk_write(self, q):
        self.connection = getattr(MongoClient(self.db_url), self.db_name)
        while True:
            message = q.get()
            if message.get('done', False):
                break
            mapping_key = message['mapping_key']
            _id = message['id']
            coll = self.mappings.get(mapping_key)
            _skip_fields = {'run_id': 0, 'uid': 0}
            docs = self.connection.get_collection(coll).find(
                {'_id': ObjectId(_id)}, _skip_fields)
            for doc in docs:
                self.convert_to_dynamo_data(doc, mapping_key)

    def get_db_raw_data(self, q):
        snapshot_file = os.path.join(self.dest_root, 'snapshot.txt')
        with open(snapshot_file, 'r') as f:
            lines = f.readlines()
        pbar = Progress(len(lines))
        for line in lines:
            pbar.advance_with_step(1)
            tmp = line.strip().split(',')
            while q.full():
                time.sleep(0.005)
            q.put({'id': tmp[1], 'mapping_key': tmp[0]})


    def get_linked_items(self, applicant, mapping_key):
        primary_search_key = self.search_key[mapping_key][0].lower()
        coll = "%s-map" %  self.mappings.get(mapping_key)
        _skip_fields = {'_id': 0, 'designs': 0, '_id': 0}
        docs = self.connection.get_collection(coll).find(
            {primary_search_key: applicant}, _skip_fields)
        to_return = []
        for doc in docs:
            for item in doc.get('trademarks', []):
                to_return.append(self.st13(item, self.collection_name.upper()))
        return to_return

    def st13(self, appnum, office):
        st13 = '%s%s' % (office.upper(), '55')
        # add application number and zfill till 17
        return '%s%s' % (st13, appnum.zfill(17 - len(st13)))

    def convert_to_dynamo_data(self, raw_data, mapping_key):
        primary_search_key = self.search_key[mapping_key][0]
        secondary_search_key = self.search_key[mapping_key][1]
        num = raw_data[primary_search_key][secondary_search_key]
        # create subdirs to contain max nb_records_per_subdir doc directories
        subdir = math.floor(int(num) / self.nb_records_per_subdir)
        stage_subdir = os.path.join(self.dest_root, str(subdir).zfill(self.pd_subdir))
        os.makedirs(stage_subdir, exist_ok=True)
        gbd_file = os.path.join(stage_subdir, '%s_%s.json' % (mapping_key, num))
        if os.path.exists(gbd_file):
            return
        db_data = {
            'entity_id': "%s.%s.%s" % (self.collection_name.lower(), mapping_key, num),
            'payload': {},
            'linked_items': []
        }
        gbd_data = self.parsers[mapping_key].run_with_object(**munchify(raw_data, factory=EmptyNoneMunch))
        db_data['payload'] = json.loads(gbd_data)
        # Add linked items
        db_data['linked_items'] = self.get_linked_items(num, mapping_key)
        # write the gbd.json file
        with open(gbd_file, 'w') as f:
            f.write(json.dumps(db_data))


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
