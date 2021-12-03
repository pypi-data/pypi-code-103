#
# def assist(ith_score):
#     """
#     Args:
#         ith_score: Float. ITH quantification for potential assistance
#     Returns:
#         assist_dict: Dictionary. Suggested tumor characteris
#     """
#
#     这里核心的逻辑是，每个表型的assist字典保存阈值：表型，使用时判断遍历keys判断阈值大小即可（这样可以用一个util函数完成这项工作）
#     后续可以考虑增加输出概率辅助决策的功能
#     # 等距离划分ITHscore，然后看每个score位置不同category的概率。决策时读取ITHscore定位其区间（取余），然后输出概率和argmax做最可能结果即可
#
