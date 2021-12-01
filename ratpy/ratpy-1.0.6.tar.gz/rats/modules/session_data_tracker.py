import pandas as pd
import os
from rats.modules.RATS_CONFIG import Packet

class SessionDataTracker:

    data_files: pd.DataFrame = None
    topo_files: pd.DataFrame = None

    def __init__(self, data_directory, parser):
        self.data_directory = data_directory
        self.parser = parser

    def scan_for_files(self):
        file_list = [str(filename) for filename in os.listdir(self.data_directory)
                     if '.txt' in filename]
        temp_file_frame = pd.DataFrame(dict(file=file_list, processed=['no'] * len(file_list),
                                            log=['not processed'] * len(file_list)))
        if self.data_files is None:
            self.data_files = temp_file_frame
        else:
            temp_file_frame = temp_file_frame[temp_file_frame['file'] not in self.data_files['file'].values]
            self.data_files.append(temp_file_frame, ignore_index=True)


    def parse_data_files(self):
        for name in self.data_files.file.values:
            parser_class = self.parser(self.data_directory+name)
            parser_class.parse()

            self.data_files.loc[self.data_files['file']==name, 'log'] = parser_class.status_message
            print(self.data_files.head())


    def compare_data_files(self):
        for name in self.data_files.file.values:
            parser_1 = self.parser(self.data_directory+name)
            parser_1.parse()
            parser_1.dataframe = parser_1.dataframe[[Packet.LLC_COUNT.field_name, Packet.FUNCTION.field_name]]
            parser_1.dataframe.drop_duplicates(inplace=True)
            for second_name in self.data_files.file.values:
                if second_name != name:
                    parser_2 = self.parser(self.data_directory+second_name)
                    parser_2.parse()
                    parser_2.dataframe = parser_1.dataframe[[Packet.LLC_COUNT.field_name, Packet.FUNCTION.field_name]]
                    parser_2.dataframe.drop_duplicates(inplace=True)

                    if parser_1.dataframe[Packet.FUNCTION.field_name].equals(parser_2.dataframe[Packet.FUNCTION.field_name]):
                        parser_1.different_to_n_dataframes += 1

            if parser_1.different_to_n_dataframes > 1 and len(self.data_files.file.values) < 3:
                # There are only two files, so
                status_message = f'{Packet.LLC_COUNT.field_name} vs {Packet.FUNCTION.field_name} ' \
                                 f'differs from the other file.'
            elif parser_1.different_to_n_dataframes > 1:
                status_message = f'{Packet.LLC_COUNT.field_name} vs {Packet.FUNCTION.field_name} ' \
                                 f'differs from more than one other file.'
            else:
                status_message = ''

            self.data_files.loc[self.data_files['file'] == name, 'log'] = self.data_files['log'] + \
                                                                          f'\n{status_message}'

    def save_session_data(self):
        self.data_files.to_feather(self.data_directory + 'sessionfilenames')

    def load_session_data(self):
        self.data_files = pd.read_feather(self.data_directory + 'sessionfilenames')
