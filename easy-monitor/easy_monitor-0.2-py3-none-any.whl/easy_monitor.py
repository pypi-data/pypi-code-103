import matplotlib.pyplot as plt
import numpy as np
import math


class easy_monitor():
    def __init__(self, figure_title=None, plotlabel=None, frame_pause_time=0.01, xlabel="X-axis", ylabel="Y-axis",
                 linestyle='b-', linewidth=2.0, xlim_lower=None, xlim_upper=None,
                 ylim_lower=None, ylim_upper=None, margin_factor=100, xticks_num=11, yticks_num=11,
                 lengend_loc="upper left", x_log=False, y_log=False):
        plt.figure(figsize=(8, 6), dpi=80)
        # 打开交互模式
        plt.ion()
        # 设置图标内容
        self.x_list = []
        self.y_list = []
        self.frame_pause_time = frame_pause_time
        self.figure_title = figure_title
        self.plotlabel = plotlabel
        self.linestyle = linestyle
        self.linewidth = linewidth
        self.xlim_lower = xlim_lower
        self.xlim_upper = xlim_upper
        self.ylim_lower = ylim_lower
        self.ylim_upper = ylim_upper
        self.x_min = float('inf')
        self.x_max = -float('inf')
        self.y_min = float('inf')
        self.y_max = -float('inf')
        self.marginFactor = margin_factor
        self.xticks_num = xticks_num
        self.yticks_num = yticks_num
        self.lengend_loc = lengend_loc
        self.x_log = x_log
        self.y_log = y_log
        self.xlabel = 'log(' + xlabel + ')' if self.x_log else xlabel
        self.ylabel = 'log(' + ylabel + ')' if self.y_log else ylabel

    def ani_plot(self, xx, yy):
        # 清除原有图像
        plt.cla()

        # 设定标题等
        if self.figure_title != 0:
            plt.title(self.figure_title)
        plt.grid(True)

        if self.x_log:
            xx = math.log10(xx)
        if self.y_log:
            yy = math.log10(yy)

        self.x_list.append(xx)
        self.y_list.append(yy)

        # 设置X轴
        plt.xlabel(self.xlabel)
        if xx < self.x_min:
            self.x_min = xx
        if xx > self.x_max:
            self.x_max = xx
        x_margin = (self.x_max - self.x_min) / self.marginFactor
        if self.xlim_lower == None:
            xlim_lower = self.x_min - x_margin
        else:
            xlim_lower = self.xlim_lower
        if self.xlim_upper == None:
            xlim_upper = self.x_max + x_margin
        else:
            xlim_upper = self.xlim_upper

        if xlim_upper == xlim_lower:
            xlim_upper = xlim_lower + 1.0
        plt.xlim(xlim_lower, xlim_upper)
        plt.xticks(np.linspace(xlim_lower, xlim_upper, self.xticks_num, endpoint=True))

        # 设置Y轴
        plt.ylabel(self.ylabel)
        if yy < self.y_min:
            self.y_min = yy
        if yy > self.y_max:
            self.y_max = yy
        y_margin = (self.y_max - self.y_min) / self.marginFactor
        if self.ylim_lower == None:
            ylim_lower = self.y_min - y_margin
        else:
            ylim_lower = self.ylim_lower
        if self.ylim_upper == None:
            ylim_upper = self.y_max + y_margin
        else:
            ylim_upper = self.ylim_upper
        if ylim_upper == ylim_lower:
            ylim_upper = ylim_lower + 1.0
        plt.ylim(ylim_lower, ylim_upper)
        plt.yticks(np.linspace(ylim_lower, ylim_upper, self.yticks_num, endpoint=True))

        # 画曲线
        plt.plot(self.x_list, self.y_list, self.linestyle, linewidth=self.linewidth, label=self.plotlabel)

        # 设置图例位置,loc可以为[upper, lower, left, right, center]
        if self.plotlabel != None:
            plt.legend(loc=self.lengend_loc, shadow=True)

        # 暂停
        plt.pause(self.frame_pause_time)
        return

    def hold_figure(self):
        # 关闭交互模式
        plt.ioff()
        # 图形显示
        plt.show()
