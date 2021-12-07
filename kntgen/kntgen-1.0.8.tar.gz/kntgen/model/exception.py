class DefinedErrorMessage:
    ERROR_SUPPORT_TEMPLATE = 'Currently we are just supporting ' \
                             '[bloc/model/network/ui] template!'
    ERROR_SUPPORT_SOURCE_INPUT = 'Currently we are just supporting ' \
                                 '[pasteboard] and [file path]!'
    ERROR_SUPPORT_FORMAT = 'Currently we are just supporting ' \
                           '[json] and [yaml] format!'
    ERROR_SUPPORT_COMPONENT = 'Currently we are just supporting ' \
                              '[image/string/color/widget] component!'
    FILE_NOT_FOUND = '❌  File not found ❌ '

    @staticmethod
    def print_error(e: any):
        print(f'❌  Occurs an error - {str(e)} ❌ ')
