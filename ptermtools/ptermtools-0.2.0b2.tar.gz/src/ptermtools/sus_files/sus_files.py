#!/usr/bin/env python3
import io
import os
import pathlib

from xdg import xdg_data_dirs, xdg_data_home

SUS_FILES_DB_LOCATIONS = [f"{xdg_data_home()}/susfiledb"] + [
    f"{data_dir}/susfilesdb" for data_dir in xdg_data_dirs()
]

if os.environ.get("SUSFILEDB"):
    SUS_FILES_DB_LOCATIONS.insert(0, os.environ["SUSFILEDB"])


class SuspiciousFileDatabase:
    def __init__(
        self,
        location: str or pathlib.Path or None = None,
        suspicious_files: list or None = None,
    ) -> None:
        if location is not None:
            self.location = location
        elif location is None:
            for db_loc in SUS_FILES_DB_LOCATIONS:
                print(f"Trying {db_loc}")
                if pathlib.Path(db_loc).exists():
                    self.location = db_loc
                    break
            else:
                self.location = f"{xdg_data_home()}/susfiledb"
        else:
            self.location = f"{xdg_data_home()}/susfiledb"
        self._load_list()

    def _dump_list(self):
        with open(self.location, "w") as fout:
            for sus_file in self.suspicious_files:
                fout.write(f"{sus_file}\n")
        print(f"Wrote {self.location}")

    def _load_list(self):
        try:
            with open(self.location, "r") as db_file:
                self.suspicious_files = [s.strip() for s in db_file.readlines()]
        except OSError as e:
            print(e)
            self.suspicious_files = []
            self._dump_list()

    def add(self, fname):
        print(f"Adding {fname} to suspicious files list.")
        self.suspicious_files.append(fname)
        self._dump_list()

    def list(self):
        print("Currently tracked suspicious files:")
        [print(f) for f in self.suspicious_files]

    def remove(self, fname):
        print(f"Removing {fname} from suspicious files list.")
        self.suspicious_files.remove(fname)
        self._dump_list()
