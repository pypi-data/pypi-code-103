# -*- coding: utf-8 -*-
'''
@File  : uuid.py
@Author: Jike Data Analysis Modeling Group
@Date  : 2021/12/4 12:17 上午
@Desc  : 人群包提取
'''

import pandas
import time
import pyspark.sql.functions as F

from pyspark.sql import Window

from jklwcs.spark import spark_1
from jklwcs.table import *
from jklwcs.osspath import *
from jklwcs.udff import get_package_name, get_category
from jklwcs.func import tran_business_hours,get_logger



class SelectUuid(object):
    """ 基础数据包查询类"""

    def __int__(self):
        pass

    def select_uuid_from_arrvied_data(
        self,
        poi_id_list,
        date_list,
        business_hours=None,
        non_business_hours=None,
        employee_days=None,
        stay_min=None,
        result_name=None,
        result_path=M_CROWD_PACK_RESULT_PATH,
        temp_result=M_CROWD_PACK_TEMP_PATH,
        arrvied_table=POI_ARRIVED_LOCATION_TABLE,
        leave_table=POI_LEAVE_EVENT_TABLE,
        poi_table=POI_TABLE,
        poi_categories_table=POI_CATEGOIRES_TABLE,
    ):
        """
        根据指定poi_id列表和时间范围查询uuid人群包,M1
        :param poi_id_list: poi_id列表
        :param date_list: 日期列表
        :param business_hours: 营业时间段
        :param non_business_hours: 非营业时间段
        :param employee_days: 员工天数判定
        :param stay_min: 驻留时间长
        :param result_name: 输出文件名
        :param result_path: 输出路径
        :param arrvied_table: poi到访表
        :param leave_table: poi离店表
        :param poi_table: poi属性表
        :param poi_categories_table: poi分类表
        :return:dataframe,[UUID，POIID，POI名称，开始时间，结束时间，驻留时长，开始小时，周几，对应节假日，POI一二三级分类]
        """
        logger = get_logger(result_name)
        date_range = pandas.date_range(start=date_list[0], end=date_list[1]).format()

        # 查询poi分类表和poi属性表,创建poi视图
        df_categories = spark_1.sql(f"""select c_id,c_name from {poi_categories_table}""").toPandas()
        c_id_categories_map = str({c_id: c_name for c_id, c_name in zip(df_categories.c_id, df_categories.c_name)})
        if len(poi_id_list) > 1:
            df_poi = spark_1.sql(
                f"""select p_id,p_name,p_encryption_id,p_category_list from {poi_table} where p_id in {tuple(poi_id_list)}""")
        else:
            df_poi = spark_1.sql(
                f"""select p_id,p_name,p_encryption_id,p_category_list from {poi_table} where p_id={poi_id_list[0]}""")
        df_poi \
            .withColumn('fisrt_c_name',
                        F.split(get_category(F.col('p_category_list'), F.lit(c_id_categories_map)), '_')[0]) \
            .withColumn('second_c_name',
                        F.split(get_category(F.col('p_category_list'), F.lit(c_id_categories_map)), '_')[1]) \
            .withColumn('third_c_name',
                        F.split(get_category(F.col('p_category_list'), F.lit(c_id_categories_map)), '_')[2]) \
            .select('p_id', 'p_name', 'p_encryption_id', 'fisrt_c_name', 'second_c_name', 'third_c_name') \
            .createOrReplaceTempView('poi_view')

        # 查询指定date_list数据
        for date in date_range:
            start_time = int(time.time())
            # 查询poi到访数据,创建arrvie视图
            sql_arrive = f"""
                select a.uuid,a.poi_id,a.create_time as timestamp ,a.date_str,a.num,
                b.fisrt_c_name,b.second_c_name,b.third_c_name,b.p_name as poi_name
                from (select c.*
                from (select uuid,poi_id,create_time,
                from_unixtime(cast(create_time as bigint) div 1000, 'yyyy-MM-dd') as date_str,
                row_number() over(partition by uuid,poi_id,from_unixtime(cast(create_time as bigint) div 1000, 'yyyy-MM-dd') order by create_time) as num
                from {arrvied_table}
                where date_str='{date}'
                and record_code in (0, 20112)
                and api_name='getSceneByAp'
                and environment='prod') c
                where c.num = 1) a
                inner join poi_view b
                on a.poi_id = b.p_id
                """
            spark_1 \
                .sql(sql_arrive) \
                .drop_duplicates(subset=['uuid', 'poi_id', 'date_str', 'num']) \
                .select("uuid", "poi_id", "poi_name", "date_str", "timestamp", 'fisrt_c_name', 'second_c_name',
                        'third_c_name') \
                .createOrReplaceTempView('df_arrive_view')

            # 查询poi离店数据,创建leave视图
            sql_leave = f"""
                select a.uuid, a.date_str,a.timestamp,a.num,
                b.p_name as poi_name,b.fisrt_c_name,b.second_c_name,b.third_c_name,b.p_id as poi_id
                from (select c.*
                from (select uuid, poi_id,timestamp,
                from_unixtime(cast(timestamp as bigint)/1000,'yyyy-MM-dd') as date_str,
                row_number() over(partition by uuid,poi_id,from_unixtime(cast(timestamp as bigint)/1000,'yyyy-MM-dd') order by timestamp desc) as num
                from {leave_table}
                where date_str='{date}') c
                where c.num = 1) a
                inner join poi_view b
                on a.poi_id=b.p_encryption_id
                """
            spark_1 \
                .sql(sql_leave) \
                .drop_duplicates(subset=['uuid', 'poi_id', 'date_str', 'num']) \
                .select("uuid", "poi_id", "poi_name", "date_str", "timestamp", 'fisrt_c_name', 'second_c_name',
                        'third_c_name') \
                .createOrReplaceTempView('df_leave_view')

            # 合并到访与离店数据
            sql_arrive_leave = f"""
                select a.uuid,a.poi_id,a.poi_name,a.timestamp as start_time,b.timestamp as end_time,
                from_unixtime(cast(a.timestamp as bigint) div 1000, 'yyyy-MM-dd HH:mm:ss') as start_time_format,
                from_unixtime(cast(b.timestamp as bigint) div 1000, 'yyyy-MM-dd HH:mm:ss') as end_time_format,
                a.fisrt_c_name,a.second_c_name,a.third_c_name,a.date_str
                from df_arrive_view a
                inner join df_leave_view b
                on a.uuid = b.uuid
                and a.poi_id = b.poi_id
                and a.date_str = b.date_str
                and a.timestamp < b.timestamp
            """
            spark_1 \
                .sql(sql_arrive_leave) \
                .withColumn('stay_min', F.round((F.col('end_time') - F.col('start_time')) / 1000 / 60, 4)) \
                .withColumn('start_hour', F.hour('start_time_format')) \
                .withColumn('day_of_week',
                            F.when(F.dayofweek('date_str') == 1, 7).otherwise(F.dayofweek('date_str') - 1)) \
                .write \
                .mode("append") \
                .option("header", "true") \
                .partitionBy("date_str") \
                .parquet(temp_result + result_name)
            logger.info(f'M1 select task : name:{result_name},date:{date},spend:{time.time() - start_time}s')

        df_arrive_levae = spark_1.read.option("header", "true").parquet(temp_result + result_name)
        logger.info('M1 filter task ...')
        # 过滤
        if business_hours:
            business_hours_list = tran_business_hours(business_hours)
            df_arrive_levae = df_arrive_levae[F.col('start_hour').isin(business_hours_list)]

        if non_business_hours:
            non_business_hours_list = tran_business_hours(non_business_hours)
            df_arrive_levae = df_arrive_levae[F.col('start_hour').isin(non_business_hours_list) == False]

        if employee_days:
            df_arrive_levae_filter_employee = df_arrive_levae.groupby('uuid', 'poi_id').agg(F.countDistinct(
                'date_str').alias('days')).filter(f'days <= {employee_days[1]} and days >= {employee_days[0]}').select(
                'uuid')
            df_arrive_levae = df_arrive_levae.join(df_arrive_levae_filter_employee, 'uuid', 'inner')

        if stay_min:
            df_arrive_levae = df_arrive_levae.filter(f'stay_min >= {stay_min[0]} and stay_min <= {stay_min[1]} ')

        df_arrive_levae.sort('start_time') \
            .repartition(1) \
            .write \
            .mode("append") \
            .option("header", "true") \
            .csv(result_path + result_name)
        logger.info(f'M1 task successed : {result_name}')

    def select_uuid_from_arrivate_and_stable_data(self,
                                                  poi_id_list,
                                                  date_list,
                                                  business_hours=None,
                                                  days_of_month=None,
                                                  short_time=None,
                                                  long_time=None,
                                                  non_business_hours=None,
                                                  city_id_list=None,
                                                  other_date_list=None):
        """
        根据指定poi_id列表和时间范围查询uuid人群包
        :param poi_id_list: poi_id列表,eg.[1234，2234]
        :param date_list: 日期列表,eg.['2021-01-01','2021-06-01']
        :param business_hours: 营业时间段
        :param days_of_month: 员工人天,eg.15/30,30天内有15天出现了
        :param short_time: 驻留过段时长
        :param long_time: 驻留过长时长
        :param non_business_hours: 非营业时间段
        :param city_id_list: 城市id列表,eg.[1,2,3]
        :param other_date_list: UUID其他场景到访的日期区间,eg.['2021-01-01','2021-06-01']
        :return:dataframe,[UUID，POIID，POI名称，开始时间，结束时间，驻留时长，开始小时，周几，对应节假日，POI一二三级分类]
        """
        pass
