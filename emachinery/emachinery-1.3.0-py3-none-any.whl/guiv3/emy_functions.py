# 常用库
from pylab import np, mpl, plt
from collections import OrderedDict as OD
from dataclasses import dataclass
import matplotlib.animation as animation
import json, re, copy, pkg_resources
import traceback
import pandas as pd

# 后端
# use cairo only for acmsimpy | use cairo for acmsimc will slow down plotting
# mpl.use('cairo') # try if this is faster for animate plotting? ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']

# 风格
mpl.style.use('ggplot') # further customize: https://stackoverflow.com/questions/35223312/matplotlib-overriding-ggplot-default-style-properties and https://matplotlib.org/2.0.2/users/customizing.html
# mpl.style.use("dark_background")
# mpl.style.use('grayscale')
# mpl.style.use('classic')

# 字体
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'STIXGeneral'
mpl.rcParams['font.weight'] ='900'     # bold is 700, normal is 400, see https://matplotlib.org/2.0.2/users/customizing.html
mpl.rcParams['font.size']   =12 # 13 is too big, commenting out is too small

# 颜色设置壹/叁
# https://matplotlib.org/2.0.2/users/customizing.html from https://stackoverflow.com/questions/35223312/matplotlib-overriding-ggplot-default-style-properties
# mpl.rcParams['axes.labelsize']  =14   # 'medium' # 'large'是没用的！
hex_monokai   = '#272822'
hex_wanderson = '#3d444c'
mpl.rcParams['axes.facecolor']  =hex_wanderson # also need to change facecolor in mplwidget.py to get a consistent look
mpl.rcParams['axes.labelcolor'] ='#d5d1c7' # tint grey
mpl.rcParams['axes.axisbelow']  ='False'   # 'line'
mpl.rcParams['ytick.color']     ='#d5d1c7' #'white'
mpl.rcParams['xtick.color']     ='#d5d1c7' #'white'
mpl.rcParams['text.color']      ='#d5d1c7' #'white'
mpl.rcParams['grid.color']      ='#d5d1c7' # grid color
mpl.rcParams['grid.linestyle']  ='--'      # solid
mpl.rcParams['grid.linewidth']  =0.3       # in points
mpl.rcParams['grid.alpha']      =0.8       # transparency, between 0.0 and 1.0



@dataclass
class CJH_Plotting(object):
    cjh_linestyles = [
            '-', '--', (0, (3, 1, 1, 1)), ':', '-.', 
            '-', '--', (0, (3, 1, 1, 1)), ':', '-.', 
            '-', '--', (0, (3, 1, 1, 1)), ':', '-.', 
        ]
    # 颜色设置叁/叁
    cjh_colors = [
            '#ff6347', # tomato red
            'white',   # #d5d1c7',
            '#B3F5FF', # dark-theme-bright-blue
            '#FFF0B3', # dark-theme-bright-yellow
            '#ffabff', # pink
            '#E1C7E0', # dark-theme-bright-violet(purple)
            '#ABF5D1', # dark-theme-bright-green
            '#FFBDAD', # dark-theme-bright-red
            '#00dcff', # blue
            '#c593ff', # dark-theme-bright-color1
            '#02dac3', # dark-theme-bright-color2
            '#efc9a1', # dark-theme-bright-color3
            # 'black',
            'blue',
            '#857F72', # warmGrey
            '#616E7C', # Cool Grey
            '#B8B2A7', # warmGrey
            '#9AA5B1', # Cool Grey
            '#504A40', # warmGrey
            '#27241D', # warmGrey
        ] # https://uxdesign.cc/dark-mode-ui-design-the-definitive-guide-part-1-color-53dcfaea5129

    def __init__(self):
        # 作图用外观设置
        # generator的好处是循环，列表则是有限的 # https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/linestyles.html
        self.cjh_linestyle = self.cyclic_generator(self.cjh_linestyles)
        self.cjh_color = self.cyclic_generator(self.cjh_colors)
        # 注意，不可以做 list(self.cjh_color)，因为这是一个无止境循环的发生器，会卡住的。。。

    @staticmethod
    def cyclic_generator(list_of_things):
        N, i = len(list_of_things), 0
        while True:
            yield list_of_things[i]
            i +=1
            if i > (N-1):
                i = 0


from emachinery.acmsimpyv1 import acmsimpy

