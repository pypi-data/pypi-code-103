from gbdmigration.filescanner import FileScanner
import gbdmigration.utilities as utilities
from gbdtransformation.parser import Parser
from gbdvalidation.engine import RuleEngine
import json
import os
import gzip
import shutil
import time
from zipfile import ZipFile
import multiprocessing

parser = None
validator = None
parser_solr = None

def convert_keys_type(input_dict):
    for key in input_dict.keys():
        if isinstance(input_dict[key], list):
            input_dict[key] = set(input_dict[key])
    return input_dict

def parse_lire_solr(lires):
    to_return = convert_keys_type(lires[0])
    for lire in lires[1:]:
        for key in lire.keys():
            if isinstance(lire[key], list):
                to_return[key] += set(lire[key])
            else:
                to_return[key] = '%s,%s' % (to_return[key], lire[key])
    for key in to_return.keys():
        if isinstance(to_return[key], set):
            to_return[key] = list(to_return[key])
    return to_return



def process_appnum(csv_file, appnum, dest_root, s_type, collection):
    gbd_format, error = utilities.get_gbd_format(csv_file['xml'], appnum, parser)

    st13 = gbd_format.get('st13')
    if not st13:
        return appnum, error
    # Create folders structure
    dest_folder = utilities.appnum_to_dirs(st13, dest_root)
    os.makedirs(dest_folder, exist_ok=True)
    # Move the images
    raw_high_image = []
    for f in sorted(csv_file['images']):
        if '.high' in f:
            raw_high_image.append(f)
    high_image = []
    crcs = []
    for img in raw_high_image:
        crc = utilities.get_crc(img)
        crcs.append(crc)
        high_image.append(utilities.rename_img(img, '%s%s' % (crc, '-hi'), dest_folder))
        img_base_path = img.replace('.high.png', '')
        icon_image = "%s-ic.jpg" % img_base_path
        try:
            utilities.rename_img(icon_image, '%s%s' % (crc, '-ic'), dest_folder)
        except Exception as _:
            error = '%s - %s' % (appnum, 'Icon image missing')
            return appnum, error
        thumbnail_image = "%s-th.jpg" % img_base_path
        try:
            utilities.rename_img(thumbnail_image, '%s%s' % (crc, '-th'), dest_folder)
        except Exception as _:
            error = '%s - %s' % (appnum, 'Thumb image missing')
            return appnum, error
    # Move the extracted xml
    with gzip.open(csv_file['xml'], 'rb') as f, \
            open(os.path.join(dest_folder, os.path.basename(csv_file['xml'].replace('.gz', ''))),
                 'wb') as g:
        g.write(f.read())
    # QC
    errors = validator.validate_with_dict(gbd_format)
    for error in errors:
        if error['severity'] == 'CRITICAL':
            return (appnum, "QC:%s" % error['message'])
    # Create the dynamodb copies
    copies = utilities.prepare_copies_for_dynamo(st13, csv_file, s_type, collection)
    with open(os.path.join(dest_folder, "copies.dynamo"), 'w') as f:
        f.write(json.dumps(copies))
    # Move the gbd_format
    with open(os.path.join(dest_folder, "%s.json" % csv_file['run_id']), 'w') as f:
        f.write(json.dumps(gbd_format))
    # Get lire info
    lire_json = []
    for idx, lire_file in enumerate(csv_file['lire']):
        crc = crcs[idx]
        lire_json.append(utilities.parse_lire(lire_file, crc))
    # Create the dyanmodb preprod
    preprod = utilities.prepare_preprod_for_dynamo(st13, csv_file, high_image, s_type, collection, lire_json)
    with open(os.path.join(dest_folder, "preprod.dynamo"), 'w') as f:
        f.write(json.dumps(preprod))

    # add custom values to biblio
    gbd_format['runid'] = preprod.get('latest_run_id')
    gbd_format['qc'] = errors
    logos = preprod.get('logo', [])

    with open(os.path.join(dest_folder, 'idx.dynamo'), 'w') as f:
        solr_json, error = utilities.get_gbd_format(json.dumps(gbd_format), appnum, parser_solr)
        if len(lire_json) > 0:
            solr_json.update(parse_lire_solr(lire_json))
        solr_json['runid'] = preprod.get('latest_run_id')
        solr_json['collection'] = collection
        solr_json['logo'] = logos
        f.write(json.dumps(solr_json))
    return (appnum, error)


class FileOrganiser:

    def __init__(self, collection, path, dest_root='./',
                 start=0, end=None, nb_workers=None):
        global parser
        global validator
        global parser_solr
        self.collection = collection
        self.dest_root = os.path.join(dest_root, 'tmp.%s' % time.time())
        self.start = start
        self.end = end
        self.path = path
        self.type = 'brands' if self.collection.endswith('tm') else 'designs'
        self.scanner = FileScanner(collection, None)
        if not parser:
            parser = Parser(self.collection)
        if not validator:
            validator = RuleEngine()
        if not parser_solr:
            parser_solr = Parser('solrjtm')
        self.errors = []
        self.nb_workers = nb_workers


    def prepare_collection(self):
        csv_files = self.scanner.from_csv(self.path, start=self.start, end=self.end)
        if self.end - self.start > len(csv_files):
            end = self.start + len(csv_files) - 1
        else:
            end = self.end - 1
        workers = min(multiprocessing.cpu_count() - 4, self.nb_workers)
        with multiprocessing.Pool(processes=workers) as pool:  # auto closing workers
            raw_results = pool.starmap(process_appnum, [(csv_files[appnum], appnum,
                                                         self.dest_root, self.type, self.collection)
                                                        for appnum in csv_files.keys()])
        assert len(raw_results) == len(csv_files.keys())
        for appnum, error in raw_results:
            if error:
                self.errors.append(error)
        # archive the output_project and cleanup
        zip_archive_tmp = "%s.%s-%s" % (os.path.basename(self.path), self.start, end)
        zip_archive = zip_archive_tmp
        if self.errors:
            zip_archive += '.part(%s)' % (end - self.start - len(self.errors) + 1 )
        zip_archive += '.zip'
        error_file = zip_archive_tmp + '.part(%s).err' % len(self.errors)
        zip_path = os.path.join(os.path.dirname(self.dest_root), zip_archive)
        error_path = os.path.join(os.path.dirname(self.dest_root), error_file)
        with ZipFile(zip_path, 'w') as ziph:
            # Iterate over all the files in directory
            for root, dirs, files in os.walk(self.dest_root):
                for file in files:
                    ziph.write(os.path.join(root, file),
                               os.path.relpath(os.path.join(root, file),
                                               os.path.join(self.dest_root, '..')))
        shutil.rmtree(self.dest_root)
        if self.errors:
            with open(error_path, 'w') as f:
                f.write('\n'.join(self.errors))
        if len(csv_files) < self.end - self.start:
            return False
        return True
