import os
import json
from datetime import datetime


class DoneFilesManager:
    def __init__(self, path):
        self.path = path

    def start(self):
        done_files = []
        for f in self._get_files():
            done_files.extend(self.process(f))
        with open('done_files_migration.json', 'w') as f:
            f.write(json.dumps(done_files))

    def _get_files(self):
        done_files = []
        for root, dirs, files in os.walk(self.path):
            for f in files:
                if f.endswith(".done"):
                    done_files.append(os.path.join(root, f))
        return done_files

    def _parse_timestamp(self, run_id, file):
        try:
            return datetime.strptime(run_id, "%Y%m%d.%H%M").strftime("%Y-%m-%d")
        except:
            return datetime.now().strftime("%Y-%m-%d")

    def process(self, file_path):
        done = []
        unique = []
        collection, _ = os.path.splitext(os.path.basename(file_path))
        with open(file_path, 'r') as f:
            for line in f.readlines():
                run_id, archive_name = line.strip().split('\t')
                tmp = '%s_%s' % (collection, archive_name)
                if tmp in unique:
                    print("duplicate for %s %s" % (collection, archive_name))
                    continue
                unique.append(tmp)
                done.append({
                  "gbd_collection": collection,
                  "run_id": run_id,
                  "archive_name": archive_name,
                  "process_date": self._parse_timestamp(run_id, file_path)
                })
        return done

