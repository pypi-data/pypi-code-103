"""Author: Quinn Brittain"""

def read_csv_data(filename):
    """Reads data from a csv file into a dictionary of lists

    ### Args:
        filename : str
            Name of the file
    ### Returns:
        Type : dict{list[str]}
            The dict uses:
                'headers' for the list headers
                'rows' for the list of rows
    ### Raises:
        OSError
            If unable to open file

    >>> read_csv_data("")
    Traceback (most recent call last):
    FileNotFoundError: [Errno 2] No such file or directory: ''
    """
    with open(filename, 'r') as file:
        csv_reader = csv.reader(file)
        rows = []
        headers = next(csv_reader)
        for row in csv_reader:
            rows.append(row)
    return {'headers': headers, 'rows': rows}


def write_csv_data(filename, data):
    """Writes data from a dictionary of arrays into a csv file

    The required dictionary must use:
        'headers' for the array headers
        'rows' for the array of rows
    ### Args:
        filename : str
            Name of the file
        data : dict{list[str]}
            The dict uses:
                'headers' for the list headers
                'rows' for the list of rows
    ### Raises:
        OSError
            If unable to open file
        KeyError
            If missing 'headers' or 'rows' from dict
        FileNotFoundError
            If filename is invalid

    >>> write_csv_data("", {'':['']})
    Traceback (most recent call last):
    FileNotFoundError: [Errno 2] No such file or directory: ''
    """
    with open(filename, 'w', newline='') as file:
        csv_writer = csv.writer(file)
        csv_writer.writerow(data['headers'])
        csv_writer.writerows(data['rows'])
