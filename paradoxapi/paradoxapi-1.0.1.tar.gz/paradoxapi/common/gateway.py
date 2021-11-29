#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:HDD
import sys, os

path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from com.datacommon import *
from com.sqlhandle import *
from com.setting import *
from com.pld_data_com import *
from com.tips_data_common import *

def get_balance_sheet_fore_annual(codes, start=None, end=None, fields=None):
    # balance_sheet_fore_annual 年度资产负债表预测表
    # 记录ai预测的上市公司资产负债表的年度数据（适用于一般工商的预测模型）
    if start is None and end is None:
        return LOSS_START_END_TIPS
    # a_fields = '*' if fields is None else ','.join(fields)
    # start_str = "and PERIOD_DATE > '{}'".format(start) if start is not None else ''
    # end_str = "and PERIOD_DATE < '{}'".format(end) if end is not None else ''
    # dt_str = start_str + end_str
    a_fields, dt_str = her_annual_tb_fields_handle(start, end, fields)
    bsfa_sql_ = "select {} from hermes.balance_sheet_fore_annual where TICKER in ('{}') {}".format(
        a_fields, "','".join(codes), dt_str)
    print('sql:{}'.format(bsfa_sql_))
    return get_her_data(sql=bsfa_sql_, cols=fields)

def get_cash_flow_statement_fore_annual(codes, start, end, fields=None):
    # cash_flow_statement_fore_annual 年度现金流量表预测表
    # 记录ai预测的上市公司现金流量表的年度数据（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'cash_flow_statement_fore_annual'
    a_fields = '*' if fields is None else ','.join(fields)

def get_finance_ratio_fore_annual(codes, start, end, fields=None):
    # finance_ratio_fore_annual 年度财务衍生指标预测表
    # 记录ai预测的上市公司财务分析的年度数据（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'finance_ratio_fore_annual'
    a_fields = '*' if fields is None else ','.join(fields)

def get_financial_summary_fore_annual(codes, start, end, fields=None):
    # financial_summary_fore_annual  年度财务摘要预测表
    # 记录ai预测的上市公司财务摘要的年度数据（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'financial_summary_fore_annual'
    a_fields = '*' if fields is None else ','.join(fields)

def get_financial_summary_fore_quarter(codes, start, end, fields=None):
    # financial_summary_fore_quarter  季度财务摘要预测表
    # 记录ai预测的上市公司季度财务摘要（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'financial_summary_fore_quarter'
    a_fields = '*' if fields is None else ','.join(fields)

def get_income_statement_fore_annual(codes, start, end, fields=None):
    # income_statement_fore_annual  年度利润表预测表
    # 记录ai预测的上市公司年度利润数据（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'income_statement_fore_annual'
    a_fields = '*' if fields is None else ','.join(fields)

def get_income_statement_fore_quarter(codes, start, end, fields=None):
    # income_statement_fore_quarter  季度利润表预测表
    # 记录ai预测的上市公司季度利润数据（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'income_statement_fore_quarter'
    a_fields = '*' if fields is None else ','.join(fields)

def get_revenue_forecast_annual(codes, start, end, fields=None):
    # 	revenue_forecast_annual  年度营收预测表
    # 记录上市公司年度营收预测数据（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'revenue_forecast_annual'
    a_fields = '*' if fields is None else ','.join(fields)

def get_revenue_forecast_quarter(codes, start, end, fields=None):
    # revenue_forecast_quarter  季度营收预测表
    # 记录上市公司季度营收预测数据（适用于一般工商的预测模型）
    db_name = 'hermes'
    table_name = 'revenue_forecast_quarter'
    a_fields = '*' if fields is None else ','.join(fields)

if __name__ == '__main__':
    env = 'pro'
    mysql_dic_filed = get_db(env)
    plddb = HandleMysql(**mysql_dic_filed)
