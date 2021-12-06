from prettytable import PrettyTable


def print_table_format(scan_results):
    table = PrettyTable()
    table.field_names = ['File', 'Line', 'Leak']
    table.align = "l"
    for result in scan_results:
        table.add_row(result)

    print(table)


def error(message):
    print('\x1b[1;37;41m ' + message + ' \033[0;0m')

def warning(message):
    print('\033[1;37;43m ' + message + ' \033[0;0m')

def success(message):
    print('\033[1;37;42m ' + message + ' \033[0;0m')


