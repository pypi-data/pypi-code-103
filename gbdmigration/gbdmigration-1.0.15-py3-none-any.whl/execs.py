import argparse
from gbdmigration.organiser import FileOrganiser
from gbdmigration.applier import AWSApply, AWSApplyEntity, AWSApplyDone, AWSApplySecrets
from gbdmigration.download import Download
from gbdmigration.filescanner import FileScanner
from gbdmigration.upload import Upload
from gbdmigration.entities import EntityMigration
from gbdmigration.pipelines import PipielineMigrations
from gbdmigration.done import DoneFilesManager
from gbdmigration.wrappers import Export, Import
from datetime import datetime
import os
from pathlib import Path

def build_command_parser(options, doc):
    """Argparse builder
    @param options: the dict of config options
    @pram doc: the helper for the command
    return parsed args"""
    parser = argparse.ArgumentParser(description=doc,
                                     formatter_class=argparse.RawTextHelpFormatter)
    for config in options:
        name = config.pop('name')
        parser.add_argument(*name, **config)
    return parser.parse_args()


def export_snapshot():
    """Run function for CLI"""
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [ {
        'name': ['path'],
        'type': str,
        'help': 'the path to the collection that needs migration'
    },
    {
        'name': ['collection'],
        'type': str,
        'help': 'the collaction to migrate'
    },
    {
        'name': ['-o'],
        'type': str,
        'default': './',
        'help': 'the path to where to save the snapshot file'
    }
    ]

    args = build_command_parser(configs, doc)
    f = FileScanner(args.collection, args.path)
    snapshot_name = 'snapshot.%s.%s' % (
        datetime.now().strftime('%Y%m%d.%H%M'), args.collection
    )
    snapshot_path = os.path.join(args.o, snapshot_name)
    f.to_csv(snapshot_path)

def export_snapincr():
    """Run function for CLI"""
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the collection that needs migration'
    },
    {
        'name': ['collection'],
        'type': str,
        'help': 'the collaction to migrate'
    },
    {
        'name': ['path_tar'],
        'type': str,
        'help': 'the path to the release archive/folder'
    },
    {
        'name': ['-o'],
        'type': str,
        'default': './',
        'help': 'the path to where to save the snapshot file'
    }
    ]

    args = build_command_parser(configs, doc)
    f = FileScanner(args.collection, args.path)
    if os.path.isdir(args.path_tar):
        p = Path(os.path.dirname(args.path_tar))
        files = [str(f) for f in list(p.glob('**/*%s.tar' % args.collection))]
    else:
        files = [args.path_tar]

    for archive in files:
        archive_name = os.path.basename(archive).replace('.tar', '').replace('_', '.')
        snapshot_name = 'snapincr.%s' % archive_name
        snapshot_name = os.path.join(args.o, snapshot_name)
        if os.path.exists(snapshot_name):
            continue
        f.extract_release(archive, snapshot_name)

def import_package():
    doc = """
        Tool to migrate a collection to AWS GBD.
        """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the collection that needs migration'
    }]
    args = build_command_parser(configs, doc)
    a = AWSApply(args.path)
    a.prepare_upload()

def export_package():
    """Run function for CLI"""
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the collection that needs migration'
    },
    {
        'name': ['collection'],
        'type': str,
        'help': 'the collaction to migrate'
    },
    {
        'name': ['--size'],
        'type': int,
        'default': 10000,
        'help': 'the start line from snapshot to perform the migration'
    },
    {
        'name': ['-n'],
        'type': int,
        'default': 0,
        'help': 'number of packages'
    },
    {
        'name': ['--offset'],
        'type': int,
        'default': 1,
        'help': 'the last line from snapshot to perform the migration'
    },
    {
        'name': ['-w'],
        'type': int,
        'default': 4,
        'help': 'the number of parallel workers'
    },
    {
        'name': ['-o'],
        'type': str,
        'default': './',
        'help': 'the path to where to save the archive file'
    }
    ]

    args = build_command_parser(configs, doc)
    i = 1
    while True:
        if args.n != 0 and i > args.n:
            break
        start = args.offset + args.size * (i-1)
        end = args.offset + args.size * i
        i += 1
        with open(args.path, 'r') as fout:
            file_size = len(fout.readlines())
        if file_size < end:
            zip_archive_tmp = "%s.%s-%s.zip" % (os.path.basename(args.path), start, file_size)
        else:
            zip_archive_tmp = "%s.%s-%s.zip" % (os.path.basename(args.path), start, end-1)
        if os.path.exists(os.path.join(args.o, zip_archive_tmp)):
            continue
        if start > file_size:
            break
        f = FileOrganiser(args.collection, args.path,
                          start=start, end=end,
                          dest_root=args.o,
                          nb_workers=args.w)
        res = f.prepare_collection()
        if not res:
            break


