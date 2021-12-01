from pathlib import Path
import pandas as pd

current_meta_df = pd.DataFrame()
current_data_df = pd.DataFrame()

def process_acs():
    here = Path(__file__).parent.resolve()
    cbg_b01 = Path(here / "data/cbg_b01.csv")
    meta    = (here / "data/cbg_field_descriptions.csv")

    global current_meta_df
    global current_data_df
    current_meta_df = pd.read_csv(str(meta))
    current_data_df = pd.read_csv(str(cbg_b01))

    def drop_unneeded_columns():
        global current_meta_df
        global current_data_df
        # Find margin of errors
        drop_marginoferror_df = current_meta_df[current_meta_df["field_level_1"] == "MarginOfError"]
        drop_marginoferror_ls = list(drop_marginoferror_df["table_id"])
        keep_meta_df = current_meta_df[current_meta_df["field_level_1"] != "MarginOfError"]


        # Drop margin of error, axis=1 drop columns, axis=0 drop rows, axis=0 is default mode
        # alternatively, axis='rows' or axis'columns' is the same as axis=0 or axis=1, respectively
        thisFilter = current_data_df.filter(drop_marginoferror_ls)
        current_data_df.drop(thisFilter, inplace=True, axis=1)


        # Display this to see unique fields in the meta file
        unique_meta_df = current_meta_df.apply(lambda col: col.unique())
        # unique_meta_df["field_level_4"]

        current_meta_df = keep_meta_df

    def rename_columns():
        global current_meta_df
        global current_data_df
        tmp_df = current_meta_df[current_meta_df.table_id.isin(list(current_data_df.columns))].copy()
        tmp_missing_df = current_meta_df[~current_meta_df.table_id.isin(list(current_data_df.columns))]
        tmp_df.fillna('', inplace=True)
        t = tmp_df[["field_level_2", "field_level_3", "field_level_4", "field_level_5", "field_level_6"]]
        newlabels_list = list(
            t["field_level_2"] + " " + t["field_level_3"] + " " + t["field_level_4"] + " " + t["field_level_5"] + " " +
            t["field_level_6"])

        newlabels_list = [x.strip() for x in newlabels_list]
        newlabels_list = [x.strip('"') for x in newlabels_list]
        newlabels_list = [x.replace(',', "") for x in newlabels_list]
        newlabels_list = [x.replace(")", "") for x in newlabels_list]
        newlabels_list = [x.replace("(", "") for x in newlabels_list]
        newlabels_list = [x.replace(" ", "_") for x in newlabels_list]
        tmp_list = list(tmp_df.table_id)
        newlabels_dict = dict(zip(tmp_list, newlabels_list))

        current_data_df.rename(columns=newlabels_dict, inplace=True)

    drop_unneeded_columns()
    rename_columns()
    return current_data_df

process_acs()
