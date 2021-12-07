#  The MIT License (MIT)
#
#  Copyright (c) 2021. Scott Lau
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.

import logging
import os

import pandas as pd
from config42 import ConfigManager
from sc_analyzer_base import BaseSummaryDiffAnalyzer

from sc_diff_analysis.utils import MoneyUtils


class BranchSummaryGroupByItemTypeDiffAnalyzer(BaseSummaryDiffAnalyzer):
    """
    按差异类型分组进行机构汇总差异分析类
    """

    def __init__(self, *, config: ConfigManager, is_first_analyzer=False):
        super().__init__(config=config, is_first_analyzer=is_first_analyzer)

    def _read_config(self, *, config: ConfigManager):
        super()._read_config(config=config)
        # 选中需要处理的机构清单
        self._branch_selected_list = config.get("branch.selected_list")
        # 生成的Excel中Sheet的名称
        self._target_sheet_name = config.get("diff.branch_summary_group_by_item_type.target_sheet_name")
        # 指标名称列名称
        self._target_compare_item_column_name = config.get(
            "diff.branch_summary_group_by_item_type.target_compare_item_column_name")
        # 指标名称列名称
        self._target_compare_item_column_name_with_unit = self._target_compare_item_column_name + "(单位)"
        # Sheet名称
        self._sheet_name = config.get("diff.branch_summary_group_by_item_type.sheet_name")
        # 表头行索引
        self._header_row = config.get("diff.branch_summary_group_by_item_type.header_row")
        # 所属机构列名称（Excel中列名必须唯一）
        self._index_column_name = config.get("diff.branch_summary_group_by_item_type.branch_column_name")
        # 待分析差异列名称列表（Excel中列名必须唯一）
        diff_column_dict: dict = config.get("diff.branch_summary_group_by_item_type.diff_column_list")
        if diff_column_dict is not None and type(diff_column_dict) is dict:
            self._diff_column_dict.update(diff_column_dict)

    def _filter_origin_data(self, *, data):
        # 筛选指定部门，删除合计行
        data = data[data[self._index_column_name].isin(self._branch_selected_list)]
        # 按机构排序
        data = data.sort_values(
            by=[self._index_column_name],
            ascending=True
        )
        return data

    def _init_result_data_frame(self):
        # 所有列
        all_columns = list()
        # 指标名称带单位列
        all_columns.append(self._target_compare_item_column_name_with_unit)
        # 指标名称列
        all_columns.append(self._target_compare_item_column_name)
        # 比较类型列
        all_columns.append(self._target_compare_type_column_name)
        # 所有机构列表
        all_columns.extend(self._branch_selected_list)
        result = pd.DataFrame(columns=all_columns)
        # 初始化基础数据
        for diff_column_name in self._diff_column_dict.keys():
            for key in self._compare_types:
                diff_item_with_unit = "{}（{}）".format(diff_column_name, self._diff_column_dict.get(diff_column_name))
                result = result.append({
                    self._target_compare_item_column_name_with_unit: diff_item_with_unit,
                    self._target_compare_item_column_name: diff_column_name,
                    self._target_compare_type_column_name: key,
                }, ignore_index=True)
        return result

    def _after_calculated_difference(self, result):
        # 没有的数据填充"-"
        result.fillna(0, inplace=True)
        # 处理比较类型的排序
        result[self._target_compare_type_column_name] = pd.Categorical(
            result[self._target_compare_type_column_name],
            self._compare_type_order.keys()
        )

        result = result.drop(columns=[self._target_compare_item_column_name])
        result = result.rename(columns={
            self._target_compare_item_column_name_with_unit: self._target_compare_item_column_name,
        })

        # 按待分析差异、按比较类型归类
        pivot_result = result.set_index([self._target_compare_item_column_name, self._target_compare_type_column_name])
        # 调整比较项目（待分析差异列）的排序
        pivot_result.sort_index(
            axis=1,
            level=[0, 1],
            key=self._sort_compare_item_and_type,
            inplace=True,
        )
        # 添加机构合计列
        pivot_result["合计"] = pivot_result.apply(lambda x: x.sum(), axis=1)
        return pivot_result

    def _deal_with_compare_result(self, *, result, compare_result):
        """
        处理比较结果
        根据比较结果去设置最终结果集
        :param compare_result: 比较结果
        :param result: 最终结果集
        :return:
        """
        for row_i, row in result.iterrows():
            # 指标名称
            compare_item = row[self._target_compare_item_column_name]
            if compare_item not in compare_result.columns.values:
                # 如果指标名称不在结果集的列中，则直接忽略
                continue
            amount_unit = self._diff_column_dict.get(compare_item)
            # 比较类型
            target_cmp_type = row[self._target_compare_type_column_name]
            if target_cmp_type not in compare_result[self._target_compare_type_column_name].values:
                # 当前比较类型不在比较结果集中，直接忽略
                continue
            for branch in self._branch_selected_list:
                # 查找指标对应的值, 1: 机构是对应的机构
                criterion1 = compare_result[self._index_column_name].map(lambda x: x == branch)
                # 2: 比较类型是相应的比较类型
                criterion2 = compare_result[self._target_compare_type_column_name].map(lambda x: x == target_cmp_type)
                # 3: 找到所在部门、相应比较类型下，该指标名称的值
                value = compare_result.loc[criterion1 & criterion2, compare_item]
                if value.empty:
                    continue
                real_value = value.values[0]
                real_value = real_value / MoneyUtils.get_money_unit_divider(amount_unit)
                result.at[row_i, branch] = real_value

    def _write_diff_result(self, *, diff: pd.DataFrame) -> int:
        target_filename_full_path = os.path.join(self._target_directory, self._target_filename)
        logging.getLogger(__name__).info("输出文件：{} ".format(target_filename_full_path))
        # 如果文件已经存在，则采用追加的模式
        mode = 'a' if os.path.exists(target_filename_full_path) else 'w'
        # 如果Sheet已经存在则替换原有的Sheet
        replace_strategy = 'replace' if mode == 'a' else None
        with pd.ExcelWriter(target_filename_full_path, mode=mode, if_sheet_exists=replace_strategy) as excel_writer:
            diff.to_excel(
                excel_writer=excel_writer,
                sheet_name=self._target_sheet_name,
            )
        return 0
