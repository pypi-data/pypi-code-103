# -*- coding:utf-8 -*-
# @Author    : g1879
# @date      : 2021-08-09
# @email     : g1879@qq.com
# @File      : memo.py
s = """
=============定位符=============
组成：('列名', '属性名', r'正则表达式')
注：列名是在paths中已定义的列

=============Paths 类属性=============
-------------
# 路径的类型，'css'或'xpath'
paths.type

# 共有的关键元素
paths.rows  # 列表行元素的定位路径，必须
paths.cols  # 行元素中列元素的定位路径，字典格式，必须
paths.next_btn  # 下一页或加载更多按钮元素路径，按页面情况使用，非必须

# 翻页式列表页独有属性
paths.pages_count  # 定位符，总页数所在元素路径，非必须

# 滚动式列表页独有属性
paths.container  # 列表容器，必须

    -------------通过字典创建-------------
    paths_dict = {
        # 路径的类型，只能是'css'或'xpath'，非必须
        'type': 'css',
        
        # 行元素路径，必须 
        'rows': 'xpath 或 css selector',
        
        # 列元素相对于行元素的路径，必须
        'cols': {
            'col1': 'xpath 或 css selector',
            'col2': 'xpath 或 css selector',
            ...
        }
        
        # 翻页式页面总页数获取定位符，格式见上一节，非必须
        'pages_count': 定位符,  
        
        # 下一页（翻页式）或加载更多（滚动式）按钮元素路径，非必须
        'next_btn': 'xpath 或 css selector',
        
        # 行元素所在容器路径，滚动式页面专用，使用滚动式页面时必须
        'container': 'xpath 或 css selector',
    }
    
    paths = Paths(paths_dict=paths_dict)

=============Targets 类=============
targets = Targets(paths)
targets.add_target('标题', '列名', '属性名', r'正则表达式')
targets.start_stop_row = (1,)  # 爬取第2行到最后一行

    -------------通过字典创建-------------
    targets_dict = {
        'start_stop': (1, -1),  # 爬取第2到倒数第2行，规则与切片的一样，非必须
        '目标1': '列1',
        '目标2': ('列2', 'href'),
        '目标3': ('列3', 'src', '(.*)@')
        ...
    }
"""
print(s)
