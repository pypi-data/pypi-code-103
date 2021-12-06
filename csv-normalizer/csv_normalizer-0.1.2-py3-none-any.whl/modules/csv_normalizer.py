# CSV Normalizer main class
import pandas as pd
import os
import collections
from . import file_processing
from pathlib import Path
class Csv_Normalizer:
    def __init__(self, config_dict, no_rename_old = False) -> None:
        """
        :param: config_dict
        {
            'csv_import_folder': '/path/import/folder',
            'csv_export_folder': '/path/export/folder',
            # Export headers you want, those missing in the import will be added 
            # with empty data.
            'csv_export_headers': ('Series_reference', 'Period', 'ELEE'),
            # delimiter only affects the output file.
            'csv_delimiter': ';',
            # Options: https://docs.python.org/3.5/library/codecs.html#text-encodings
            # use mbcs for ansi on python prior 3.6
            'csv_encoding': 'utf-8',
        }
        param: no_rename_old
                Set to true if you don't want to rename the old file

        """
        self.csv_import_folder = config_dict.get('csv_import_folder')
        self.csv_export_folder = config_dict.get('csv_export_folder')
        self.csv_export_headers = config_dict.get('csv_export_headers')
        self.csv_delimiter = config_dict.get('csv_delimiter', ";")
        self.csv_encoding = config_dict.get('csv_encoding', "utf-8")
        self.no_rename_old = no_rename_old

        _export_folder = Path(self.csv_export_folder)
        if _export_folder.is_dir():
            pass
        else:
            msg = (f"Error: export folder is not a directory: {self.csv_export_folder} \n"
                             )
            raise SystemExit(msg)

        if self.csv_export_folder == self.csv_import_folder:
            raise SystemExit(f'Same folder for import and export is not yet supported \n'
                             'If you need support, create issue requesting it')

    def _import_file(self, file):
        """
        param: file: file to read from csv to pandas
        param: sep: separator, default ;
        Read the .csv file and return pandas Dataset.
        """
        imported_data = pd.read_csv(file, sep=self.csv_delimiter)
        return imported_data
    
    def _normalize_data(self, dataset):
        """
        input: dataset to normlize
        return: normalized dataset with only columns desired in csv_export_headers
        """
        new_data = dataset.reindex(columns=self.csv_export_headers)
        return new_data
    
    def _export_csv(self, dataset, file):
        """
        input: dataset to export to csv
        return: True: No errors
                False: Failed to export
        """
        export_succeed = True # type: bool
        try:
            dataset.to_csv(path_or_buf=file, index=False, sep=self.csv_delimiter, encoding=self.csv_encoding)
        except:
            export_succeed = False
        
        return export_succeed

    def run(self):
        """
        run the process, 
            - scan the directory for .csv files
            - For each file:
                - read and Normalize the columns
                - export to the desired directory the .csv resultant file
                - rename old to _normalized?
        # return summary defaultdict
            {'ok': [{
                'import_path': '/full/path/origfile.csv'
                'export_path': '/full/path/filename.csv'},{
                'import_path': '/full/path/origfile.csv'
                'export_path': '/full/path/filename.csv'}]
             'failed': [{'import_path': '/full/path/origfile.csv'
                'export_path': '/full/path/filename.csv'},{
                'import_path': '/full/path/origfile.csv'
                'export_path': '/full/path/filename.csv'}]
            }
            When no data, default dict is:
            {'ok': [],
             'failed': []}
        """
        _summary_dict = collections.defaultdict(dict) # type: dict
        _summary_dict['ok'] = []
        _summary_dict['failed'] = []

        # Get the list of the files
        _files_list = file_processing.get_file_list(self.csv_import_folder, extension='*.csv')
        #iterate over each file
        for file in _files_list:
            _pd_imported_data = self._import_file(file=file)
            # normalize
            _pd_normalized_data = self._normalize_data(_pd_imported_data)
            # exported path
            _basename_file = os.path.basename(file)
            _export_path_file = os.path.join(self.csv_export_folder, _basename_file)
            # export
            _export_result_bool = self._export_csv(_pd_normalized_data,
                                                   # Use export path joining csv_export_folder with original name of file
                                                   file=_export_path_file
                                                   )
            if _export_result_bool:
                _summary_dict['ok'].append({'import_path': file,
                                           'export_path': _export_path_file})
                # Rename old file
                if not self.no_rename_old:
                    file_processing.rename_file(file, f'{file}.old')
            else:
                _summary_dict['failed'].append({'import_path': file,
                                           'export_path': _export_path_file})

        # return summary defaultdict
        return _summary_dict
