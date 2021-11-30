import hashlib
import logging
import os
from typing import Iterable, Union

import pandas as pd
from pathlib import Path

import rsa
from rsa import VerificationError
from rsa.key import PublicKey

logger = logging.getLogger(__name__)

alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

_dtypes = {
    'pcd': 'str',
    'oseast1m': 'float64',
    'osnrth1m': 'float64',
    'laua': 'str',
    'pcd_abbr': 'str',
}
columns = list(_dtypes.keys())


class Postcodes:
    _read = set()
    _data_dir = Path(__file__).parent
    _df = pd.DataFrame({c: pd.Series(dtype=t) for c, t in _dtypes.items()})
    __hashes = None

    def __init__(self, pubkey: PublicKey = None, data_dir: Union[Path, str] = None):
        if data_dir is not None:
            self._data_dir = Path(data_dir)
        elif os.getenv('QLACREF_DATA_DIR') is not None:
            self._data_dir = Path(os.environ['QLACREF_DATA_DIR'])

        if os.getenv('QLACREF_PC_INSECURE') == 'True':
            return

        if pubkey is None:
            key = os.environ['QLACREF_PC_KEY']
            try:
                pubkey = rsa.PublicKey.load_pkcs1(key)
            except ValueError:
                pubkey = None

            if pubkey is None:
                with open(key, 'rt') as file:
                    pubkey = rsa.PublicKey.load_pkcs1(file.read())

        if pubkey is None:
            raise Exception("No public key found, and insecure flag not set.")

        with open(self._data_dir / 'hashes.sig', 'rt') as file:
            signature = bytes.fromhex(file.read())

        with open(self._data_dir / 'hashes.txt', 'rb') as file:
            file_data = file.read()

        rsa.verify(file_data, signature, pubkey)
        file_data = file_data.decode('ascii').split('\n')

        self.__hashes = {n: h for h, n in [w.split(' ') for w in file_data if len(w) > 0]}

    def _get_filename(self, letter):
        return self._data_dir / f"postcodes_{letter}.pickle.gz"

    def _read_pickle(self, letter):
        filename = self._get_filename(letter)
        logger.debug(f"Opening {filename}")
        if self.__hashes is not None:
            with open(filename, 'rb') as file:
                hash = hashlib.sha512(file.read()).hexdigest()
                if hash != self.__hashes[filename.name]:
                    raise VerificationError(f"Incorrect hash for {filename}")
        return pd.read_pickle(filename)

    @property
    def dataframe(self):
        return self._df

    def load_postcodes(self, letters: Iterable[str]):
        if os.getenv("QLAC_DISABLE_PC"):
            return
        dataframes = [self._df]
        to_load = set([l.upper() for l in letters]) - self._read
        logger.info(f"Loading {to_load}")
        for letter in to_load:
            if letter in self._read:
                continue
            try:
                df = self._read_pickle(letter)
                logger.debug(f"Read {df.shape[0]} postcodes from {letter}")
                dataframes.append(df)
            except (ValueError, FileNotFoundError):
                logger.debug(f"File not found for {letter}")
                pass

        if len(dataframes) > 1:
            logger.debug(f"Concateting {len(dataframes)} dataframes")
            self._df = pd.concat(dataframes)
            self._df.reset_index(drop=True, inplace=True)
            logger.debug(f"Creating abbreviations")
            self._df['pcd_abbr'] = self._df['pcd'].str.replace(' ', '')
            logger.debug(f"Done")
            self._read = self._read | to_load
