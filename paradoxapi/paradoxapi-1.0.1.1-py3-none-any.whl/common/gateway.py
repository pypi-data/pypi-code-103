#!/usr/bin/env python
# -*- coding:utf-8 -*-
# Author:HDD
import sys, os
path = os.path.abspath(os.path.dirname(__file__))
sys.path.append(path)

from com.pld_data_com import *
from com.tips_data_common import *

def get_balance_sheet_fore_annual(codes, start=None, end=None, fields=None):
    # balance_sheet_fore_annual 年度资产负债表预测表
    # 记录ai预测的上市公司资产负债表的年度数据（适用于一般工商的预测模型）
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, 'balance_sheet_fore_annual', start, end, fields), cols=AN_BSFA_COLS)

def get_cash_flow_statement_fore_annual(codes, start=None, end=None, fields=None):
    # cash_flow_statement_fore_annual 年度现金流量表预测表
    # 记录ai预测的上市公司现金流量表的年度数据（适用于一般工商的预测模型）
    if start is None and end is None:
        return LOSS_START_END_TIPS
    table_name = 'cash_flow_statement_fore_annual'
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_CFSA_COLS)

def get_finance_ratio_fore_annual(codes, start=None, end=None, fields=None):
    # finance_ratio_fore_annual 年度财务衍生指标预测表
    # 记录ai预测的上市公司财务分析的年度数据（适用于一般工商的预测模型）
    table_name = 'finance_ratio_fore_annual'
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_FRFAN_COLS)

def get_financial_summary_fore_annual(codes, start=None, end=None, fields=None):
    # financial_summary_fore_annual  年度财务摘要预测表
    # 记录ai预测的上市公司财务摘要的年度数据（适用于一般工商的预测模型）
    table_name = 'financial_summary_fore_annual'
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_FSFA_COLS)

def get_financial_summary_fore_quarter(codes, start=None, end=None, fields=None):
    # financial_summary_fore_quarter  季度财务摘要预测表
    # 记录ai预测的上市公司季度财务摘要（适用于一般工商的预测模型）
    table_name = 'financial_summary_fore_quarter'
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_FSFQ_COLS)

def get_income_statement_fore_annual(codes, start=None, end=None, fields=None):
    # income_statement_fore_annual  年度利润表预测表
    # 记录ai预测的上市公司年度利润数据（适用于一般工商的预测模型）
    table_name = 'income_statement_fore_annual'
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_ISFA_COLS)

def get_income_statement_fore_quarter(codes, start=None, end=None, fields=None):
    # income_statement_fore_quarter  季度利润表预测表
    # 记录ai预测的上市公司季度利润数据（适用于一般工商的预测模型）
    table_name = 'income_statement_fore_quarter'
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_ISFQ_COLS)

def get_revenue_forecast_annual(codes, start=None, end=None, fields=None):
    # revenue_forecast_annual  年度营收预测表
    # 记录上市公司年度营收预测数据（适用于一般工商的预测模型）
    table_name = 'revenue_forecast_annual'
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_RFA_COLS)

def get_revenue_forecast_quarter(codes, start=None, end=None, fields=None):
    # revenue_forecast_quarter  季度营收预测表
    # 记录上市公司季度营收预测数据（适用于一般工商的预测模型）
    table_name = 'revenue_forecast_quarter'
    if start is None and end is None:
        return LOSS_START_END_TIPS
    return get_her_data(sql=merge_sql_str(codes, table_name, start, end, fields), cols=AN_RFQ_COLS)

if __name__ == '__main__':
    env = 'pro'
    mysql_dic_filed = get_db(env)
    plddb = HandleMysql(**mysql_dic_filed)
