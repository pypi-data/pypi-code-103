import io
import sys
import base64
import pandas as pd

from mitosheet.sheet_functions.types.utils import get_string_columns

def get_dataframe_as_excel(event, steps_manager):
    """
    Sends a dataframe as a excel string.
    """
    sheet_index = event['sheet_index']
    df: pd.DataFrame = steps_manager.dfs[sheet_index]

    # We write to a buffer so that we don't have to save the file
    # to the file system for no reason
    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        df.to_excel(writer, index=False)
    
    # Go back to the start of the buffer
    buffer.seek(0)
    
    # First, we take the buffer, and base64 encode it in bytes,
    # and then we covert this to ASCII. On the front-end, we 
    # turn it back into base64, then back to bytes, before 
    # creating a Blob out of it
    return base64.b64encode(buffer.read()).decode('ascii')