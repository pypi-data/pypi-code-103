"""
@author  : MG
@Time    : 2021/1/19 16:16
@File    : strategy_stats.py
@contact : mmmaaaggg@163.com
@desc    : 用于更新策略统计表的状态
"""
import json
import logging
import os

import pandas as pd

from vnpy_extra.db.orm import StrategyBacktestStats, StrategyInfo

logger = logging.getLogger(__name__)


def update_strategy_stats_by_df(
        file_path,
        encoding="GBK",  # "utf-8-sig" 旧版本的数据是 utf-8 编码
        update_account_stg_mapping=False,
):
    """通过exce、csv文件更新策略状态"""
    _, ext = os.path.splitext(file_path)
    if ext == '.csv':
        df = pd.read_csv(file_path, encoding=encoding)
    else:
        df = pd.read_excel(file_path)

    if "short_name" not in df:
        df['short_name'] = ''

    if "shown_name" not in df:
        df['shown_name'] = ''

    df = df[['strategy_class_name', 'id_name', 'symbols', 'cross_limit_method', 'backtest_status',
             'short_name', 'shown_name']]
    # 历史版本有个bug，这里修正一下。以后可以删除这段代码
    df['strategy_class_name'] = df['strategy_class_name'].apply(lambda x: x.lstrip("('").rstrip("',)"))
    strategy_class_name = df['strategy_class_name'].iloc[0]
    symbols = df['symbols'].iloc[0]
    update_count = StrategyBacktestStats.update_backtest_status_bulk([
        {k: None if isinstance(v, str) and v == '' else v for k, v in record.items()}
        for record in df.to_dict('record')])
    logger.info("%s[%s] %d 条记录被更新", strategy_class_name, symbols, update_count)
    if update_account_stg_mapping:
        StrategyBacktestStats.add_mapping_all(
            strategy_class_name=strategy_class_name,
            symbols_info=symbols,
        )
    return update_count


def update_strategy_stats_by_dir(folder_path: str):
    """更新目录下所有 csv/xls/xlsx 文件"""
    for file_name in os.listdir(folder_path):
        try:
            _, ext = os.path.splitext(file_name)
            if ext not in ('.csv', '.xls', '.xlsx'):
                logger.warning(f'文件 {file_name} 无效')
                continue
            file_path = os.path.join(folder_path, file_name)
            update_strategy_stats_by_df(file_path, update_account_stg_mapping=True)
        except:
            logger.exception(f"处理 {file_name} 文件时发生异常")


def get_strategy_class_name_by_settings_file(setting_file_path) -> str:
    """通过 setting 文件获取 strategy_class_name"""
    with open(setting_file_path, 'r', encoding='utf-8') as f:
        return list(json.load(f).values())[0]["class_name"]


def get_backtest_status_info_by_images_in_output_stg_dir(folder_path: str):
    """根据目录结果获取策略信息"""
    _, strategy_class_name = os.path.split(folder_path)
    stg_info = StrategyInfo.get_instance_by_strategy_class_name(strategy_class_name)
    if stg_info is None:
        strategy_class_name = None

    for vt_symbol in os.listdir(folder_path):
        symbol_str = vt_symbol.split('.')[0]
        vt_symbol_path = os.path.join(folder_path, vt_symbol)
        if not os.path.isdir(vt_symbol_path):
            continue
        for cross_limit_method in os.listdir(vt_symbol_path):
            cross_limit_method_path = os.path.join(vt_symbol_path, cross_limit_method)
            images_path = os.path.join(cross_limit_method_path, 'images')
            if not os.path.isdir(images_path):
                continue
            for backtest_status in os.listdir(images_path):
                backtest_status_path = os.path.join(images_path, backtest_status)
                if not os.path.isdir(backtest_status_path):
                    continue
                try:
                    backtest_status_int = int(backtest_status)
                except ValueError:
                    logger.error(f"{backtest_status} 不是有效的状态。{images_path}")
                    continue
                for id_name_png in os.listdir(backtest_status_path):
                    id_name_png_path = os.path.join(backtest_status_path, id_name_png)
                    if not os.path.isfile(id_name_png_path):
                        continue
                    id_name, ext = os.path.splitext(id_name_png)
                    if strategy_class_name is None:
                        setting_file_path = os.path.join(cross_limit_method_path, 'setting', f"{id_name}_setting.json")
                        _strategy_class_name = get_strategy_class_name_by_settings_file(setting_file_path)
                    else:
                        _strategy_class_name = strategy_class_name

                    if id_name.endswith(symbol_str):
                        # file_name_include_symbol == True 时，文件名结尾将会带有 _symbol 因此需要去除
                        id_name = id_name[:-len(symbol_str) - 1]

                    yield {
                        "strategy_class_name": _strategy_class_name,
                        "symbols": vt_symbol,
                        "cross_limit_method": cross_limit_method,
                        "backtest_status": backtest_status_int,
                        "id_name": id_name,
                    }


def update_strategy_stats_by_images_in_output_stg_dir(folder_path: str, update_account_stg_mapping=False):
    """通过指定 output/strategy_name 目录，程序自动根据其中的 images 目录进行策略状态更新"""
    data_dic_list = list(get_backtest_status_info_by_images_in_output_stg_dir(folder_path))
    if len(data_dic_list) == 0:
        logger.info(f"没有数据记录可更新：{folder_path}")
        return
    strategy_class_name = data_dic_list[0]['strategy_class_name']
    update_count = StrategyBacktestStats.update_backtest_status_bulk(data_dic_list)
    if update_count > 0:
        logger.info(f"{strategy_class_name} {update_count}/{len(data_dic_list)} 条记录记录被更新")
        if update_account_stg_mapping:
            StrategyBacktestStats.add_mapping_all(strategy_class_name=strategy_class_name)

    else:
        logger.info(f"更新：{strategy_class_name} 0 条状态记录")

    return update_count


def run_update_strategy_stats_by_images_in_output_stg_dir():
    folder_path = r'c:\github\quant_vnpy\strategies\trandition\period_resonance\pr_2021_04_02_two_signals\reports\RsiMacdPr20210402And'
    update_strategy_stats_by_images_in_output_stg_dir(folder_path)


def run_update_strategy_stats_by_df():
    folder_path = r'd:\github\quant_vnpy\strategies\spread\main_secondary\reports\output\bulk_backtest_2021-04-04'
    file_name = 'PTReversionWithAlgoTradingStrategy_CJ9999.CZCE_CJ8888.CZCE_0_0.5_open_price_2021-04-04.xlsx'
    file_path = os.path.join(folder_path, file_name)
    update_strategy_stats_by_df(file_path, update_account_stg_mapping=True)


if __name__ == "__main__":
    # run_update_strategy_stats_by_df()
    run_update_strategy_stats_by_images_in_output_stg_dir()
