import numpy as np
import pandas as pd


def convert_dict_to_df(data, columns) -> pd.DataFrame:
    if data:
        df = pd.DataFrame(np.array(data), columns=columns)
        if not df.empty:
            df = df.convert_dtypes()
    else:
        df = pd.DataFrame([], columns=columns)
    return df


def convert_content_data_to_df(input_data: dict):
    headers_names = [header["name"] for header in input_data["headers"]]
    data = input_data["data"]
    return convert_dict_to_df(data, headers_names)