def upload_package():
    """Run function for CLI"""
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the collection that needs migration'
    },
    {
        'name': ['collection'],
        'type': str,
        'help': 'the collaction to migrate'
    },
    {
        'name': ['--role'],
        'type': str,
        'default': 'arn:aws:iam::161581150093:role/devops',
        'help': 'the name of the role to assume identity'
    },
    {
        'name': ['--bucket'],
        'type': str,
        'default': 'gbd-migrations-eu-central-1-161581150093',
        'help': 'the bucket name'
    },
    ]

    args = build_command_parser(configs, doc)
    upload = Upload(args.role)
    upload.upload_file(args.bucket, args.collection, args.path)

def download_packages():
    """Run function for CLI"""
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path where to download the collection'
    },
    {
        'name': ['collection'],
        'type': str,
        'help': 'the collaction to migrate'
    },
    {
        'name': ['--role'],
        'type': str,
        'default': 'arn:aws:iam::161581150093:role/devops',
        'help': 'the name of the role to assume identity'
    },
    {
        'name': ['--bucket'],
        'type': str,
        'default': 'gbd-migrations-eu-central-1-161581150093',
        'help': 'the bucket name'
    },
    ]

    args = build_command_parser(configs, doc)
    upload = Download()
    upload.download_files(args.bucket, args.collection, args.path)

def export_collection():
    doc = """
        Tool to migrate a collection to AWS GBD.
        """
    configs = [
        {
            'name': ['collection'],
            'type': str,
            'help': 'the collaction to migrate'
        }
    ]
    args = build_command_parser(configs, doc)
    e = Export(args.collection)
    e.run()

def delete_files():
    doc = """
          Tool to migrate a collection to AWS GBD.
          """
    configs = [
        {
            'name': ['bucket'],
            'type': str,
            'help': 'the collaction to migrate'
        },
        {
            'name': ['--ext'],
            'type': str,
            'default': None,
            'help': 'the extension to delete'
        },
        {
            'name': ['--role'],
            'type': str,
            'default': 'arn:aws:iam::161581150093:role/devops',
            'help': 'the name of the role to assume identity'
        },
    ]
    args = build_command_parser(configs, doc)
    e = Upload(args.role)
    e.delete_all_objects(args.bucket, ext=args.ext)

def import_collection():
    doc = """
        Tool to migrate a collection to AWS GBD.
        """
    configs = [
        {
            'name': ['collection'],
            'type': str,
            'help': 'the collaction to migrate'
        },
        {
            'name': ['--bucket'],
            'type': str,
            'default': 'gbd-migrations-eu-central-1-161581150093',
            'help': 'the bucket name'
        },
    ]
    args = build_command_parser(configs, doc)
    e = Import(args.collection, args.bucket)
    e.run()


def export_entities():
    """Run function for CLI"""
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [
    {
        'name': ['collection'],
        'type': str,
        'help': 'the collaction to migrate'
    }
    ]

    args = build_command_parser(configs, doc)
    EntityMigration(args.collection)

def import_entities():
    """Run function for CLI"""
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the collection that needs migration'
    }]
    args = build_command_parser(configs, doc)
    a = AWSApplyEntity(args.path)
    a.prepare_upload()


def export_done():
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the done files'
    }]
    args = build_command_parser(configs, doc)
    d = DoneFilesManager(args.path)
    d.start()


def import_done():
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to the done file exported from bsidx1'
    }]
    args = build_command_parser(configs, doc)
    a = AWSApplyDone(args.path)
    a.prepare_upload()


def export_pipelines():
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['pipelines_path'],
        'type': str,
        'help': 'the path to pipelines config dir'
    },{
        'name': ['git_path'],
        'type': str,
        'help': 'the path to git config'
    },{
        'name': ['collection_type'],
        'type': str,
        'help': 'the collection_type'
    }]

    args = build_command_parser(configs, doc)
    d = PipielineMigrations(args.pipelines_path, args.git_path, args.collection_type)
    d.start()

def import_pipelines_secrets():
    doc = """
    Tool to migrate a collection to AWS GBD.
    """
    configs = [{
        'name': ['path'],
        'type': str,
        'help': 'the path to secrtes file'
    }]

    args = build_command_parser(configs, doc)
    d = AWSApplySecrets(args.path)
    d.prepare_upload()
