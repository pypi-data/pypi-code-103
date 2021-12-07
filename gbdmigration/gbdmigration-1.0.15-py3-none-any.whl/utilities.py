import json
import os
import zlib
import shutil
from datetime import datetime
import xmltodict


RAW_DOCUMENTS = '{{RAW_DOCUMENTS}}'
GBD_DOCUMENTS = '{{GBD_DOCUMENTS}}'
IMAGES_BUCKET = '{{IMAGES_BUCKET}}'


def get_gbd_format(path_to_raw, appnum, parser):
    try:
        transformed = parser.run(path_to_raw, raise_errors=True)
        return json.loads(transformed), None
    except Exception as e:
        return {}, '%s - %s' % (appnum, e)


def appnum_to_subdirs(appnum):
    """
    return a properly zfilled 2 level path from the application number:
     - 0123456789 should return 67/89
     - 1 should return 00/01
    """
    appnum = appnum.zfill(4)
    subs_dir = os.path.join(appnum[-4:-2], appnum[-2:])
    return subs_dir


def appnum_to_dirs(appnum, dest_root):
    """
    return the prefix_dir with the properly zfilled 2 level path from
    the application number
    - prefix_dir: /data/brand-data/frtm/xml/  && appnum = 1 >
    /data/brand-data/frtm/xml/00/01/
    """
    return os.path.join(dest_root, appnum_to_subdirs(appnum), appnum)


def get_crc(img_file):
    prev = 0
    fh = open(img_file, 'rb')
    for eachLine in fh:
        prev = zlib.crc32(eachLine, prev)
    fh.close()
    return "%X" % (prev & 0xFFFFFFFF)


def rename_img(img_file, new_name, new_path):
    """
    helper to rename img files
    123.1.png 123.1-th.jpg
    """
    _, basename = os.path.split(img_file)
    name, ext = os.path.splitext(basename)
    renamed = os.path.join(new_path, '%s%s' % (new_name, ext))
    shutil.copyfile(img_file, renamed)
    return renamed


def build_s3_path(bucket_name, filename, s_type, collection):
    store_path = os.path.join(s_type, collection, filename)
    storage_location = os.path.join(bucket_name, store_path)
    return storage_location


def prepare_copies_for_dynamo(st13, meta_info, s_type, collection):
    run_id = meta_info['run_id']
    office_extraction_date = '1900-01-01'
    xml_location = os.path.basename(meta_info['xml'].replace('.gz', '')).split('.')[1]
    results = {
        "gbd_extraction_date": datetime.today().strftime("%Y-%m-%d"),
        "run_id": run_id,
        "st13": st13,
        'gbd_type': s_type,
        "biblio": "%s.%s" % (st13, xml_location),
        'gbd_collection': collection,
        "office_extraction_date": office_extraction_date,
        'logo': [],
        'archive': '__bsidx1n__'
    }
    return results


ifc_map = {
    'cl': 'color',
    'ph': 'shape',
    'jc': 'composite',
    'sf': 'concept'
}

def parse_lire(lire_file, crc):
    with open(lire_file, 'r') as f:
        raw_xml_data = xmltodict.parse(f.read())
        xml_data = {}
        for field in raw_xml_data['doc']['field']:
            key = field.get('@name', None)
            value = field.get('#text', None)
            if key and value:
                xml_data[key] = value
        return {
            "crc": crc,
            "lastAnalyzed": "1900-01-01",
            "imgDescColor": xml_data.get('cl_hi'),
            "imgDescShape": xml_data.get('ph_hi'),
            "imgDescComposite": xml_data.get('jc_hi'),
            "imgDescConcept": xml_data.get('sf_hi'),
            "imgClassIC": xml_data.get('classes_significant_ws', '').split(' '),
            "imgActiveDesc": [ifc_map.get(x[:2]) for x in xml_data.keys() if x.endswith('_hi')]
        }

def prepare_preprod_for_dynamo(st13, meta_info, high_image, s_type, collection, lire_json):
    run_id = meta_info['run_id']
    office_extraction_date = '1900-01-01'
    logo = []
    for img in high_image:
        logo.append(os.path.basename(img).split('-')[0])
    results = {
        "gbd_extraction_date": datetime.today().strftime("%Y-%m-%d"),
        "latest_run_id": run_id,
        "st13": st13,
        'gbd_type': s_type,
        'gbd_collection': collection,
        "office_extraction_date": office_extraction_date,
        'image_analysis': lire_json if lire_json else [],
        'logo': logo,
        'archive': '__bsidx1n__'
    }
    return results
