import pyecharts.options as opts
from pyecharts.charts import WordCloud
from cntext.stats.stats import term_freq
from shifterator import EntropyShift
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.textpath import TextPath
from matplotlib.patches import PathPatch
from matplotlib.collections import PolyCollection
from matplotlib.font_manager import FontProperties
from matplotlib import font_manager as fm, rcParams
import matplotlib.pyplot as plt
from pathlib import Path
from PIL import Image
import os


def wordcloud(text, title, html_path):
    """
    使用pyecharts库绘制词云图
    :param text:  中文文本字符串数据
    :param title:  词云图标题
    :param html_path:  词云图html文件存储路径
    :return:
    """
    wordfreq_dict = dict(term_freq(text))
    wordfreqs = [(word, str(freq)) for word, freq in wordfreq_dict.items()]
    wc = WordCloud()
    wc.add(series_name="", data_pair=wordfreqs, word_size_range=[20, 100])
    wc.set_global_opts(
        title_opts=opts.TitleOpts(title=title,
                                  title_textstyle_opts=opts.TextStyleOpts(font_size=23)
                                  ),
        tooltip_opts=opts.TooltipOpts(is_show=True))
    wc.render(html_path)  #存储位置
    print('可视化完成，请前往 {} 查看'.format(html_path))




def wordshiftor(text1, text2, title, top_n=50, matplotlib_family='Arial Unicode MS'):
    """
    使用shifterator库绘制词移图，可用于查看两文本在词语信息熵上的区别
    :param text1:  文本数据1；字符串
    :param text2:  文本数据2；字符串
    :param title:  词移图标题
    :param top_n:  显示最常用的前n词； 默认值15
    :param matplotlib_family matplotlib中文字体，默认"Arial Unicode MS"；如绘图字体乱码请，请参考下面提示

        设置参数matplotlib_family，需要先运行下面代码获取本机字体列表
        from matplotlib.font_manager import FontManager
        mpl_fonts = set(f.name for f in FontManager().ttflist)
        print(mpl_fonts)
    """
    import matplotlib
    matplotlib.rc("font", family=matplotlib_family)
    type2freq_1 = term_freq(text1)

    type2freq_2 = term_freq(text2)

    entropy_shift = EntropyShift(type2freq_1=type2freq_1,
                                 type2freq_2=type2freq_2,
                                 base=2)
    entropy_shift.get_shift_graph(title=title, top_n=top_n)







def textpic(title='PYTHON测试', subtitle='使用Python生成图片', font='Alibaba-PuHuiTi-Bold.otf', titlesize=1.8, subsize=14):
    """
    :param title:  主标题
    :param subtitle: 副标题
    :param font:  本地中文字体路径
    :param titlesize: 主标题字体大小
    :param subsize: 副标题字体大小
    """

    fig, ax = plt.subplots()

    #更改字体，支持中文。
    prop = FontProperties(fname=font, weight=100)
    red = np.array([233, 77, 85, 255]) / 255
    darkred = np.array([130, 60, 71, 255]) / 255
    fig = plt.figure(figsize=(14.8 / 2.54, 21 / 2.54))
    ax = fig.add_axes([0, 0, 1, 1], aspect=1, xlim=[-10, 10], ylim=[-14.2, 14.2])
    ax.axis("off")

    # Text path
    path = TextPath((0, 0), title, size=titlesize, prop=prop)

    # Text centering
    V = path.vertices
    xmin, xmax = V[:, 0].min(), V[:, 0].max()
    ymin, ymax = V[:, 1].min(), V[:, 1].max()
    V -= (xmin + xmax) / 2 + 1, (ymin + ymax) / 2


    # Compute shadow by iterating over text path segments
    polys = []
    for (point, code) in path.iter_segments(curves=False):
        if code == path.MOVETO:
            points = [point]
        elif code == path.LINETO:
            points.append(point)
        elif code == path.CLOSEPOLY:
            points.append(points[0])
            points = np.array(points)
            for i in range(len(points) - 1):
                p0, p1 = points[i], points[i + 1]
                polys.append([p0, p1, p1 + (+20, -20), p0 + (+20, -20)])

    # Display shadow
    collection = PolyCollection(
        polys, closed=True, linewidth=0.0, facecolor=darkred, zorder=-10
    )
    ax.add_collection(collection)

    # Display text
    patch = PathPatch(path, facecolor="white", edgecolor="none", zorder=10)
    ax.add_artist(patch)

    # Transparent gradient to fade out shadow
    I = np.zeros((200, 1, 4)) + red
    ax.imshow(I, extent=[-11, 11, -15, 15], zorder=-20, clip_on=False)
    I[:, 0, 3] = np.linspace(0, 1, len(I))
    ax.imshow(I, extent=[-11, 11, -15, 15], zorder=0, clip_on=False)


    ax.text(
        6.5,
        -1.75,
        subtitle,
        color="white",
        ha="right",
        va="baseline",
        size=subsize,
        #family="Pacifico",
        zorder=30,
        fontproperties=prop
    )


    from pathlib import Path
    from PIL import Image
    import os

    cwd = Path().cwd()
    cwd.mkdir(exist_ok=True)
    filepath = cwd/"sideproduct.png"
    plt.savefig(filepath, dpi=300)



    img = Image.open(filepath)
    croping = img.crop((0,900,1748,1700))
    output = Path().cwd()/"output"
    output.mkdir(exist_ok=True)
    respath = cwd/"output"/"result.png"
    croping.save(respath)
    os.remove(filepath)




