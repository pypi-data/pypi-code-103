#! /usr/bin/env python3
"""
@author  : MG
@Time    : 2021/10/11 13:53
@File    : import_save_failed.py
@contact : mmmaaaggg@163.com
@desc    : 用于
"""
import json
import logging
import os

from vnpy_extra.db.orm import StrategyBacktestStats


def import_save_failed_by_dir(folder_path: str):
    """将 save_failed 目录下的json文件导入数据库"""
    logger = logging.getLogger(__name__)
    for num, file_name in enumerate(os.listdir(folder_path), start=1):
        json_file_path = os.path.join(folder_path, file_name)
        with open(json_file_path, encoding='utf-8', ) as fp:
            kwargs: dict = json.load(fp)

        StrategyBacktestStats.update_stats(**kwargs)
        logger.info(f"{num:2d}) strategy_settings={kwargs['strategy_settings']} 保存完成")


def run_import_save_failed_by_dir():
    folder_path = r"C:\github\quant_vnpy\strategies\half_arbitrage\lv_transfer_lm03\output\save_failed"
    import_save_failed_by_dir(folder_path)


if __name__ == "__main__":
    run_import_save_failed_by_dir()
