
import sys
sys.path.append("..")
from fml.data import read_data

def test_read_data_():
    dataset = read_data("data.xlsx")