# FUNCTIONS
class EmyFunctions(object):

    # Run real time simulation with ACMSymPy
    ''' Python-Numba-based Simulation '''
    # @Slot()
    # @decorator_status(status='Configuring') # this will not be updated until this function is done
    def runPyBasedSimulation(self, bool_realtime=True):

        # 颜色设置贰/叁
        self.ui.load_pages.MplWidget_ACMPlot.toolbar.setStyleSheet("background-color: #9AA5B1;")
        # self.ui.right_column.horizontalLayout_CBSMplToolBar.addWidget(self.ui.MplWidget_ACMPlot.toolbar)

        def update_line_data(end_time, line, ydata):
            line.ydata = np.append(line.ydata, ydata)
            line.ydata = line.ydata[-CONSOLE.NUMBER_OF_SAMPLE_TO_SHOW:]
            line.MIN = min(line.ydata) if min(line.ydata) < line.MIN else line.MIN
            line.MAX = max(line.ydata) if max(line.ydata) > line.MAX else line.MAX

            xdata = np.arange(end_time*CONSOLE.SAMPLING_RATE-len(line.ydata), end_time*CONSOLE.SAMPLING_RATE, 1) * CONSOLE.CL_TS # 整数代替浮点数，精度高否则会出现xdata长3001，ydata长3000的问题。
            # print(len(xdata),len(line.ydata))
            line.set_data(xdata, line.ydata)
            if line.MIN != line.MAX:
                line.ax.set_ylim([line.MIN, line.MAX]) # this .ax is manually assigned when line object is created.

        def ACMアニメ4Py(ii):
            # if ii>100000 or self.ui.load_pages.lineEdit_AtTop.text() == 's':
            #     CONSOLE.anim.event_source.stop()
            #     print('Stop ACMPlot animation for Python.\n----------\n\n')
            #     UIFunctions.labelTitle(self, 'Main Window - emachinery - Simulation Done')

                # Save time here
                # print(f'Animation goes {ii}')
                # try:
                #     int(self.ui.load_pages.lineEdit_AtTop.text())
                # except:
                #     pass
                # else:
                #     self.NUMBER_OF_SAMPLE_TO_SHOW = int(self.ui.load_pages.lineEdit_AtTop.text())
                # if self.NUMBER_OF_SAMPLE_TO_SHOW<self.TIME_SLICE*self.SAMPLING_RATE:
                #     self.NUMBER_OF_SAMPLE_TO_SHOW = int(self.TIME_SLICE*self.SAMPLING_RATE)

                # Runtime User Input from window self.eW
                # if self.eW is not None and self.eW.input1.text() != '':
                #     CTRL.cmd_rpm_speed = float(self.eW.input1.text())
                #     print('\t', CTRL.cmd_rpm_speed, 'rpm')

            """perform animation step"""
            if CONSOLE.reset == True:
                CONSOLE.reset = False
                CONSOLE.offset_anime_ii = ii
            t0 = (ii-CONSOLE.offset_anime_ii)*CONSOLE.TIME_SLICE
            control_times, numba__waveforms_dict, = \
                acmsimpy.ACMSimPyWrapper(
                    numba__scope_dict,
                    t0=t0, TIME=CONSOLE.TIME_SLICE,
                    ACM=ACM,
                    CTRL=CTRL,
                    reg_id=reg_id,
                    reg_iq=reg_iq,
                    reg_speed=reg_speed,
                    OB=OB,
                    HUMAN=HUMAN
                )
            end_time = control_times[-1] # print('\tend_time:', end_time)

            """ update matplotlib artist """
            for key, waveforms_data in numba__waveforms_dict.items():
                for line, ydata in zip(numba__line_dict[key], waveforms_data):
                    # print(key, line, ydata[0:3], numba__line_dict[key], len(waveforms_data))
                    update_line_data(end_time, line, ydata)
            # time_text.set_text('time = %.1f' % end_time)

            first_ax.set_xlim([end_time-CONSOLE.NUMBER_OF_SAMPLE_TO_SHOW*CONSOLE.CL_TS, end_time])
            # first_ax.set_xticklabels(np.arange(0, int(round(end_time)), int(round(end_time))*0.1)) #, fontdict=font)

            # return line01, line02, time_text # for using blit=True but blit does not update xticks and yticks

        """ Read from GUI """
        try:
            the_cmd = self.ui.load_pages.plainTextEdit_NumbaScopeDict.toPlainText()
            numba__scope_dict = eval(the_cmd[the_cmd.find('OD'):])
        except Exception as err:
            print('-------------------')
            print('Decypher for NumbaScopeDict has failed. Will use the default dict.')
            numba__scope_dict = OD([
                (r'Speed [rpm]',                  ( 'CTRL.omega_elec'           ,)  ),
                (r'Position [rad]',               ( 'ACM.x[3]'                  ,)  ),
                (r'$q$-axis current [A]',         ( 'ACM.x[1]', 'CTRL.idq[1]'   ,)  ),
                (r'$d$-axis current [A]',         ( 'ACM.x[0]', 'CTRL.idq[0]'   ,)  ),
                (r'$\alpha\beta$ current [A]',    ( 'CTRL.iab[0]', 'CTRL.iab[1]',)  ),
            ])
            print('err:', err)
            traceback.print_exc()
            print('-------------------')

        """ Canvas """
        self.ui.load_pages.MplWidget_ACMPlot.canvas.figure.clf() # clear canvas
        print('numba__scope_dict =', numba__scope_dict)
        number_of_subplot = len(numba__scope_dict)
        numba__line_dict = OD()
        numba__axes = []
        first_ax = None

        cjh_plotting = CJH_Plotting()

        for index, (ylabel, waveform_names) in enumerate(numba__scope_dict.items()):
            # get axes
            ax = self.ui.load_pages.MplWidget_ACMPlot.canvas.figure.add_subplot(
                number_of_subplot, 
                1, 1+index, 
                autoscale_on=False, 
                sharex=first_ax
            )
            first_ax = ax if index == 0 else first_ax
            numba__axes.append(ax)

            numba__line_dict[ylabel] = []
            for jj, name in enumerate(waveform_names):
                # print(jj, name)
                # get line objects
                line, = ax.plot([], [], 
                                linestyle=cjh_plotting.cjh_linestyles[jj], 
                                color=cjh_plotting.cjh_colors[jj], 
                                lw=1.5, 
                                label=name, 
                                alpha=0.7) # zorder
                line.ax = ax
                line.ydata = np.array(0)
                line.MIN = -1e-10
                line.MAX =  1e-10
                numba__line_dict[ylabel].append(line)

            ax.set_ylabel(ylabel)
            ax.legend(loc='lower left').set_zorder(202)

        numba__axes[-1].set_xlabel('Time [s]')
        # time_text = first_ax.text(0.02, 0.95, '', transform=first_ax.transAxes)

        """ User control over the mpl animation """
        @dataclass
        class THE_CONSOLE:
            offset_anime_ii : int = 0
            reset : int = False
            _pause : int = False
            SAMPLING_RATE : float = 1e4
            TIME_SLICE : float = 0.2
            NUMBER_OF_SAMPLE_TO_SHOW : int = 30000
            def __post_init__(self):
                self.CL_TS = 1 / self.SAMPLING_RATE
        CONSOLE = THE_CONSOLE(TIME_SLICE=0.2)

        """ Simulation Globals """
        HUMAN     = acmsimpy.The_Human()
        OB        = acmsimpy.The_Observer(HUMAN)
        ACM       = acmsimpy.The_AC_Machines(HUMAN)
        CTRL      = acmsimpy.The_Motor_Controller(CONSOLE.CL_TS, 5*CONSOLE.CL_TS, HUMAN)
        reg_id    = acmsimpy.The_PI_Regulator(6.39955, 6.39955*237.845*CTRL.CL_TS, 600)
        reg_iq    = acmsimpy.The_PI_Regulator(6.39955, 6.39955*237.845*CTRL.CL_TS, 600)
        reg_speed = acmsimpy.The_PI_Regulator(0.0380362, 0.0380362*30.5565*CTRL.VL_TS, 1*1.414*ACM.IN)

        """ Simulation Globals Access from Console """
        self.console_push_variable({'CONSOLE':CONSOLE})
        self.console_push_variable({'ACM':ACM})
        self.console_push_variable({'CTRL':CTRL})
        self.console_push_variable({'HM':HUMAN, 'HUMAN':HUMAN})
        self.console_push_variable({'reg_id':reg_id})
        self.console_push_variable({'reg_iq':reg_iq})
        self.console_push_variable({'reg_speed':reg_speed})

        """ Visualization of Realtime Simulation """
        print('\tJIT compile with numba...')
        def onClick(event):
            print(event)
            CONSOLE._pause ^= True
            if CONSOLE._pause:
                CONSOLE.anim.event_source.stop()
            else:
                CONSOLE.anim.event_source.start()

        self.ui.load_pages.MplWidget_ACMPlot.canvas.figure.canvas.mpl_connect('button_press_event', onClick)
        self.ui.load_pages.MplWidget_ACMPlot.canvas.draw_idle() # draw before animation # https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
        CONSOLE.anim = animation.FuncAnimation(self.ui.load_pages.MplWidget_ACMPlot.canvas.figure, ACMアニメ4Py, 
                                        interval=200, cache_frame_data=False) # cache_frame_data=False is good for large artists when plotting
                                        #, blit=True) # blit=True means only re-draw the parts that have changed. 
                                        # https://matplotlib.org/stable/tutorials/advanced/blitting.html
                                        # https://stackoverflow.com/questions/14421924/matplotlib-animate-does-not-update-tick-labels
                                        # https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/

