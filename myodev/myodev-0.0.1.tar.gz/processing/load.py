"""
Processing - Load
=================

Load the signal in a readable format.

AUTHOR
    Itokiana Rafidinarivo, itokiana.rafidinarivo@edu.esiee.fr

LAST MODIFIED
    Wed. 01 Dec. 2021
"""

# External packages
import typing  # functions
import numpy as np  # vector operations
import pandas as pd  # data analysis & manipulation
import sys


def get_file_content(filepath: str) -> typing.Union[None, pd.DataFrame]:
    """
    Get the content of a given file from its path.

    Parameters
    ----------
        filepath (str) path to the file

    Returns
    -------
        (pandas.DataFrame) file content
    """
    content = None

    try:
        # Get the content
        values = np.loadtxt(filepath)

        # Transform to pandas.DataFrame
        columns = ["nSeq", "I1", "I2", "O1", "O2", "A1"]
        content = pd.DataFrame(values, columns=columns)

    # Error either caused by the file not existing or
    # number of columns
    except Exception as e:
        raise e

    return content


# Main script
if __name__ == "__main__":
    # Package for doctest running
    import doctest

    # Launch tests and get results
    no_failures, no_tests = doctest.testmod()

    # Print results
    print(f"No. failures  : {no_failures}")
    print(f"No. successes : {no_tests - no_failures}")
    print(f"No. tests     : {no_tests}")

    # Check
    assert no_failures == 0
