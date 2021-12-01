import gc

import numpy as np
import pandas as pd
import pyspark
from spark_gaps_date_rorc_tools.utils.config import load_config
from spark_gaps_date_rorc_tools.utils.dataframe import show_spark_df
from spark_gaps_date_rorc_tools.utils.dataframe import show_pd_df


def show_gaps_date(spark=None,
                   config_path_name=None,
                   hdfs_uri=None,
                   table_rorc=None,
                   filter_date_initial="202101",
                   filter_date_final="202112"):
    if not config_path_name:
        raise Exception(f'require file .yaml: {config_path_name} ')

    if not spark:
        raise Exception(f'require object: {spark} ')

    if not hdfs_uri:
        raise Exception(f'require hdfs_uri: {hdfs_uri} ')

    if not filter_date_initial:
        raise Exception(f'require filter_date_initial: {filter_date_initial} ')

    if not filter_date_final:
        raise Exception(f'require filter_date_final: {filter_date_final} ')

    sc = spark.sparkContext
    URI = sc._gateway.jvm.java.net.URI
    Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
    FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
    Configuration = sc._gateway.jvm.org.apache.hadoop.conf.Configuration
    fs = FileSystem.get(URI(f"{hdfs_uri}"), Configuration())

    data = load_config(path_name=f"{config_path_name}")
    conf_table_job_dict = data["conf-rorc"]

    pyspark.sql.dataframe.DataFrame.show2 = show_spark_df
    pd.DataFrame.show2 = show_pd_df

    if table_rorc in ("", None):
        table_list = [key for key, value in conf_table_job_dict.items()]
    else:
        table_list = [key for key, value in conf_table_job_dict.items() if key in table_rorc]

    global df_detail
    global df_detail2

    for ind, table in enumerate(table_list):
        table_cdd_dict = data["conf-rorc"][table]
        table_rorc_path = str(table_cdd_dict["table_path"])
        table_supplies_list = table_cdd_dict["supplies"]

        for index, table_supplies_path in enumerate(table_supplies_list):

            try:
                hdfs_files = fs.listStatus(Path(f'{table_supplies_path}'))

                date_list = list()
                for hdfs_file in hdfs_files:
                    supplies_input_dict = dict(table_principal="", table_principal_path="",
                                               table_supplies_path="", partition_date="")
                    hdfs_file_supplies = str(hdfs_file.getPath())

                    table_supplies_partition = str(hdfs_file_supplies.split("/")[-1]).lower()
                    table_supplies_partition = table_supplies_partition.split("=")

                    if len(table_supplies_partition) == 2:
                        _partition_date = str(table_supplies_partition[1])

                        supplies_input_dict["table_principal"] = table
                        supplies_input_dict["table_principal_path"] = table_rorc_path
                        supplies_input_dict["table_supplies_path"] = table_supplies_path
                        supplies_input_dict["partition_date"] = _partition_date
                        date_list.append(supplies_input_dict)

                df = pd.DataFrame(date_list)
                df["partition_date"] = pd.to_datetime(df['partition_date'])
                df["year_month"] = df["partition_date"].dt.strftime('%Y%m')

                df = df[df['year_month'].between(filter_date_initial, filter_date_final)]

                df2 = df.groupby(["table_principal", "table_principal_path", "table_supplies_path", "year_month"]) \
                    .agg(max_partition_date=("partition_date", np.max),
                         count_partition_date=("partition_date", np.size)) \
                    .reset_index()
                df2["max_month_day"] = df2["max_partition_date"].dt.strftime('%d')
                df2["max_month_day"] = df2["max_month_day"].apply(lambda x: int(x))

            except:
                date_list = list()
                supplies_input_dict = dict()
                supplies_input_dict["table_principal"] = table
                supplies_input_dict["table_principal_path"] = table_rorc_path
                supplies_input_dict["table_supplies_path"] = table_supplies_path
                date_list.append(supplies_input_dict)
                df2 = pd.DataFrame(date_list)
                df2["year_month"] = filter_date_initial
                df2["max_partition_date"] = pd.to_datetime(filter_date_initial, format="%Y%m", dayfirst=True)
                df2["count_partition_date"] = 0
                df2["max_month_day"] = 0

            if index == 0:
                df_detail = df2.copy()
            else:
                df_detail = pd.concat([df2, df_detail], ignore_index=True)

        if ind == 0:
            df_detail2 = df_detail.copy()
        else:
            df_detail2 = pd.concat([df_detail, df_detail2], ignore_index=True)

    df_pivot = pd.pivot_table(data=df_detail2,
                              index=["table_principal", "table_supplies_path"],
                              columns="year_month",
                              values="max_month_day",
                              aggfunc=[np.max])
    df_pivot.columns = [f'P_{str(j).upper()}' for i, j in df_pivot.columns]
    df_pivot = df_pivot.reset_index().fillna(0)

    new_df = spark.createDataFrame(df_pivot)
    del df_pivot, df_detail2
    gc.collect()

    return new_df
