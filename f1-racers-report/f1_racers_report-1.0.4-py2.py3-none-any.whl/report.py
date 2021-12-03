import argparse
import os
import datetime
import colorama
import pkg_resources


def create_parser():
    """
    Initializes parser
    :return: parser object
    """
    parser = argparse.ArgumentParser(
        description='application that allows you to obtain list of best racers according lap time')
    parser.add_argument('--files', type=str, help='path to the folder where info files are located')
    parser.add_argument('--asc', default='asc', help='ascending order')
    parser.add_argument('--desc', help='descending order')
    parser.add_argument('--driver', help='name of the driver statistics of which you want to obtain')

    return parser


def create_abbr_dict(file):
    """
    Creates a dictionary with abbreviation explanations for each driver

    :param file: where explanations should be found
    :return: dictionary with abbreviation-explanation pair
    """
    abbreviation_dict = {}

    with open(file, encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            splitted = line.split('_')
            abbreviation_dict[splitted[0]] = (splitted[1], splitted[2])

    return abbreviation_dict


def get_time_info(time_file) -> dict:
    """
    Generates a time of a lap from the provided file

    :param time_file: file where either start or end time of the lap should be found
    :return: information about lap time
    """
    time_info = {}

    with open(time_file) as f:
        for log in f:
            log = log.strip()
            try:
                if log:
                    time_info[log[:3]] = datetime.datetime.strptime(log[3:], '%Y-%m-%d_%I:%M:%S.%f')
                else:
                    continue
            except ValueError:
                raise ValueError('Format of the time in the provided data is not correct')

    return time_info


def build_report(start_time_file, end_time_file, abbr_info, driver, reverse) -> dict:
    """
    Creates a report regarding the best lap time of each racer

    :param start_time_file: file with the lap start time
    :param end_time_file: file with lap finish time
    :param driver: name of the driver
    :param abbr_info: file with abbreviations explanations
    :param reverse: order in which list of drivers should be sorted
    :return: sorted report of the best lap time of each racer
    """
    start_time_info = get_time_info(start_time_file)
    end_time_info = get_time_info(end_time_file)
    best_lap_time = {}

    for abbr in end_time_info:
        best_lap_time[abbr_info[abbr][0]] = [abbr, end_time_info[abbr] - start_time_info[abbr]]

    best_lap_time = {k: v for k, v in sorted(best_lap_time.items(), key=lambda item: item[1][1])}

    for index, (key, value) in enumerate(best_lap_time.items(), 1):
        value.append(index)

    if reverse == 'desc':
        best_lap_time = dict(reversed(list(best_lap_time.items())))

    if driver:
        if driver in best_lap_time:
            return {driver: best_lap_time[driver]}
        else:
            return {}
    else:
        return best_lap_time


def print_report(sorted_report, abbr_info):
    """
    Displays the report in the command line

    :param sorted_report: report to display
    :param abbr_info: dict with explanations of acronyms
    """

    print(colorama.Fore.BLUE + '{0}  {1:17} | {2:25} | {3}'.format('№', 'FULL NAME', 'CAR MODEL', 'TIME'))
    print(colorama.Fore.BLUE + '_' * 60)

    for name, record in sorted_report.items():
        print(colorama.Fore.BLUE +
              '{0:0}. {1:17} | {2:25} | {3}'.format(record[2], name, abbr_info[record[0]][1],
                                                    str(record[1])))
        if record[2] == 15:
            print(colorama.Fore.BLUE + '_' * 60)

    if len(sorted_report) == 0:
        print(colorama.Back.RED + colorama.Fore.BLACK + 'Record was not found, please type a valid name')


def check_files(path: str, *args) -> list:
    """
    Validates whether provided directory and files in it exist

    :param path: path to the directory where required files should be gathered
    :param args: names of the files from where data should be taken
    :return: list of absolute paths to required files
    """
    checked = []

    if os.path.exists(path):
        for file in args:
            joined = os.path.join(path, file)
            if os.path.exists(os.path.join(path, file)):
                checked.append(joined)
            else:
                print(
                    colorama.Back.RED + colorama.Fore.BLACK + f'File "{file}" doesn\'t exist in the provided directory')
                exit()
    else:
        print(colorama.Back.RED + colorama.Fore.BLACK + 'Directory that you provided doesn\'t exist')
        exit()

    return checked


def main():
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    file_names = ['start.log', 'end.log', 'abbreviations.txt']
    colorama.init(autoreset=True)
    args = create_parser().parse_args()
    order = args.desc or args.asc

    if args.files:
        start_file, end_file, abbr_file = check_files(args.files, *file_names)
    else:
        start_file = pkg_resources.resource_filename(__name__, "data/start.log")
        end_file = pkg_resources.resource_filename(__name__, "data/start.log")
        abbr_file = pkg_resources.resource_filename(__name__, "data/abbreviations.txt")

    abbreviations = create_abbr_dict(abbr_file)
    report = build_report(start_file, end_file, abbreviations, driver=args.driver, reverse=order)
    print_report(report, abbreviations)


if __name__ == '__main__':
    main()
