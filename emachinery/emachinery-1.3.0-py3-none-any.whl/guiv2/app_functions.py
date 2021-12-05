## ==> GUI FILE
from app_modules import *

if bool_use_PySide6 == True:
    from PySide6.QtCore import Signal, Slot
elif bool_use_PyQt5:
    from PyQt5.QtCore import pyqtSignal as Signal, pyqtSlot as Slot
else:
    from PySide2.QtCore import Signal, Slot
from ui_functions_old import UIFunctions

# 常用库
import matplotlib.animation as animation
import json, re, copy, pkg_resources
import traceback
import pandas as pd
from pylab import np, mpl, plt
# use cairo only for acmsimpy | use cairo for acmsimc will slow down plotting
# mpl.use('cairo') # try if this is faster for animate plotting? ['GTK3Agg', 'GTK3Cairo', 'MacOSX', 'nbAgg', 'Qt4Agg', 'Qt4Cairo', 'Qt5Agg', 'Qt5Cairo', 'TkAgg', 'TkCairo', 'WebAgg', 'WX', 'WXAgg', 'WXCairo', 'agg', 'cairo', 'pdf', 'pgf', 'ps', 'svg', 'template']
from collections import OrderedDict as OD
from dataclasses import dataclass


# 界面模块
# from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
# Promoted Widgets: use these two absolute imports to replace the relative imports in mainWindow.py before uploading to PyPI
    # from emachinery.gui.consolewidget import ConsoleWidget
    # from emachinery.gui.mplwidget import MplWidget
from emachinery.guiv2 import latexdemo
from emachinery.guiv2.stylesheet.toggle_stylesheet import toggle_stylesheet
# from emachinery.newcode import newcode

# 电机
from emachinery.utils.conversion import ElectricMachinery
from emachinery.jsons import ACMInfo
from emachinery.acmdesignv2 import tuner
# from emachinery.acmdesignv2 import simulator
from emachinery.acmdesignv2 import analyzer

#? Numba accelerated python simulation
# from emachinery.acmsimpyv1 import acmsimpy
from acmsimpyv1 import acmsimpy # 哎见鬼了，为什么这个库可以不用加前缀emachinery.？？
    # https://stackoverflow.com/questions/3012473/how-do-i-override-a-python-import
    # if imp.lock_held() is True:
    #     del sys.modules[moduleName]
    #     sys.modules[tmpModuleName] = __import__(tmpModuleName)
    #     sys.modules[moduleName] = __import__(tmpModuleName)

# 风格
mpl.style.use('ggplot') # further customize: https://stackoverflow.com/questions/35223312/matplotlib-overriding-ggplot-default-style-properties and https://matplotlib.org/2.0.2/users/customizing.html
# plt.style.use("dark_background")
# mpl.style.use('grayscale')
# mpl.style.use('classic')

# 字体
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['font.weight'] ='900'     # bold is 700, normal is 400, see https://matplotlib.org/2.0.2/users/customizing.html
plt.rcParams['font.size']   =12 # 13 is too big, commenting out is too small

# 颜色设置壹/叁
# https://matplotlib.org/2.0.2/users/customizing.html from https://stackoverflow.com/questions/35223312/matplotlib-overriding-ggplot-default-style-properties
# plt.rcParams['axes.labelsize']  =14   # 'medium' # 'large'是没用的！
hex_monokai   = '#272822'
hex_wanderson = '#3d444c'
plt.rcParams['axes.facecolor']  =hex_wanderson # also need to change facecolor in mplwidget.py to get a consistent look
plt.rcParams['axes.labelcolor'] ='#d5d1c7' # tint grey
plt.rcParams['axes.axisbelow']  ='False'   # 'line'
plt.rcParams['ytick.color']     ='#d5d1c7' #'white'
plt.rcParams['xtick.color']     ='#d5d1c7' #'white'
plt.rcParams['text.color']      ='#d5d1c7' #'white'
plt.rcParams['grid.color']      ='#d5d1c7' # grid color
plt.rcParams['grid.linestyle']  ='--'      # solid
plt.rcParams['grid.linewidth']  =0.3       # in points
plt.rcParams['grid.alpha']      =0.8       # transparency, between 0.0 and 1.0

from copy import deepcopy
# 本函数用于备份产生某特定数据的代码
def get_global_plot_script(details, list__number_of_traces_per_subplot, list__label):
    details_backup = deepcopy(details)
    number_of_subplot = len(list__number_of_traces_per_subplot)
    python_script = f'''
    list_of_ylabel = [{chr(10).join(['    "'+label+'",' for label in list__label])}
    ]\n
    list_of_signalNames = [
    '''

    for number_of_traces in list__number_of_traces_per_subplot:
        traces = ''
        for _ in range(number_of_traces):
            traces += '\n\t\t\t"' + details.pop(0) + '",'
        python_script += f'''\t######################################
        ( {traces}
        ),
        '''
    return f'''if __name__ == '__main__':
    import os, sys; sys.path.insert(1, os.path.dirname(__file__) + '/../../CJHAcademicPlot'); 
    from __cjhAcademicPlotSettings import CJHStylePlot
    csp = CJHStylePlot(path2info_dot_dat=__file__, nrows={number_of_subplot})
    csp.load()
    """ Plot Menu
    ''' + '\n\t'.join(list__label)  \
        + f'\n\t{details_backup}'   \
        + '\n\t"""\n\n'             \
        + python_script + ']\n\n'   \
        + '\n    csp.figsize = (4,4)' \
        + '\n    csp.plot(list_of_ylabel, list_of_signalNames, index=0)' # must use space here or else python compiler will complain about indentation

# 实用函数
import subprocess
def subprocess_cmd(command_string, bool_run_parallel=False):
    process = subprocess.Popen(command_string, stdout=subprocess.PIPE, shell=True)
    if not bool_run_parallel:
        streamdata = proc_stdout = process.communicate()[0].strip()
        print(proc_stdout)
    return process
def cyclic_generator(list_of_things):
    N, i = len(list_of_things), 0
    while True:
        yield list_of_things[i]
        i +=1
        if i > (N-1):
            i = 0
def decorator_status(status=''): # https://stackoverflow.com/questions/739654/how-to-make-function-decorators-and-chain-them-together
    def run_time(fn):
        def wrapped(*args, **kwargs):
            self=args[0]
            UIFunctions.labelTitle(self, f'Main Window - emachinery - {status}')
            fn(*args, **kwargs)
        return wrapped
    return run_time


class AppFunctions:

    ########################################################################
    ## START - APP FUNCTIONS
    ########################################################################
    ''' Connect functions to GUI compoents '''
    def initialize_connections(self):
        # 为什么初始化的时候设置css无效？而是必须在这里事后设置呢？？
        # 为什么无法修改ConsoleWidget和QCodeEditor的背景色呢？
        #         css = '''
        # color: blue;
        # background-color: yellow;
        # selection-color: yellow;
        # selection-background-color: blue;
        # '''
        #         print('[debug app_functions.py]: apply css loc 1')
        #         # self.ui.ConsoleWidget.setStyleSheet(css)
        #         self.ui.plainTextEdit_ACMPlotLabels.setStyleSheet(css)
        #         self.ui.plainTextEdit_ACMPlotDetails.setStyleSheet(css)
        #         self.ui.plainTextEdit_LissajousPlotSignals.setStyleSheet(css)
        #         self.ui.plainTextEdit_PANames.setStyleSheet(css)
        #         self.ui.plainTextEdit_PAValues.setStyleSheet(css)

        '''tab 1: Name Plate Data
        '''
        self.mj = ACMInfo.MotorJson().d

        self.ui.comboBox_MachineName.activated.connect(lambda: AppFunctions.comboActivate_namePlateData(self))
        self.ui.comboBox_MachineType.activated.connect(lambda: AppFunctions.comboActivate_machineType(self))


        # load global config
        self.filepath_to_configlob = None
        AppFunctions.load_configlob(self)
        # 记住上一次的电机类型选择
        self.ui.comboBox_MachineType.setCurrentIndex(self.configlob['MachineTypeIndex']) # BUG

        #
        self.filepath_to_configini = None
        AppFunctions.load_configini(self)

        # this will invoke: AppFunctions.update_ACMPlotLabels_and_ACMPlotSignals(self, bool_re_init=True) for ya
        AppFunctions.comboActivate_machineType(self, bool_write_configlob=False) # configini is loaded here

        # Move this to later, because we need to update lineEdit_OutputDataFileName from recovery first
        # self.motor_dict = AppFunctions.get_motor_dict(self, self.mj);

        # Select Excitation
        self.list__radioButton4Excitation = [
            self.ui.radioButton_Excitation_Position,
            self.ui.radioButton_Excitation_Velocity,
            self.ui.radioButton_Excitation_SweepFrequency]
        self.list__checkedExcitation = [radioButton.isChecked() for radioButton in self.list__radioButton4Excitation]
        for radioButton in self.list__radioButton4Excitation:
            radioButton.toggled.connect(lambda: AppFunctions.radioChecked_ACMExcitation(self))

        self.control_dict   = dict(); self.control_dict = AppFunctions.get_control_dict(self)
        self.sweepFreq_dict = dict(); self.sweepFreq_dict = AppFunctions.get_sweepFreq_dict(self)



        '''tab_3: C-based Simulation
        '''
        self.ui.pushButton_runCBasedSimulation      .clicked.connect(lambda: AppFunctions.runCBasedSimulation(self))
        self.ui.pushButton_runCBasedSimulation_AtTop.clicked.connect(lambda: AppFunctions.runCBasedSimulation(self))
        self.ui.pushButton_runPyBasedSimulation_AtTop.clicked.connect(lambda: AppFunctions.runPyBasedSimulation(self))

        self.ui.pushButton_ShowFloatingConsole_AtTop.clicked.connect(lambda: UIFunctions.invoke_PyBlackBox(self))


        # init comboBox_PlotSettingSelect
        self.ui.comboBox_PlotSettingSelect.activated.connect(lambda: AppFunctions.update_ACMPlotLabels_and_ACMPlotSignals(self))

        # Motor Dict ( The order matters, should be after AppFunctions.comboActivate_machineType(self) )
        print('\tOutputDataFileName:', self.ui.lineEdit_OutputDataFileName.text())
        self.motor_dict = AppFunctions.get_motor_dict(self, self.mj);


        self.ui.label_top_info_1.     setText(self.path2acmsimc)
        self.ui.lineEdit_path2acmsimc.setText(self.path2acmsimc)
        self.ui.lineEdit_path2acmsimc.textChanged[str].connect(lambda: AppFunctions.save_path2acmsimc(self))

        self.ui.lineEdit_OutputDataFileName.textChanged[str].connect(lambda: AppFunctions.update_PADataFileList(self))


        # settings for sweep frequency
        self.ui.radioButton_openLoop.toggled.       connect(lambda: AppFunctions.radioChecked_Settings4SweepFrequency(self))
        self.ui.radioButton_currentLoopOnly.toggled.connect(lambda: AppFunctions.radioChecked_Settings4SweepFrequency(self))

        # settings for uncertainty
        AppFunctions.update_uncertaintyTable(self, self.configini)

        '''PlotPanel: ACMPlot
        '''
        self.ui.pushButton_ACMPlotHere     .clicked.connect(lambda: AppFunctions.clicked__pushButton_ACMPlotHere(self))
        self.ui.pushButton_ACMPlotHereAtTop.clicked.connect(lambda: AppFunctions.clicked__pushButton_ACMPlotHere(self))
        # Matplotlib navigation bar to: self or tabWidget
        # self.scope_toolbar = NavigationToolbar(self.ui.MplWidget_ACMPlot.canvas, self)

        # 颜色设置贰/叁
        self.ui.MplWidget_ACMPlot.toolbar.setStyleSheet("background-color: #9AA5B1;")
        self.ui.horizontalLayout_CBSMplToolBar.addWidget(self.ui.MplWidget_ACMPlot.toolbar)
        # self.ui.verticalLayout_CBSMplToolBar.addWidget(self.scope_toolbar)
        # self.ui.frame_CBSMplToolBar.addWidget(self.scope_toolbar) # no addWidget
        # https://stackoverflow.com/questions/60495523/how-to-adjust-the-size-of-a-widget-within-a-horizontal-layout


        # this is used to judge when to stop animation
        self.last_no_samples = None

        # 作图用外观设置
        # generator的好处是循环，列表则是有限的 # https://matplotlib.org/3.1.0/gallery/lines_bars_and_markers/linestyles.html
        self.cjh_linestyles= [
                '-', '--', (0, (3, 1, 1, 1)), ':', '-.', 
                '-', '--', (0, (3, 1, 1, 1)), ':', '-.', 
                '-', '--', (0, (3, 1, 1, 1)), ':', '-.', 
            ]
        self.cjh_linestyle = cyclic_generator(self.cjh_linestyles)
        # 颜色设置叁/叁
        self.cjh_colors = [
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
        self.cjh_color = cyclic_generator(self.cjh_colors)
        # 注意，不可以做 list(self.cjh_color)，因为这是一个无止境循环的发生器，会卡住的。。。


        '''tab_2: Controller Tuning
        '''
        latex_repo = latexdemo.LaTeX_Repo()
        self.ui.label_qpix_CLKP.setPixmap(latex_repo.qpixmap_CLKP)
        self.ui.label_qpix_CLKI.setPixmap(latex_repo.qpixmap_CLKI)
        self.ui.label_qpix_VLKP.setPixmap(latex_repo.qpixmap_VLKP)
        self.ui.label_qpix_VLKI.setPixmap(latex_repo.qpixmap_VLKI)
        self.ui.label_qpix_Note1.setPixmap(latex_repo.qpixmap_Note1)
        self.ui.label_qpix_Note2.setPixmap(latex_repo.qpixmap_Note2)
        self.ui.label_qpix_Note3.setPixmap(latex_repo.qpixmap_Note3)
        self.ui.pushButton_pidTuner.clicked.connect(lambda: AppFunctions.run_series_pid_tuner(self))
        AppFunctions.run_series_pid_tuner(self)
        # self.ui.pushButton_SweepFreq.clicked.connect(lambda: AppFunctions.runCBasedSimulation_SweepFrequnecyAnalysis(self))


        '''tab_4: Bode Plot
        '''
        self.ui.pushButton_bodePlot.clicked.connect(lambda: AppFunctions.update_BodePlot(self))


        '''tab_5: Parametric Analysis
        '''
        self.ui.pushButton_runCBasedSimulation4PA.clicked.connect(lambda: AppFunctions.runCBasedSimulation4PA(self))
        self.ui.plainTextEdit_PANames.clear()
        self.ui.plainTextEdit_PANames.appendPlainText(self.configini['PANames'])
        self.ui.plainTextEdit_PAValues.clear()
        self.ui.plainTextEdit_PAValues.appendPlainText(self.configini['PAValues'])

        self.ui.pushButton_plot4PA.clicked.connect(lambda: AppFunctions.plot4PA(self))

        data_file_name_list = AppFunctions.getDataFileNameList4PA(self)
        self.ui.comboBox_PADataFileSelected.clear()
        self.ui.comboBox_PADataFileSelected.addItems(data_file_name_list)
        self.ui.comboBox_PADataFileSelected.activated.connect(lambda: AppFunctions.update_PASelected(self))


        '''tab_6: Plots
        '''
        # update plot
        self.ui.pushButton_getSignal.clicked.connect(lambda: AppFunctions.update_graph(self))
        # undate model
        self.ui.pushButton_updateModel.clicked.connect(lambda: AppFunctions.update_emy(self))

        # Matplotlib navigation bar to: self or tabWidget
        # self.plot_toolbar = NavigationToolbar(self.ui.MplWidget.canvas, self)
            # self.addToolBar(self.plot_toolbar) # add to mainWindow
        self.ui.verticalLayout_inTab2.addWidget(self.ui.MplWidget.toolbar) # add to tab 2 only

        # Lissajous Plot
        self.ui.pushButton_LissajousPlot.clicked.connect(lambda: AppFunctions.update_LissajousPlot(self))
        self.ui.horizontalSlider_LissajousTimeStart.valueChanged.connect(lambda: AppFunctions.update_LissajousPlot(self))
        self.ui.horizontalSlider_LissajousTimeEnd.valueChanged.connect(lambda: AppFunctions.update_LissajousPlot(self))
        self.signals = self.no_samples = None


        '''tab_7: FEA-based Optimization
        '''
        # self.path2boptPython = self.ui.lineEdit_path2boptPython.text()
        # if False:
        #     try:
        #         sys.path.insert(0, self.path2boptPython)
        #         sys.path.insert(0, self.path2boptPython+'codes3/')

        #         with open(self.path2boptPython+'/codes3/machine_specifications.json', 'r', encoding='utf-8') as f:
        #             self.bopt_fea_config_dict = json.load(f, object_pairs_hook=OrderedDict) # https://stackoverflow.com/questions/10844064/items-in-json-object-are-out-of-order-using-json-dumps/23820416
        #         self.ui.comboBox_MachineSpec.addItems(self.bopt_fea_config_dict.keys())
        #         self.ui.comboBox_MachineSpec.activated.connect(lambda: AppFunctions.update_machineSpec(self))
        #         self.update_machineSpec()

        #         with open(self.path2boptPython+'/codes3/machine_simulation.json', 'r', encoding='utf-8') as f:
        #             self.bopt_machine_spec_dict = json.load(f, object_pairs_hook=OrderedDict) # https://stackoverflow.com/questions/10844064/items-in-json-object-are-out-of-order-using-json-dumps/23820416
        #         self.ui.comboBox_FEAConfig.addItems(self.bopt_machine_spec_dict.keys())
        #         self.ui.comboBox_FEAConfig.activated.connect(lambda: AppFunctions.update_FEAConfig(self))
        #         self.update_FEAConfig()
        #     except Exception as e:
        #         print(str(e))
        #         print('[Warn] Skip FEA-based Optimization')
        #         pass


        '''tab_8: Swarm Analyzer
        '''
        # path = self.path2boptPython + self.ui.lineEdit_path2CollectionFolder.text()
        # list_path2SwarmDataOfTheSpecification = []
        # list_specifications = []
        # for root, dirs, files in os.walk(path):
        #     for file in files:
        #         if 'swarm_data.txt' in file:
        #             # print(root)
        #             list_path2SwarmDataOfTheSpecification.append(root)
        #             normpath = os.path.normpath(root)
        #             specification = normpath.split(os.sep)[-1].replace('_', ' ')
        #             list_specifications.append(specification)
        #             # print(specification)
        # self.ui.comboBox_ListOfSwarmData.addItems(list_specifications)

        # def test():
        #     cmd = f"streamlit run {__file__[:-7]}../visualize/streamlitSwarmAnalyzer.py"
        #     print(cmd)
        #     os.system(cmd)
        #     # child = subprocess_cmd(cmd)
        #     # rc = child.returncode
        #     # if rc == 0:
        #     #     return rc
        #     # else:
        #     #     raise Exception('The returncode is %d'%(rc))
        # self.ui.pushButton_runStreamlit.clicked.connect(test)

        '''menu
        '''
        # # Style sheet
        # self.ui.actionDark.triggered.connect(lambda: toggle_stylesheet("QDarkStyleSheet.qss")) # need to use "./stylesheet/QDarkStyleSheet.qss" if pkg_resources is not used in toggle_stylesheet.py
        # self.ui.actionLight.triggered.connect(lambda: toggle_stylesheet(""))

        # # View
        # self.bool_showTabs = [True]*8
        # def showOrHideTab(tabIndices):
        #     for tabIndex in tabIndices:
        #         status = self.bool_showTabs[tabIndex]
        #         self.ui.tabWidget.setTabEnabled(tabIndex, not status)
        #         self.bool_showTabs[tabIndex] = not status
        #     self.ui.tabWidget.setStyleSheet("QTabBar::tab::disabled {width: 0; height: 0; margin: 0; padding: 0; border: none;} ")
        # self.ui.actionControl_Simulation.triggered.connect(lambda :showOrHideTab(range(5)))
        # self.ui.actionPlots             .triggered.connect(lambda :showOrHideTab([5]))
        # self.ui.actionFEA_Simulation    .triggered.connect(lambda :showOrHideTab([6,7]))
        # if not self.ui.actionControl_Simulation.isChecked():
        #     showOrHideTab(range(5))
        # if not self.ui.actionPlots.isChecked():
        #     showOrHideTab([5])
        # if not self.ui.actionFEA_Simulation.isChecked():
        #     showOrHideTab([6,7])

        # Save
        @decorator_status(status='Saving')
        def save_data_and_source_files(self):
            import shutil, glob
            target_dir = self.path2acmsimc+'/dat/'+self.ui.lineEdit_OutputDataFileName.text()+'/'
            if not os.path.exists(target_dir):         os.makedirs(target_dir)
            if not os.path.exists(target_dir+'/src/'): os.makedirs(target_dir+'/src/')
            shutil.copy(self.path2acmsimc+'/dat/'+self.data_file_name, target_dir)
            shutil.copy(self.path2acmsimc+'/dat/info.dat', target_dir)
            for file in glob.glob(self.path2acmsimc+'/c/*.c'): shutil.copy(file, target_dir+'/src/')
            for file in glob.glob(self.path2acmsimc+'/c/*.h'): shutil.copy(file, target_dir+'/src/')

            # save waveform plot
            # self.ui.MplWidget_ACMPlot.fig.savefig(target_dir+'/waveforms.pdf', dpi=300, bbox_inches='tight', pad_inches=0)

            # export plot menu as python codes
            with open(target_dir+'/plot.py', 'w') as f:
                f.write(get_global_plot_script(*AppFunctions.decode_labelsAndSignals(self)))

            UIFunctions.labelTitle(self, f'Main Window - emachinery - Idling')
        # self.ui.actionSave_dat.triggered.connect(lambda: save_data_and_source_files()) # There is no menu anymore in modern GUI design
        self.ui.pushButton_SaveAtTop.clicked.connect(lambda: save_data_and_source_files(self))



        '''MainWindow
        '''
        # self.setWindowTitlre("Electric Machinery")
        self.setWindowTitle("Figure: Electric Machinery")

        '''
        todo
        '''
        # read in c header file and figure out what are the possible labels

    ''' Utility '''
    def load_configini(self):
        if self.filepath_to_configini is None:
            self.filepath_to_configini = pkg_resources.resource_filename(__name__, f'config_{AppFunctions.get_mtype(self)}.json') # updated in AppFunctions.comboActivate_machineType(self)
        with open(self.filepath_to_configini, 'r') as f:
            self.configini = json.load(f)
    def load_configlob(self):
        if self.filepath_to_configlob is None:
            self.filepath_to_configlob = pkg_resources.resource_filename(__name__, 'config_global.json')
        with open(self.filepath_to_configlob, 'r') as f:
            self.configlob = json.load(f)
    def get_mtype(self, bool_always_true_bug=None, bool_also_return_index=False):

        if 'Induction Machine' in self.ui.comboBox_MachineType.currentText():
            mtype = 'im'
            mtypeIndex = 0
        elif 'Synchronous Machine' in self.ui.comboBox_MachineType.currentText():
            mtype = 'pmsm'
            mtypeIndex = 1
        else:
            raise 'Unknown machine type'
        if bool_also_return_index:
            return mtype, mtypeIndex
        else:
            return mtype
    # def user_shortcut(self, event):
    #     print('app_functions: pass to mpl toolbar,', event.text())
    #     mpl.backend_bases.key_press_handler(event, self.ui.MplWidget_ACMPlot.canvas, self.scope_toolbar)

    ''' PI Regulator Tuning '''
    @Slot()
    def run_series_pid_tuner(self):
        # Specify your desired damping factor
        delta = eval(self.ui.lineEdit_dampingFactor_delta.text())
        # Specify your desired speed closed-loop bandwidth
        desired_VLBW_HZ = eval(self.ui.lineEdit_desiredVLBW.text())

        # Update CL_TS and CL_VS
        self.motor_dict['CL_TS'] = eval(self.ui.lineEdit_CLTS.text())
        self.motor_dict['VL_TS'] = eval(self.ui.lineEdit_VLTS.text())

        currentPI, speedPI, 上位机电流PI, 上位机速度PI, tuple_designedMagPhaseOmega, BW_in_Hz = tuner.iterate_for_desired_bandwidth(delta, desired_VLBW_HZ, self.motor_dict)

        currentKp, currentKi     = currentPI
        speedKp, speedKi         = speedPI
        上位机电流KP, 上位机电流KI = 上位机电流PI
        上位机速度KP, 上位机速度KI = 上位机速度PI
        self.C2C_designedMagPhaseOmega, self.C2V_designedMagPhaseOmega, self.V2V_designedMagPhaseOmega = tuple_designedMagPhaseOmega
        CLBW_Hz, VLBW_Hz, CutOff_Hz = BW_in_Hz

        self.ui.lineEdit_CLBW        .setText(f'{CLBW_Hz:g}')
        self.ui.lineEdit_designedVLBW.setText(f'{VLBW_Hz:g}')
        self.ui.lineEdit_currentKP   .setText(f'{currentKp:g}')
        self.ui.lineEdit_currentKI   .setText(f'{currentKi:g}')
        self.ui.lineEdit_speedKP     .setText(f'{speedKp:g}')
        self.ui.lineEdit_speedKI     .setText(f'{speedKi:g}')
        self.ui.lineEdit_PC_currentKP.setText(f'{上位机电流KP:g}')
        self.ui.lineEdit_PC_currentKI.setText(f'{上位机电流KI:g}')
        self.ui.lineEdit_PC_speedKP  .setText(f'{上位机速度KP:g}')
        self.ui.lineEdit_PC_speedKI  .setText(f'{上位机速度KI:g}')
    @Slot()
    def get_control_dict(self):

        self.control_dict["currentPI"] = (eval(self.ui.lineEdit_currentKP.text()), eval(self.ui.lineEdit_currentKI.text()))
        self.control_dict["speedPI"]   = (eval(self.ui.lineEdit_speedKP.text()),   eval(self.ui.lineEdit_speedKI.text()))
        # print(f'\n\n\
        #     #define CURRENT_KP {currentKp:g}\n\
        #     #define CURRENT_KI {currentKi:g}\n\
        #     #define CURRENT_KI_CODE (CURRENT_KI*CURRENT_KP*CL_TS)\n\
        #     #define SPEED_KP {speedKp:g}\n\
        #     #define SPEED_KI {speedKi:g}\n\
        #     #define SPEED_KI_CODE (SPEED_KI*SPEED_KP*VL_TS)\n')

        self.list__checkedExcitation = [radioButton.isChecked() for radioButton in self.list__radioButton4Excitation]
        self.control_dict['ExcitationType'] = np.argmax(self.list__checkedExcitation)

        # pass to console
        AppFunctions.console_push_variable(self, {'control_dict':self.control_dict})

        AppFunctions.console_push_variable(self, {'tuner_trick':
            ''' (1) A value of damping factor (δ) equal to 1.0 corresponds to the condition where the velocity open-loop gain intercepts 0 dB right at the frequency of the current controller bandwidth. This results in pole/zero cancellation at this frequency with a phase margin of zero. It goes without saying that zero phase margin equals bad things for your system. \n
                (2) Where "δ" we will define as the damping factor. The larger δ is, the further apart the zero corner frequency and the current loop pole will be. And the further apart they are, the phase margin is allowed to peak to a higher value in-between these frequencies. This improves stability at the expense of speed loop bandwidth. If δ = 1, then the zero corner frequency and the current loop pole are equal, which results in pole/zero cancellation and the system will be unstable. Theoretically, any value of δ > 1 is stable since phase margin > 0. However, values of δ close to 1 result in severely underdamped performance.\n
                (3) In short, δ > 1 gives positive phase margin and the larger δ gets, the larger the phase margin becomes, and at the same time, the velocity performance would become sluggish (i.e., you will need to increase your current bandwidth to really high to achieve higher velocity bandwidth).\n
            '''})

        # print(self.control_dict, end='\n'*2)
        return self.control_dict
    @Slot()
    def get_sweepFreq_dict(self):

        self.sweepFreq_dict["max_freq"] = eval(self.ui.lineEdit_maxFreq2Sweep.text())
        self.sweepFreq_dict["init_freq"] = 2
        self.sweepFreq_dict["SWEEP_FREQ_C2V"] = self.ui.radioButton_openLoop.isChecked() # speed open loop
        self.sweepFreq_dict["SWEEP_FREQ_C2C"] = self.ui.radioButton_currentLoopOnly.isChecked()

        # pass to console
        AppFunctions.console_push_variable(self, {'sweepFreq_dict':self.sweepFreq_dict})

        # print(self.sweepFreq_dict, end='\n'*2)
        return self.sweepFreq_dict
    @Slot()
    def update_BodePlot(self):
        try:
            self.data_file_name
        except AttributeError as e:
            print('\t[Warning]: run C based simulation first with Sweep Frequency excitation first.')
            return 
        dot_dat_file_dir = self.path2acmsimc+'/dat/'+self.data_file_name
        # print(self.motor_dict)
        # print(self.sweepFreq_dict)
        ret = analyzer.analyze(dot_dat_file_dir, self.motor_dict, self.sweepFreq_dict)
        if ret is None:
            msg = QMessageBox()
            msg.setWindowTitle("Error")
            msg.setText('Output file: '+dot_dat_file_dir+' does not exist.')
            msg.setIcon(QMessageBox.Critical)
            x = msg.exec_()
        else:
            # 1. Plot simualted Bode plot
            dB, Deg, Freq, max_freq = ret
            # for el in ret:
            #     print(el)

            self.ui.MplWidget_bodePlot.canvas.figure.clf()
            ax = self.ui.MplWidget_bodePlot.canvas.figure.add_subplot(111)
            ax.plot(Freq, dB, '--.', label=self.data_file_name)

            if self.sweepFreq_dict["SWEEP_FREQ_C2V"]:
            # Open-Loop

                # C2V
                ax.set_ylabel('Velocity / Current open-loop-tf amplitude [dB] (elec.rad/s/Apk)')
            else:
            # Closed-Loop

                # Bandwidth@-3dB
                index, value = analyzer.find_nearest(dB, -3) # find -3dB freq
                VLBW_Hz = Freq[index]
                ax.text(VLBW_Hz, -5, f'{VLBW_Hz:.0f} Hz', color='red', fontsize=20)
                ax.plot([0,max_freq], [-3, -3], 'k--')

                if self.sweepFreq_dict["SWEEP_FREQ_C2C"]:
                    # C2C
                    ax.set_ylabel('Current closed-loop-tf amplitude [dB]')
                else:
                    # V2V
                    ax.set_ylabel('Velocity closed-loop-tf amplitude [dB]')
            ax.set_xscale('log')
            ax.set_xlabel('Frequency [Hz]')

            # 2. Plot designed Bode plot
            if self.sweepFreq_dict["SWEEP_FREQ_C2V"]:
                # C2V
                mag, phase, omega = self.C2V_designedMagPhaseOmega
            elif self.sweepFreq_dict["SWEEP_FREQ_C2C"]:
                # C2C
                mag, phase, omega = self.C2C_designedMagPhaseOmega
            else:
                # V2V
                mag, phase, omega = self.V2V_designedMagPhaseOmega
            index_max_freq = sum(omega/(2*np.pi) < max_freq)
            ax.plot((omega/(2*np.pi))[:index_max_freq], 20*np.log10(mag[:index_max_freq]), '-.', label=f'designed:$\\delta={eval(self.ui.lineEdit_dampingFactor_delta.text())}$')

            # # 3. Plot measured Bode plot
            # fname = r'D:\ISMC\SweepFreq\Jupyter\VLBW_Hz-Data/' + 'BiasSine500rpm' + data_file_name[data_file_name.find(data_file_name_prefix)+len(data_file_name_prefix)+len('-CLOSED-@'):-4]+'.txt'
            # try:
            #     CL_VL_TF, list_phase_difference, list_qep_max_frequency, max_freq = Experiment.analyze_experimental_measurements(fname)
            # except FileNotFoundError as e:
            #     raise e
            #     print(str(e))
            #     pass
            # except Exception as e:
            #     raise e
            # finally:
            #     index, value = Experiment.find_nearest(CL_VL_TF, -3) # find -3dB freq
            #     VLBW_Hz = list_qep_max_frequency[index]
            #     plt.text(VLBW_Hz, -5, f'{VLBW_Hz:.0f} Hz', color='purple', fontsize=20)
            #     plt.plot(list_qep_max_frequency, CL_VL_TF, '--.', label=fname)

            ax.legend()

        # analyzer.folder(self.data_file_name, self.motor_dict, data_file_name_prefix=self.motor_dict['data_file_name_prefix'])

        # ax.plot(time, signal, '-.', lw=1, label=key)
        # ax.set_ylabel(self.list__label[i])
        # ax.legend(loc='lower right')

        # ax.set_xlabel('Time [s]')
        # ax.set_ylabel('Time [s]')

        # adjust height per number of traces
        # self.ui.MplWidget_bodePlot.setMinimumSize(QtCore.QSize(500, 200*no_traces))

        self.ui.MplWidget_bodePlot.canvas.draw()



    ''' C-based Simulation '''
    @Slot() # Plot Menu
    def update_ACMPlotLabels_and_ACMPlotSignals(self, bool_always_true_bug=True, bool_re_init=False, mtype=None, configini=None):

        # selected = self.ui.comboBox_PlotSettingSelect.currentText()
        # print('selected:', selected)

        if configini is None:
            configini = self.configini
        if mtype is None:
            mtype = AppFunctions.get_mtype(self)

        ACMPlotNameDict = configini[f'{mtype}-PlotSettingNameDict']
        ACMPlotSelect   = configini[f'{mtype}-PlotSettingSelect']
        print('[app_functions] DEBUG!!', ACMPlotSelect)
        print(ACMPlotNameDict)

        # 初始化（电机类型切换的时候也得运行）
        if bool_re_init:

            # 产生下拉菜单，最多21个，可修改。
            self.ui.comboBox_PlotSettingSelect.clear()
            list_of_strings = [f'{mtype}_default'] \
                            + [f'{mtype}_user{key}: {ACMPlotNameDict[key] if key in ACMPlotNameDict.keys() else ""}' for key in ["%02d"%(i) for i in range(21)] ]
                            # 神经病，写成这样一大串谁看得懂……
            self.ui.comboBox_PlotSettingSelect.addItems(list_of_strings)

            # 为了重新启动以后能记住上一次所选择的PlotSetting
            for i in range(self.ui.comboBox_PlotSettingSelect.count()):
                if ACMPlotSelect in self.ui.comboBox_PlotSettingSelect.itemText(i):
                    self.ui.comboBox_PlotSettingSelect.setCurrentIndex(i)
                    self.ui.lineEdit_plotSettingName.setText(ACMPlotNameDict[ACMPlotSelect])
                    break

        # Read in ACM Plot Settings
        # 根据所选择的配置更新ACMPlot绘图信号列表
        selected = self.ui.comboBox_PlotSettingSelect.currentText().split(':')[0] # 'im_user:12212'.split(":")[0] -> im_user 
        last_two_digits = selected[-2:]
        # 更新绘图标签和信号变量名
        self.filepath_to_ACMPlotLabels  = pkg_resources.resource_filename(__name__, f'./plot_setting_files/labels_{selected}.txt')
        self.filepath_to_ACMPlotSignals = pkg_resources.resource_filename(__name__, f'./plot_setting_files/signals_{selected}.txt')
        self.ui.lineEdit_path2ACMPlotLabels.setText(f'./plot_setting_files/labels_{selected}.txt')
        self.ui.lineEdit_path2ACMPlotSignals.setText(f'./plot_setting_files/signals_{selected}.txt')
        # 更新绘图配置名称
        try:
            self.ui.lineEdit_plotSettingName.setText(ACMPlotNameDict[last_two_digits])
        except Exception as e:
            print('[ignore]', str(e))
        try:
            with open(self.filepath_to_ACMPlotLabels, 'r') as f:
                self.ui.plainTextEdit_ACMPlotLabels.clear()
                self.ui.plainTextEdit_ACMPlotLabels.appendPlainText(f.read())
            with open(self.filepath_to_ACMPlotSignals, 'r') as f:
                self.ui.plainTextEdit_ACMPlotDetails.clear()
                self.ui.plainTextEdit_ACMPlotDetails.appendPlainText(f.read())
        except FileNotFoundError as e:
            with open(self.filepath_to_ACMPlotLabels, 'w') as f:
                pass
            with open(self.filepath_to_ACMPlotLabels, 'r') as f:
                self.ui.plainTextEdit_ACMPlotLabels.clear()
                self.ui.plainTextEdit_ACMPlotLabels.appendPlainText(f.read())
            with open(self.filepath_to_ACMPlotSignals, 'w') as f:
                pass
            with open(self.filepath_to_ACMPlotSignals, 'r') as f:
                self.ui.plainTextEdit_ACMPlotDetails.clear()
                self.ui.plainTextEdit_ACMPlotDetails.appendPlainText(f.read())
        except Exception as e:
            raise e
            # print('ACMPlot settings are not found. Will use the default instead.')

    def save_Config4CBasedSimulation(self):
        self.bool_CbasedSimulationDone = False

        # 读取需要记住的用户输入
        self.configini['MachineNameIndex'] = self.ui.comboBox_MachineName.currentIndex()
        self.configini['ControlStrategy'] = self.ui.lineEdit_ControlStrategy.text()
        self.configini['CLTS'] = self.ui.lineEdit_CLTS.text()
        self.configini['VLTS'] = self.ui.lineEdit_VLTS.text()
        self.configini['EndTime'] = self.ui.lineEdit_EndTime.text()
        self.configini['LoadInertiaPercentage'] = self.ui.lineEdit_LoadInertiaPercentage.text()
        self.configini['LoadTorque'] = self.ui.lineEdit_LoadTorque.text()
        self.configini['ViscousCoefficient'] = self.ui.lineEdit_ViscousCoefficient.text()
        self.configini['FluxCmdDetails'] = self.ui.lineEdit_FluxCmdDetails.text()
        # self.configini['FluxCmdSinePartPercentage'] = self.ui.lineEdit_FluxCmdSinePartPercentage.text()
        # self.configini['DCBusVoltage'] = self.ui.lineEdit_DCBusVoltage.text()
        self.configini['OutputDataFileName'] = self.ui.lineEdit_OutputDataFileName.text()
        mtype, mtypeIndex = AppFunctions.get_mtype(self, bool_also_return_index=True)
        self.configini['MachineTypeIndex'] = mtypeIndex
        self.configini[f'{mtype}-PlotSettingSelect'] = self.ui.comboBox_PlotSettingSelect.currentText().split(':')[0][-2:] # last_two_digits
        # self.configini[f'{mtype}-PlotSettingNameDict'] = dict({'09': 'untitled'})
        self.configini[f'{mtype}-PlotSettingNameDict'].update({self.configini[f'{mtype}-PlotSettingSelect']: self.ui.lineEdit_plotSettingName.text()})
        print('[app_functions] DEBUG', self.ui.lineEdit_plotSettingName.text())


        # parameteric analysis
        self.configini['PANames'] = self.ui.plainTextEdit_PANames.toPlainText()
        self.configini['PAValues'] = self.ui.plainTextEdit_PAValues.toPlainText()

        # uncertainty
        if "Induction Machine" in self.ui.comboBox_MachineType.currentText():
            self.configini['uncertainty']["rs"]     = self.ui.tableWidget_Uncertainty.item(0, 0).text()
            self.configini['uncertainty']["rreq"]   = self.ui.tableWidget_Uncertainty.item(1, 0).text()
            self.configini['uncertainty']["Lmu"]    = self.ui.tableWidget_Uncertainty.item(2, 0).text()
            self.configini['uncertainty']["Lsigma"] = self.ui.tableWidget_Uncertainty.item(3, 0).text()
        elif "Synchronous Machine" in self.ui.comboBox_MachineType.currentText():
            self.configini['uncertainty']["R"]      = self.ui.tableWidget_Uncertainty.item(0, 0).text()
            self.configini['uncertainty']["Ld"]     = self.ui.tableWidget_Uncertainty.item(1, 0).text()
            self.configini['uncertainty']["Lq"]     = self.ui.tableWidget_Uncertainty.item(2, 0).text()
            self.configini['uncertainty']["KE"]     = self.ui.tableWidget_Uncertainty.item(3, 0).text()

        with open(self.filepath_to_configini, 'w') as f:
            json.dump(self.configini, f, ensure_ascii=False, indent=4)
    @Slot()
    def save_path2acmsimc(self):
        self.configlob['path2acmsimc'] = self.ui.lineEdit_path2acmsimc.text()

        if os.path.exists(self.configlob['path2acmsimc']):
            self.path2acmsimc = self.configlob['path2acmsimc']
        else:
            print(f'''\tPath "{self.configlob['path2acmsimc']}" does not exist. Will use default C codes instead.''')
            self.configlob['path2acmsimc'] = self.path2acmsimc = self.default_path2acmsimc = os.path.dirname(__file__) + '/../acmsimcv5' # the default code comes along with the emachinery package

        # the top label
        self.ui.label_top_info_1.setText(self.path2acmsimc)

        with open(self.filepath_to_configlob, 'w') as f:
            json.dump(self.configlob, f, ensure_ascii=False, indent=4)

    @Slot()
    def update_PADataFileList(self):
        # print('Not implemented: update_PADataFileList')
        try:
            data_file_name_list = AppFunctions.getDataFileNameList4PA(self)
        except Exception as e:
            print(e)
            print('there are no such file')
            return
        self.ui.comboBox_PADataFileSelected.clear()
        self.ui.comboBox_PADataFileSelected.addItems(data_file_name_list)

    def get_data_file_name(self):

        上位机电流KP = eval(self.ui.lineEdit_PC_currentKP.text())
        上位机电流KI = eval(self.ui.lineEdit_PC_currentKI.text())
        上位机速度KP = eval(self.ui.lineEdit_PC_speedKP  .text())
        上位机速度KI = eval(self.ui.lineEdit_PC_speedKI  .text())

        if not os.path.exists(self.path2acmsimc+'/dat'):
            os.makedirs(self.path2acmsimc+'/dat')

        # get ExcitationType
        self.list__checkedExcitation = [radioButton.isChecked() for radioButton in self.list__radioButton4Excitation]
        self.control_dict['ExcitationType'] = np.argmax(self.list__checkedExcitation)

        if self.control_dict['ExcitationType'] == 2:
            if not os.path.exists(self.path2acmsimc+'/dat/Closed'):
                os.makedirs(self.path2acmsimc+'/dat/Closed')
            if not os.path.exists(self.path2acmsimc+'/dat/Open'):
                os.makedirs(self.path2acmsimc+'/dat/Open')
            if self.sweepFreq_dict["SWEEP_FREQ_C2V"]:
                self.data_file_name = f"../dat/Open/{  self.motor_dict['data_file_name_prefix']}-C2V-@{self.sweepFreq_dict['max_freq']:.0f}Hz-{上位机电流KP:.0f}-{上位机电流KI:.0f}-{上位机速度KP:.0f}-{上位机速度KI:.0f}.dat"
            else:
                if self.sweepFreq_dict["SWEEP_FREQ_C2C"]:
                    self.data_file_name = f"../dat/Closed/{self.motor_dict['data_file_name_prefix']}-C2C-@{self.sweepFreq_dict['max_freq']:.0f}Hz-{上位机电流KP:.0f}-{上位机电流KI:.0f}-{上位机速度KP:.0f}-{上位机速度KI:.0f}.dat"
                else:
                    self.data_file_name = f"../dat/Closed/{self.motor_dict['data_file_name_prefix']}-V2V-@{self.sweepFreq_dict['max_freq']:.0f}Hz-{上位机电流KP:.0f}-{上位机电流KI:.0f}-{上位机速度KP:.0f}-{上位机速度KI:.0f}.dat"

        else:
            # file name with PI coefficients
            self.data_file_name = f"../dat/{self.motor_dict['data_file_name_prefix']}-{上位机电流KP:.0f}-{上位机电流KI:.0f}-{上位机速度KP:.0f}-{上位机速度KI:.0f}.dat"
        # print('self.data_file_name:', self.data_file_name, end='\n'*2)
        return self.data_file_name
    # read in .dat file for plot
    def get_dataFrame(self, data_file_name):

        # info.dat
        # df_info = pd.read_csv(path+"/dat/info.dat", na_values = ['1.#QNAN', '-1#INF00', '-1#IND00'])
        # data_file_name = df_info['DATA_FILE_NAME'].values[0].strip()

        # 这个大的数据文件产生有滞后，可能文件还没生成，程序就已经跑到这里开始调用read_csv了！
        # 所以要判断一下，数据文件应该是在info.dat之后生成的。
        # while True:
        #     print('st_mtime 1:', os.stat(path+'/dat/'+data_file_name).st_mtime )
        #     print('st_mtime 2:', os.stat(path+"/dat/info.dat").st_mtime)
        #     if os.stat(path+'/dat/'+data_file_name).st_mtime < os.stat(path+"/dat/info.dat").st_mtime:
        #         print('Sleep in ACMPlot.py')
        #         sleep(0.1)
        #         break    

        # moved outside of this function
        # data_file_name = AppFunctions.get_data_file_name(self)

        # ???.dat
        # data_file_name = path+'/dat/'+data_file_name
        df_profiles = pd.read_csv(self.path2acmsimc+'/dat/'+data_file_name, na_values = ['1.#QNAN', '-1#INF00', '-1#IND00'])
        no_samples = df_profiles.shape[0]
        no_traces  = df_profiles.shape[1]
        # print(data_file_name)

        return df_profiles, no_samples, no_traces 
    # plot as animation
    @Slot()
    def clicked__pushButton_ACMPlotHere(self):
        AppFunctions.update_ACMPlot(self, data_file_name=self.ui.comboBox_PADataFileSelected.currentText())

    @decorator_status(status='Loading Data')
    def update_ACMPlot(self, bool_always_false_bug=None, data_file_name=None):
        # UIFunctions.labelTitle(self, 'Main Window - emachinery - Loading Data')
        # if(not self.bool_import_ACMPlot):
        #     sys.path.append(self.path2acmsimc)
        #     import ACMPlot

        if data_file_name is None:
            data_file_name = self.data_file_name

        # 需要动画的原因是画图的程序和main.exe是同时运行的，数据还没完整就开始画了，所以要动画。
        def ACMアニメ4C(i):
            df_profiles, no_samples, no_traces = AppFunctions.get_dataFrame(self, data_file_name)

            # 上次读的csv和这次读的csv中的数据行数没有变化，那么认为时是否终止画图了（且这一次也不需要画了）
            if self.last_no_samples == no_samples:
                self.last_no_samples = None
                self.anim.event_source.stop()
                print('\tStop ACMPlot animation for C.\n----------\n\n')
                self.bool_CbasedSimulationDone = True
                UIFunctions.labelTitle(self, 'Main Window - emachinery - Simulation Done')

                # switch to self.ui.page_scope to see the waveforms
                UIFunctions.selectStandardMenu(self, "btn_cBasedSimulation")
                self.ui.stackedWidget.setCurrentWidget(self.ui.page_scope)

            else:
                self.last_no_samples = no_samples

                print('\t', df_profiles.shape, end=' | ')
                print('\tread in', self.path2acmsimc+'/dat/'+data_file_name)
                # print(df_profiles)


            time = np.arange(1, no_samples+1) * self.motor_dict['DOWN_SAMPLE'] * self.motor_dict['CL_TS']

            self.ui.MplWidget_ACMPlot.canvas.figure.clf()
            trace_counter = 0

            # for i, key in enumerate(df_profiles.keys()):
            # for i, key in enumerate(self.list__label):
            # 遍历子图们
            first_ax = None
            for i, number_of_traces_per_subplot in enumerate(list__number_of_traces_per_subplot):
                ax = self.ui.MplWidget_ACMPlot.canvas.figure.add_subplot(number_of_subplot, 1, 1+i, sharex=first_ax)
                if first_ax is None:
                    first_ax = ax

                # 遍历某一张子图中的波形们
                for j in range(number_of_traces_per_subplot):
                    key = details[trace_counter]
                    # print('key:', key)
                    try:
                        signal = df_profiles[key]
                    except Exception as e:
                        print('debug:', df_profiles.keys())
                        raise e
                    trace_counter += 1
                    try:
                        ax.plot(time, signal, linestyle=self.cjh_linestyles[j], color=self.cjh_colors[j], lw=1.5, label=key, alpha=0.5, zorder=100+trace_counter) # 如果是减去trace_counter，那么就是后来的画在下面
                    except ValueError as e:
                        print('ValueError during ax.plot():', e, '\nThis is known issue and will ignore and continue.') # ValueError: could not convert string to float: '3.33723e-'
                        pass
                # print(i)
                # print('DEBUG:', list__label[i], i, list__label)
                ax.set_ylabel(list__label[i])
                ax.legend(loc='lower right').set_zorder(202)
                ax.grid(True)
            ax.set_xlabel('Time [s]')

            # axes = self.ui.MplWidget_ACMPlot.canvas.figure.get_axes()

        # before animation, some global information is set here first
        details, list__number_of_traces_per_subplot, list__label = AppFunctions.decode_labelsAndSignals(self)
        number_of_subplot = len(list__number_of_traces_per_subplot)

        # plot it once (need to sleep for the data to complete)
        # ACMアニメ4C(0)

        # animate it (it is okay for incomeplete data)
        self.anim = animation.FuncAnimation(self.ui.MplWidget_ACMPlot.canvas.figure, ACMアニメ4C, interval=500)

        # adjust height per number of traces
        df_profiles, no_samples, no_traces = AppFunctions.get_dataFrame(self, data_file_name)
        AppFunctions.setACMPlotHeight(self, number_of_subplot)
        # draw
        self.ui.MplWidget_ACMPlot.canvas.draw()

        # save waveform plot
        # self.ui.MplWidget_ACMPlot.canvas.print_figure(self.path2acmsimc+'/dat/aaawaveforms.pdf', dpi=300, bbox_inches='tight', pad_inches=0)

        # # lissajous plot
        # if self.checkBox_LissajousPlot.isChecked():
        #     signals = []
        #     for signal_name_pair in eval(self.ui.plainTextEdit_LissajousPlotSignals.toPlainText()):
        #         x_name, y_name = signal_name_pair
        #         signals.append( (df_profiles[x_name], df_profiles[y_name]) )
        #     self.update_LissajousPlot(signals=signals, no_samples=no_samples)

    def setACMPlotHeight(self, number_of_subplot):
        self.ui.MplWidget_ACMPlot.setMinimumSize(QtCore.QSize(500, number_of_subplot*200))
        # mpl.rcParams["figure.figsize"] = (10, number_of_subplot*10) #(default: [6.4, 4.8]) # no effect
        # self.ui.MplWidget_ACMPlot.fig.figsize=(8, number_of_subplot*5) # no effect

    @Slot()
    def radioChecked_ACMExcitation(self):
        # This is not needed as there is an option for radioButton as autoExclusive
        # temp = [radioButton.isChecked() for radioButton in self.list__radioButton4Excitation]
        # if sum(temp)>=2:
        #     index = 0
        #     for new, old in zip(temp, self.list__checkedExcitation):
        #         # 原来已经被勾上的
        #         if new == old == True:
        #             self.list__radioButton4Excitation[index].setChecked()
        #         # 刚刚被勾上的
        #         if new != old and new == True:
        #             self.control_dict['ExcitationType'] = index
        #         index += 1

        self.list__checkedExcitation = [radioButton.isChecked() for radioButton in self.list__radioButton4Excitation]
        self.control_dict['ExcitationType'] = np.argmax(self.list__checkedExcitation)

        # sweep frequency
        if self.control_dict['ExcitationType'] == 2:
            self.ui.groupBox_sweepFrequency.setEnabled(True)
        else:
            self.ui.groupBox_sweepFrequency.setEnabled(False)
            self.ui.radioButton_openLoop.setChecked(False)
            self.ui.radioButton_currentLoopOnly.setChecked(False)
    @Slot()
    def radioChecked_Settings4SweepFrequency(self):
        # This is not needed as there is an option for radioButton as autoExclusive
        if self.ui.radioButton_openLoop.isChecked() and self.ui.radioButton_currentLoopOnly.isChecked():
            msg = QMessageBox()
            msg.setWindowTitle("Warning")
            msg.setText("Not support open-loop and current-loop-only at the same time!\nPlease select only one of them.")
            msg.setIcon(QMessageBox.Warning)
            x = msg.exec_()
            self.ui.radioButton_openLoop.setChecked(False)
            self.ui.radioButton_currentLoopOnly.setChecked(False)
    def decode_labelsAndSignals(self):
        # #define DATA_LABELS
        labels = [el.strip() for el in self.ui.plainTextEdit_ACMPlotLabels.toPlainText().split('\n') if el.strip()!='']
        # avoid using ',' or ';' in label, because comma will be interpreted as new column by pandas
        # labels = [el.replace(',','|') for el in labels]
        # self.list__label = labels
        # print(labels)

        details = self.ui.plainTextEdit_ACMPlotDetails.toPlainText()
        # print(details)

        # 每个通道有几条信号？
        list__number_of_traces_per_subplot = []
        for detail in [el.strip() for el in self.ui.plainTextEdit_ACMPlotDetails.toPlainText().split('\n') if el.strip()!='']:
            number_of_traces_per_subplot = len( [el.strip() for el in detail.split(',') if el.strip()!=''] )
            list__number_of_traces_per_subplot.append(number_of_traces_per_subplot)

        # #define DATA_DETAILS
        details = [el.strip() for el in re.split('\n|,', details) if el.strip()!='']
        # self.list__detail = details

        if len(list__number_of_traces_per_subplot) != len(labels):
            print('\t[Warning] missing label or plotting variable.')
            for i in range(len(list__number_of_traces_per_subplot) - len(labels)):
                labels.append(f'No title {i}')

        self.number_of_subplot = len(list__number_of_traces_per_subplot)

        # print(details)
        return details, list__number_of_traces_per_subplot, labels

    # save setting, compile .c and run .exe
    @decorator_status(status='Running') # this will not be updated until this function is done
    def compile_and_run(self, output_fname='main'):
        UIFunctions.labelTitle(self, 'Main Window - emachinery - Compling and Running')

        # compile c and run
        if os.path.exists(self.path2acmsimc+"/dat/info.dat"):
            os.remove(self.path2acmsimc+"/dat/info.dat")

        """ CMake or GNU make? """
        if output_fname == 'main' and builtins.pcname == "HORY-Y730":
            try:
                # 也可以用GMAKE，但是CMAKE编译更快一些
                os.system(f"   cd /d {self.path2acmsimc} \
                            && cmake --build ./cmake-build-debug --target all -- -j 12 \
                            && cd ./cmake-build-debug && acmsimcv5.exe")
            except Exception as e:
                print('\tCMake is not available in Windows system environment path. Will use GNU-Make instead.')
                os.system(f"   cd /d {self.path2acmsimc}/c \
                            && gmake {output_fname} \
                            && start cmd /c {output_fname}")

        else:
            # PA调用时，可能会同时编译出好几个main.exe，这样上一次放着还没跑完的话，就会报占用错误。
            # 目前只能用GMAKE，做法是在makefile里面写了很多不同的make方案。
            os.system(f"   cd /d {self.path2acmsimc}/c \
                        && gmake {output_fname} \
                        && start cmd /c {output_fname}")
        while not os.path.exists(self.path2acmsimc+"/dat/info.dat"):
            # print('sleep for info.dat')
            time.sleep(0.1)

        # reset data used for lissajous plot
        self.signals = None
        self.no_samples = None

    @Slot()
    @decorator_status(status='Configuring') # this will not be updated until this function is done
    def runCBasedSimulation(self, bool_always_true_bug=True, bool_savePlotSetting=True, bool_updatePlotSetting=True, bool_compileAndRun=True):
        # UIFunctions.labelTitle(self, 'Main Window - emachinery - Configuring')
        # self.ui.label_top_info_1.setText('Main Window - emachinery - Configuring')
        AppFunctions.save_Config4CBasedSimulation(self)

        def savePlotSettingSelect():
            with open(  self.filepath_to_ACMPlotLabels, 'w') as f:
                f.write(self.ui.plainTextEdit_ACMPlotLabels.toPlainText())
            with open(  self.filepath_to_ACMPlotSignals, 'w') as f:
                f.write(self.ui.plainTextEdit_ACMPlotDetails.toPlainText())

        def updatePlotSettingSelect(path2acmsimc, details):
            self = None
            with open(path2acmsimc+'/c/ACMSim.h', 'r', encoding='utf-8') as f:
                new_lines = []
                for line in f.readlines():
                    if   '#define DATA_LABELS '    in line: new_lines.append(rf'#define DATA_LABELS "{  ",".join(details)}\n"'       +'\n')
                    elif '#define DATA_DETAILS '   in line: new_lines.append(rf'#define DATA_DETAILS {  ",".join(details)}'          +'\n')
                    elif '#define DATA_FORMAT '    in line: new_lines.append(rf'#define DATA_FORMAT "{("%g,"*len(details))[:-1]}\n"' +'\n')
                    else: new_lines.append(line)
            with open(path2acmsimc+'/c/ACMSim.h', 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        def updateACMConfig(path2acmsimc, motor_dict, control_dict, sweepFreq_dict):
            # print(motor_dict)
            def conditions_to_continue(line):
                # 原来如果有定义这些宏，那就不要了
                if     '#define IM_STAOTR_RESISTANCE' in line \
                    or '#define IM_ROTOR_RESISTANCE' in line \
                    or '#define IM_TOTAL_LEAKAGE_INDUCTANCE' in line \
                    or '#define IM_MAGNETIZING_INDUCTANCE' in line \
                    or '#define IM_FLUX_COMMAND_DC_PART' in line \
                    or '#define IM_FLUX_COMMAND_SINE_PART' in line \
                    or '#define IM_FLUX_COMMAND_SINE_HERZ' in line \
                    or '#define PMSM_RESISTANCE' in line \
                    or '#define PMSM_D_AXIS_INDUCTANCE' in line \
                    or '#define PMSM_Q_AXIS_INDUCTANCE' in line \
                    or '#define PMSM_PERMANENT_MAGNET_FLUX_LINKAGE' in line \
                    or '#define MOTOR_NUMBER_OF_POLE_PAIRS' in line \
                    or '#define MOTOR_RATED_CURRENT_RMS' in line \
                    or '#define MOTOR_RATED_POWER_WATT' in line \
                    or '#define MOTOR_RATED_SPEED_RPM' in line \
                    or '#define MOTOR_SHAFT_INERTIA' in line \
                    or '#define INDIRECT_FOC 1' in line \
                    or '#define MARINO_2005_ADAPTIVE_SENSORLESS_CONTROL 2' in line \
                    or '#define NULL_D_AXIS_CURRENT_CONTROL -1' in line \
                    or '#define MTPA -2' in line \
                    or '// 电机参数' in line \
                    or '// 磁链给定' in line \
                    or '// 铭牌值' in line \
                    or '// 参数误差' in line \
                    or '#define MISMATCH_RS' in line \
                    or '#define MISMATCH_RREQ' in line \
                    or '#define MISMATCH_LMU' in line \
                    or '#define MISMATCH_LSIGMA' in line\
                    or '#define MISMATCH_R' in line \
                    or '#define MISMATCH_LD' in line \
                    or '#define MISMATCH_LQ' in line \
                    or '#define MISMATCH_KE' in line:
                    return True
                else:
                    return False

            # self = None
            NUMBER_OF_STEPS_CL_TS = motor_dict['EndTime']/motor_dict['CL_TS']
            # print('NUMBER_OF_STEPS_CL_TS', NUMBER_OF_STEPS_CL_TS)
            with open(path2acmsimc+'/c/ACMConfig.h', 'r', encoding='utf-8') as f:
                new_lines = []
                for line in f.readlines():
                    # Basic Quantities
                    if   '#define NUMBER_OF_STEPS' in line: new_lines.append(f'#define NUMBER_OF_STEPS {NUMBER_OF_STEPS_CL_TS:.0f}\n'); continue
                    elif '#define CL_TS '          in line: new_lines.append(f'#define CL_TS          ({motor_dict["CL_TS"]:g})\n'); continue
                    elif '#define CL_TS_INVERSE'   in line: new_lines.append(f'#define CL_TS_INVERSE  ({1.0/motor_dict["CL_TS"]:g})\n'); continue
                    elif '#define VL_TS '          in line: new_lines.append(f'#define VL_TS          ({motor_dict["VL_TS"]:g})\n'); continue
                    elif '#define DATA_FILE_NAME'  in line: new_lines.append(f'#define DATA_FILE_NAME "{self.data_file_name}"\n'); continue

                    # Load Related Quantities;
                    elif '#define LOAD_INERTIA'    in line: new_lines.append(f'#define LOAD_INERTIA    {motor_dict["JLoadRatio"]}\n'); continue
                    elif '#define LOAD_TORQUE'     in line: new_lines.append(f'#define LOAD_TORQUE     {motor_dict["Tload"]}\n'); continue
                    elif '#define VISCOUS_COEFF'   in line: new_lines.append(f'#define VISCOUS_COEFF   {motor_dict["ViscousCoeff"]}\n'); continue

                    # Machine Type
                    if "Induction Machine" in self.ui.comboBox_MachineType.currentText():
                        if '#define MACHINE_TYPE' in line: 
                            new_lines.append(f'#define MACHINE_TYPE {1}\n') # 11 or 1
                            # Machine Parameters
                            new_lines.append(f'\t// 电机参数\n')
                            new_lines.append(f'\t#define IM_STAOTR_RESISTANCE        {motor_dict["Rs"]}\n')
                            new_lines.append(f'\t#define IM_ROTOR_RESISTANCE         {motor_dict["Rreq"]}\n')
                            new_lines.append(f'\t#define IM_TOTAL_LEAKAGE_INDUCTANCE {motor_dict["Lsigma"]}\n')
                            new_lines.append(f'\t// 磁链给定\n')
                            new_lines.append(f'\t#define IM_MAGNETIZING_INDUCTANCE   {motor_dict["Lmu"]}\n')
                            new_lines.append(f'\t#define IM_FLUX_COMMAND_DC_PART     {motor_dict["flux_cmd_dc_part"]}\n')
                            new_lines.append(f'\t#define IM_FLUX_COMMAND_SINE_PART   {motor_dict["flux_cmd_sine_part"]}\n')
                            new_lines.append(f'\t#define IM_FLUX_COMMAND_SINE_HERZ   {motor_dict["flux_cmd_sine_herz"]}\n')
                            new_lines.append(f'\t// 铭牌值\n')
                            new_lines.append(f'\t#define MOTOR_NUMBER_OF_POLE_PAIRS  {motor_dict["n_pp"]}\n')
                            new_lines.append(f'\t#define MOTOR_RATED_CURRENT_RMS     {motor_dict["IN"]}\n')
                            new_lines.append(f'\t#define MOTOR_RATED_POWER_WATT      {motor_dict["PW"]}\n')
                            new_lines.append(f'\t#define MOTOR_RATED_SPEED_RPM       {motor_dict["RPM"]}\n')
                            new_lines.append(f'\t#define MOTOR_SHAFT_INERTIA         {motor_dict["J_s"]}\n')
                            new_lines.append(f'\t// 参数误差\n')
                            new_lines.append(f'\t\t#define MISMATCH_RS               {self.configini["uncertainty"]["rs"]}\n')
                            new_lines.append(f'\t\t#define MISMATCH_RREQ             {self.configini["uncertainty"]["rreq"]}\n')
                            new_lines.append(f'\t\t#define MISMATCH_LMU              {self.configini["uncertainty"]["Lmu"]}\n')
                            new_lines.append(f'\t\t#define MISMATCH_LSIGMA           {self.configini["uncertainty"]["Lsigma"]}\n')
                            continue
                        if '#define CONTROL_STRATEGY' in line:
                            # Control Methods
                            new_lines.append(f'\t#define INDIRECT_FOC 1\n')
                            new_lines.append(f'\t#define MARINO_2005_ADAPTIVE_SENSORLESS_CONTROL 2\n')
                            new_lines.append(f'#define CONTROL_STRATEGY {self.ui.lineEdit_ControlStrategy.text()}\n')
                            continue
                    elif "Synchronous Machine" in self.ui.comboBox_MachineType.currentText():
                        if '#define MACHINE_TYPE' in line: 
                            new_lines.append(f'#define MACHINE_TYPE {2}\n')
                            # Machine Parameters
                            new_lines.append(f'\t// 电机参数\n')
                            new_lines.append(f'\t#define PMSM_RESISTANCE                    {motor_dict["Rs"]}\n')
                            new_lines.append(f'\t#define PMSM_D_AXIS_INDUCTANCE             {motor_dict["Ld"]}\n')
                            new_lines.append(f'\t#define PMSM_Q_AXIS_INDUCTANCE             {motor_dict["Lq"]}\n')
                            new_lines.append(f'\t#define PMSM_PERMANENT_MAGNET_FLUX_LINKAGE {motor_dict["KE"]}\n')
                            new_lines.append(f'\t// 铭牌值\n')
                            new_lines.append(f'\t#define MOTOR_NUMBER_OF_POLE_PAIRS         {motor_dict["n_pp"]}\n')
                            new_lines.append(f'\t#define MOTOR_RATED_CURRENT_RMS            {motor_dict["IN"]}\n')
                            new_lines.append(f'\t#define MOTOR_RATED_POWER_WATT             {motor_dict["PW"]}\n')
                            new_lines.append(f'\t#define MOTOR_RATED_SPEED_RPM              {motor_dict["RPM"]}\n')
                            new_lines.append(f'\t#define MOTOR_SHAFT_INERTIA                {motor_dict["J_s"]}\n')
                            new_lines.append(f'\t// 参数误差\n')
                            new_lines.append(f'\t\t#define MISMATCH_R   {self.configini["uncertainty"]["R"]}\n')
                            new_lines.append(f'\t\t#define MISMATCH_LD  {self.configini["uncertainty"]["Ld"]}\n')
                            new_lines.append(f'\t\t#define MISMATCH_LQ  {self.configini["uncertainty"]["Lq"]}\n')
                            new_lines.append(f'\t\t#define MISMATCH_KE  {self.configini["uncertainty"]["KE"]}\n')
                            continue
                        if '#define CONTROL_STRATEGY' in line:
                            # Control Methods
                            new_lines.append(f'\t#define NULL_D_AXIS_CURRENT_CONTROL -1\n')
                            new_lines.append(f'\t#define MTPA -2 // not supported\n')
                            new_lines.append(f'#define CONTROL_STRATEGY {self.ui.lineEdit_ControlStrategy.text()}\n')
                            # new_lines.append(f'#define CONTROL_STRATEGY NULL_D_AXIS_CURRENT_CONTROL')
                            continue

                    # Ignore old Machiner Parameters macros
                    if conditions_to_continue(line): continue

                    # Control Related Quantities
                    if len(control_dict.keys()) > 2: # there could be the case in which only ExcitationType assigned to control_dict
                        # PID Coefficients
                        if   '#define CURRENT_KP '     in line: new_lines.append(f'#define CURRENT_KP ({control_dict["currentPI"][0]:g})\n'); continue
                        elif '#define CURRENT_KI '     in line: new_lines.append(f'#define CURRENT_KI ({control_dict["currentPI"][1]:g})\n'); continue
                        elif '#define SPEED_KP '       in line: new_lines.append(f'#define SPEED_KP ({  control_dict["speedPI"]  [0]:g})\n'); continue
                        elif '#define SPEED_KI '       in line: new_lines.append(f'#define SPEED_KI ({  control_dict["speedPI"]  [1]:g})\n'); continue
                        elif '#define EXCITATION_TYPE' in line: new_lines.append(f'#define EXCITATION_TYPE ({control_dict["ExcitationType"]})\n'); continue
                        elif '#define CURRENT_LOOP_LIMIT_VOLTS' in line: new_lines.append(f'#define CURRENT_LOOP_LIMIT_VOLTS ({motor_dict["Udc"]})\n'); continue

                    # Sweep Frequency Related Quantities
                    if len(sweepFreq_dict.keys()) > 0:
                        if   '#define SWEEP_FREQ_MAX_FREQ'  in line: new_lines.append(f'#define SWEEP_FREQ_MAX_FREQ {     sweepFreq_dict["max_freq"]:.0f}\n'); continue
                        elif '#define SWEEP_FREQ_INIT_FREQ' in line: new_lines.append(f'#define SWEEP_FREQ_INIT_FREQ {    sweepFreq_dict["init_freq"]:.0f}\n'); continue
                        elif '#define SWEEP_FREQ_C2V'       in line: new_lines.append(f'#define SWEEP_FREQ_C2V {"TRUE" if sweepFreq_dict["SWEEP_FREQ_C2V"] else "FALSE"}\n'); continue
                        elif '#define SWEEP_FREQ_C2C'       in line: new_lines.append(f'#define SWEEP_FREQ_C2C {"TRUE" if sweepFreq_dict["SWEEP_FREQ_C2C"] else "FALSE"}\n'); continue

                    # No if-clause is activated, so simply append the line.
                    new_lines.append(line)
            with open(path2acmsimc+'/c/ACMConfig.h', 'w', encoding='utf-8') as f:
                f.writelines(new_lines)

        # update panel inputs
        self.motor_dict = AppFunctions.get_motor_dict(self, self.mj)
        self.control_dict = AppFunctions.get_control_dict(self)
        self.sweepFreq_dict = AppFunctions.get_sweepFreq_dict(self)

        # save
        if bool_savePlotSetting: savePlotSettingSelect()

        # decode labels and signals for plot
        details, _, _ = AppFunctions.decode_labelsAndSignals(self)

        # update path/to/acmsimcv5/c/utility.c
        if bool_updatePlotSetting: updatePlotSettingSelect(self.path2acmsimc, details)
        self.data_file_name = AppFunctions.get_data_file_name(self) # 这里是正式产生 self.data_file_name 的地方哦
        updateACMConfig(self.path2acmsimc, self.motor_dict, self.control_dict, self.sweepFreq_dict)
        print('\t[acmsimc] ACMConfig.h is updated.')

        if self.ui.checkBox_compileAndRun.isChecked() and bool_compileAndRun:
            AppFunctions.compile_and_run(self)

            # Animate ACMPlot
            # print('sleep for .dat file')
            # sleep(2) # it takes time for main.exe to write data into the disk.
            # but we don't need to use sleep() to wait for that anymore, because we have animated ACMPlot now which works well with incomplete data
            AppFunctions.update_ACMPlot(self)
    # def runCBasedSimulation_SweepFrequnecyAnalysis(self):

    ''' C-based Simulation: Parametric Analysis '''
    @Slot()
    def runCBasedSimulation4PA(self, bool_always_false_bug=99999999, bool_=88888888):
        # see the bug clearly
        # print(self, bool_always_false_bug, bool_)

        # 先清除旧的 .dat-00X 文件
        data_file_name_list = AppFunctions.getDataFileNameList4PA(self)
        for data_file_name in data_file_name_list:
            os.remove(self.path2acmsimc+'/dat/'+data_file_name)
            print('Remove', self.path2acmsimc+'/dat/'+data_file_name)

        # Basic Run to make sure everything is up-to-date and saved.
        AppFunctions.runCBasedSimulation(self, bool_compileAndRun=False)
        # if self.bool_CbasedSimulationDone==False:
        #     UIFunctions.labelTitle(self, 'Main Window - emachinery - Sleeping')
        #     sleep(0.2)
        #     print('sleep 0.2 s...')

        # 先根据多个参数的名字，找到它们在文件ACMConfig.h中的行数，即PAIndex。
        PANameTuple = eval(self.ui.plainTextEdit_PANames.toPlainText())
        original_buf = None
        PAIndexList = []
        with open(self.path2acmsimc+'/c/ACMConfig.h', 'r', encoding='utf-8') as f:
            original_buf = list(f.readlines())
            for index, line in enumerate(original_buf):
                for PAName in PANameTuple:
                    if ' ' + PAName + ' ' in line:
                        PAIndexList.append(index)
                        break
        # print('PAIndexList', PAIndexList)
        print('\tPANameTuple:', PANameTuple)

        # 输出数据文件所在行数
        DataFileNameIndex = None
        for i in range(-1,-100, -1):
            if 'DATA_FILE_NAME' in original_buf[i]:
                DataFileNameIndex = i
                break

        # 根据每一个PAValueTuple，更新ACMConfig.h，并编译运行，保存数据。
        count = 0
        for _, PAValueTuple in enumerate(eval(self.ui.plainTextEdit_PAValues.toPlainText())):
            print('\t', PAValueTuple)
            if PAValueTuple == ():
                raise Exception('Error: PAValueTuple is empty.')
            count += 1

            write_buf = copy.deepcopy(original_buf)

            # 打开文件
            with open(self.path2acmsimc+'/c/ACMConfig.h', 'w', encoding='utf-8') as f:

                # 每个参数都要修改ACMConfig.h文件的一行
                for PAName, PAIndex, PAValue in zip(PANameTuple, PAIndexList, PAValueTuple):
                    write_buf[PAIndex] = f'#define {PAName} {PAValue}\n'

                # 修改输出数据文件名
                write_buf[DataFileNameIndex] = f'#define DATA_FILE_NAME "{self.data_file_name}-{_+1:03d}"\n'

                # 写入ACMConfig.h
                f.writelines(write_buf)

            # 编译+运行C
            AppFunctions.compile_and_run(self, output_fname=f'main{_+1}')

        # call with bool_compileAndRun=False), no need to stop self.anim anymore.
        # stop the animation as we are going to plot the canvas for PA
        # self.anim.event_source.stop()

        # 画图
        # sleep(0.5) # wait for the simulation done
        AppFunctions.plot4PA(self, data_file_name_list = [f"{self.data_file_name}-{_+1:03d}" for _ in range(count)])
        AppFunctions.update_PADataFileList(self) # update comboBox_PADataFileSelected
    @Slot()
    def getDataFileNameList4PA(self):
        data_file_name = AppFunctions.get_data_file_name(self)
        target = data_file_name[len("../dat/"):]
        data_file_name_list = ["../dat/"+file for file in os.listdir(self.path2acmsimc+'/dat/') if target in file] #  and 'dat-' in file
        return data_file_name_list
    @Slot()
    def plot4PA(self, bool_always_false_bug=None, data_file_name_list=None):
        # print(bool_always_false_bug, data_file_name_list)

        # 不运行C，直接画图的话
        if data_file_name_list is None:
            data_file_name_list = AppFunctions.getDataFileNameList4PA(self)

        def 类似ACMアニメ4C_但只画第一个信号_j等于0(df_profiles, no_samples, no_traces, PAIndex=None):
            time = np.arange(1, no_samples+1) * self.motor_dict['DOWN_SAMPLE'] * self.motor_dict['CL_TS']
            trace_counter = 0
            first_ax = None
            for i, number_of_traces_per_subplot in enumerate(list__number_of_traces_per_subplot):
                ax = axes[i]
                # ax = self.ui.MplWidget_ACMPlot.canvas.figure.add_subplot(number_of_subplot, 1, 1+i, sharex=first_ax)
                # if first_ax is None:
                #     first_ax = ax

                for j in range(number_of_traces_per_subplot):
                    key = details[trace_counter]
                    signal = df_profiles[key]
                    trace_counter += 1
                    if j==number_of_traces_per_subplot-1: # 我改变主意了，还是画最后一个吧
                        print(len(signal), i, j, key+f'{PAIndex}')
                        ax.plot(time, signal, '-.', lw=1.0, label=key+f'{PAIndex}', alpha=0.75, zorder=100+trace_counter) # 如果是减去trace_counter，那么就是后来的画在下面
                ax.set_ylabel(list__label[i])
                ax.legend(loc='lower right').set_zorder(202)
            ax.set_xlabel('Time [s]')
            return no_traces

        details, list__number_of_traces_per_subplot, list__label = AppFunctions.decode_labelsAndSignals(self)
        number_of_subplot = len(list__number_of_traces_per_subplot)

        self.ui.MplWidget_ACMPlot.canvas.figure.clf()
        axes = self.ui.MplWidget_ACMPlot.canvas.figure.subplots(nrows=number_of_subplot, ncols=1, sharex=True)
        # for index, data_file_name in enumerate(data_file_name_list[::-1]): # 我要倒着画
        for index, data_file_name in enumerate(data_file_name_list): # 不要倒着画！最后跑的程序都还没跑完呢！
            PAIndex = data_file_name[-4:] # len(data_file_name_list) - index

            print('\tParametric Analysis Read In:', data_file_name)
            print(self.ui.plainTextEdit_PANames.toPlainText(), end=":")
            print(', '.join(f'{el}' for el in eval(self.ui.plainTextEdit_PAValues.toPlainText())[int(PAIndex[1:])-1]), end=' ')
            print(PAIndex)

            if PAIndex == '.dat':
                continue
            no_traces = 类似ACMアニメ4C_但只画第一个信号_j等于0(*AppFunctions.get_dataFrame(self, data_file_name), PAIndex=PAIndex) # df_profiles, no_samples, no_traces


        # adjust height per number of traces
        AppFunctions.setACMPlotHeight(self, number_of_subplot)
        # draw
        self.ui.MplWidget_ACMPlot.canvas.draw()
    @Slot()
    def update_PASelected(self):
        if self.ui.comboBox_PADataFileSelected.currentText()[-3:] == 'dat':
            self.ui.lineEdit_PAValueSelected.setText('')
            self.ui.label_PANameSelected_2.setText('')
        else:
            PAIndex = int(self.ui.comboBox_PADataFileSelected.currentText()[-3:]) - 1
            self.ui.lineEdit_PAValueSelected.setText(', '.join(f'{el}' for el in eval(self.ui.plainTextEdit_PAValues.toPlainText())[PAIndex]))
            self.ui.label_PANameSelected_2.setText(self.ui.plainTextEdit_PANames.toPlainText()) # maybe replace \n with ?

    ''' C-based Simulation: Uncertainty '''
    @Slot()
    def update_uncertaintyTable(self, configini):
        if "Induction Machine" in self.ui.comboBox_MachineType.currentText():
            self.ui.tableWidget_Uncertainty.setVerticalHeaderLabels(["rs", "rreq", "Lmu", "Lsigma"])
            self.ui.tableWidget_Uncertainty.setItem(0, 0, QtWidgets.QTableWidgetItem(configini['uncertainty']["rs"]))
            self.ui.tableWidget_Uncertainty.setItem(0, 1, QtWidgets.QTableWidgetItem(configini['uncertainty']["rreq"]))
            self.ui.tableWidget_Uncertainty.setItem(0, 2, QtWidgets.QTableWidgetItem(configini['uncertainty']["Lmu"]))
            self.ui.tableWidget_Uncertainty.setItem(0, 3, QtWidgets.QTableWidgetItem(configini['uncertainty']["Lsigma"]))
        else:
            self.ui.tableWidget_Uncertainty.setVerticalHeaderLabels(["R", "Ld", "Lq", "KE"])
            self.ui.tableWidget_Uncertainty.setItem(0, 0, QtWidgets.QTableWidgetItem(configini['uncertainty']["R"]))
            self.ui.tableWidget_Uncertainty.setItem(0, 1, QtWidgets.QTableWidgetItem(configini['uncertainty']["Ld"]))
            self.ui.tableWidget_Uncertainty.setItem(0, 2, QtWidgets.QTableWidgetItem(configini['uncertainty']["Lq"]))
            self.ui.tableWidget_Uncertainty.setItem(0, 3, QtWidgets.QTableWidgetItem(configini['uncertainty']["KE"]))


    ''' Python-Numba-based Simulation '''
    @Slot()
    @decorator_status(status='Configuring') # this will not be updated until this function is done
    def runPyBasedSimulation(self, bool_realtime=True):

        # switch to scope page
        if bool_realtime:
            self.ui.stackedWidget.setCurrentWidget(self.ui.page_scope)

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
            if ii>100000 or self.ui.lineEdit_AtTop.text() == 's':
                CONSOLE.anim.event_source.stop()
                print('Stop ACMPlot animation for Python.\n----------\n\n')
                UIFunctions.labelTitle(self, 'Main Window - emachinery - Simulation Done')

            # Save time here
            # print(f'Animation goes {ii}')
            # try:
            #     int(self.ui.lineEdit_AtTop.text())
            # except:
            #     pass
            # else:
            #     self.NUMBER_OF_SAMPLE_TO_SHOW = int(self.ui.lineEdit_AtTop.text())
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
            the_cmd = self.ui.plainTextEdit_NumbaScopeDict.toPlainText()
            numba__scope_dict = eval(the_cmd[the_cmd.find('OD'):])
        except Exception as err:
            print('-------------------')
            print('Execution for NumbaScopeDict has failed. Will use the default.')
            numba__scope_dict = OD([
                (r'Speed [rpm]',                  ( 'CTRL.omega_elec'           ,)  ),
                (r'Position [rad]',               ( 'ACM.x[3]'                  ,)  ),
                (r'$q$-axis current [A]',         ( 'ACM.x[1]', 'CTRL.idq[1]'   ,)  ),
                (r'$d$-axis current [A]',         ( 'ACM.x[0]', 'CTRL.idq[0]'   ,)  ),
                (r'$\alpha\beta$ current [A]',    ( 'CTRL.iab[0]', 'CTRL.iab[1]',)  ),
            ])
            print('-------------------')
            print('err:', err)
            print('-------------------')
            traceback.print_exc()
            print('-------------------')

        """ Canvas """
        self.ui.MplWidget_ACMPlot.canvas.figure.clf() # clear canvas
        print('numba__scope_dict =', numba__scope_dict)
        number_of_subplot = len(numba__scope_dict)
        numba__line_dict = OD()
        numba__axes = []
        first_ax = None
        for index, (ylabel, waveform_names) in enumerate(numba__scope_dict.items()):
            # get axes
            ax = self.ui.MplWidget_ACMPlot.canvas.figure.add_subplot(
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
                                linestyle=self.cjh_linestyles[jj], 
                                color=self.cjh_colors[jj], 
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
        AppFunctions.console_push_variable(self, {'CONSOLE':CONSOLE})
        AppFunctions.console_push_variable(self, {'ACM':ACM})
        AppFunctions.console_push_variable(self, {'CTRL':CTRL})
        AppFunctions.console_push_variable(self, {'HM':HUMAN, 'HUMAN':HUMAN})
        AppFunctions.console_push_variable(self, {'reg_id':reg_id})
        AppFunctions.console_push_variable(self, {'reg_iq':reg_iq})
        AppFunctions.console_push_variable(self, {'reg_speed':reg_speed})

        """ Visualization of Realtime Simulation """
        print('\tJIT compile with numba...')
        def onClick(event):
            print(event)
            CONSOLE._pause ^= True
            if CONSOLE._pause:
                CONSOLE.anim.event_source.stop()
            else:
                CONSOLE.anim.event_source.start()

        self.ui.MplWidget_ACMPlot.canvas.figure.canvas.mpl_connect('button_press_event', onClick)
        self.ui.MplWidget_ACMPlot.canvas.draw_idle() # draw before animation # https://stackoverflow.com/questions/8955869/why-is-plotting-with-matplotlib-so-slow
        CONSOLE.anim = animation.FuncAnimation(self.ui.MplWidget_ACMPlot.canvas.figure, ACMアニメ4Py, 
                                        interval=200, cache_frame_data=False) # cache_frame_data=False is good for large artists when plotting
                                        #, blit=True) # blit=True means only re-draw the parts that have changed. 
                                        # https://matplotlib.org/stable/tutorials/advanced/blitting.html
                                        # https://stackoverflow.com/questions/14421924/matplotlib-animate-does-not-update-tick-labels
                                        # https://jakevdp.github.io/blog/2012/08/18/matplotlib-animation-tutorial/

    ''' Optimization Section '''
    # choose machine specification
    @Slot()
    def update_machineSpec(self):
        import acmop
        mop = acmop.AC_Machine_Optiomization_Wrapper(
                    select_fea_config_dict = self.ui.comboBox_FEAConfig.currentText(), 
                    select_spec = self.ui.comboBox_MachineSpec.currentText()
                )
        print(mop)
    @Slot()
    def update_FEAConfig(self):
        pass



    ''' General Information '''
    @Slot()
    def comboActivate_machineType(self, bool_always_true_bug=None, bool_write_configlob=True):

        mtype = AppFunctions.get_mtype(self)
        # print('DEBUG comboActivate_machineType:')
        # print(mtype)
        # print(self.ui.comboBox_MachineType.currentText())
        # print()

        pmsm_list, im_list = [], []
        for key, machine in self.mj.items():
            # Permanent Magnet Motor
            if '永磁' in machine['基本参数']['电机类型']:
                pmsm_list.append(key)
            elif '感应' in machine['基本参数']['电机类型']:
                im_list.append(key)
        self.ui.comboBox_MachineName.clear()
        if 'Synchronous Machine' in self.ui.comboBox_MachineType.currentText():
            self.ui.comboBox_MachineName.addItems(pmsm_list) #(self.mj.keys())
        elif 'Induction Machine' in self.ui.comboBox_MachineType.currentText():
            self.ui.comboBox_MachineName.addItems(im_list) #(self.mj.keys())


        # Recover last user input
        self.filepath_to_configini = pkg_resources.resource_filename(__name__, f'config_{AppFunctions.get_mtype(self)}.json') # updated in AppFunctions.comboActivate_machineType(self)        
        try:
            with open(self.filepath_to_configini, 'r') as f:
                configini = self.configini = json.load(f)
            if bool_write_configlob:
                # 用户界面操作调用则写
                _, self.configlob['MachineTypeIndex'] = AppFunctions.get_mtype(self, bool_also_return_index=True)
                with open(self.filepath_to_configlob, 'w') as f:
                    json.dump(self.configlob, f, ensure_ascii=False, indent=4)
            # else:
            #     # __init__初始化的时候则读
            #     with open(self.filepath_to_configlob, 'r') as f:
            #         configlob = self.configlob = json.load(f)
            if os.path.exists(self.configlob['path2acmsimc']):
                self.path2acmsimc = self.configlob['path2acmsimc']
            else:
                print(f'''\tPath "{self.configlob['path2acmsimc']}" does not exist. Will use default C codes instead.''')
                self.default_path2acmsimc = os.path.dirname(__file__) + '/../acmsimcv5'
                self.path2acmsimc = self.default_path2acmsimc # the default code comes along with the emachinery package
            print('\tPath to acmsimc is:', self.path2acmsimc)
            self.ui.lineEdit_CLTS.setText(configini['CLTS'])
            self.ui.lineEdit_VLTS.setText(configini['VLTS'])
            self.ui.lineEdit_EndTime.setText(configini['EndTime'])
            self.ui.lineEdit_LoadInertiaPercentage.setText(configini['LoadInertiaPercentage'])
            self.ui.lineEdit_LoadTorque.setText(configini['LoadTorque'])
            self.ui.lineEdit_ViscousCoefficient.setText(configini['ViscousCoefficient'])
            self.ui.lineEdit_FluxCmdDetails.setText(configini['FluxCmdDetails'])
            # self.ui.lineEdit_FluxCmdSinePartPercentage.setText(configini['FluxCmdSinePartPercentage'])
            # self.ui.lineEdit_DCBusVoltage.setText(configini['DCBusVoltage'])
            self.ui.lineEdit_OutputDataFileName.setText(configini['OutputDataFileName'])
            self.ui.lineEdit_ControlStrategy.setText(configini['ControlStrategy'])

            AppFunctions.update_uncertaintyTable(self, configini)
        except Exception as e:
            raise e

        # 根据configini，将电机型号选为用户之前选择的那个
        self.ui.comboBox_MachineName.setCurrentIndex(self.configini['MachineNameIndex']) # BUG

        # 更新铭牌值，
        AppFunctions.comboActivate_namePlateData(self)

        # 更新绘图信号对
        # update file path to plot settings
        AppFunctions.update_ACMPlotLabels_and_ACMPlotSignals(self, configini=configini, bool_re_init=True, mtype=None)
            # self.ui.lineEdit_path2ACMPlotLabels.setText('./plot_setting_files/labels_pmsm.txt')
            # self.ui.lineEdit_path2ACMPlotSignals.setText('./plot_setting_files/signals_pmsm.txt')
            # self.ui.lineEdit_path2ACMPlotLabels.setText('./plot_setting_files/labels_im.txt')
            # self.ui.lineEdit_path2ACMPlotSignals.setText('./plot_setting_files/signals_im.txt')
            # AppFunctions.update_ACMPlotLabels_and_ACMPlotSignals(self, )
    @Slot()
    def comboActivate_namePlateData(self):
        self.motor_dict = AppFunctions.get_motor_dict(self, self.mj)
        # print('debug main.py', self.motor_dict)
        self.ui.lineEdit_npp         .setText(str(self.motor_dict['n_pp']))
        self.ui.lineEdit_RatedCurrent.setText(str(self.motor_dict['IN']))
        self.ui.lineEdit_RatedPower  .setText(str(self.motor_dict['PW']))
        self.ui.lineEdit_RatedSpeed  .setText(str(self.motor_dict['RPM']))

        # tab "C-based Simulation" 另一个tab下的LineEdit也同步更新
        self.ui.lineEdit_RO_MachineName.setText(self.ui.comboBox_MachineName.currentText())
        self.ui.lineEdit_DCBusVoltage.setText(str(self.motor_dict['Udc']))

    # parameter conversion
    @Slot()
    def console_push_variable(self, d):
        self.ui.ConsoleWidget.push_vars(d)
        if self.ui.label_pushedVariables.text() == 'None':
            self.ui.label_pushedVariables.setText(', '.join(d.keys()))
        else:
            # Duplicated variable names would exist
            # self.ui.label_pushedVariables.setText(self.ui.label_pushedVariables.text()+', '+', '.join(d.keys()))

            # Avoid duplicated variable names
            for key in d.keys():
                if key not in self.ui.label_pushedVariables.text():
                    self.ui.label_pushedVariables.setText(self.ui.label_pushedVariables.text()+f', {key}')
    @Slot()
    def update_emy(self):
        self.emy = ElectricMachinery( NUMBER_OF_POLE_PAIRS  = int  (self.ui.lineEdit_npp.text()),
                                      RATED_CURRENT_RMS     = float(self.ui.lineEdit_RatedCurrent.text()),
                                      RATED_POWER_WATT      = float(self.ui.lineEdit_RatedPower.text()),
                                      RATED_SPEED_RPM       = float(self.ui.lineEdit_RatedSpeed.text()),
            )
        AppFunctions.console_push_variable(self, {'emy':self.emy})

    # decide which motor is used
    @Slot()
    def get_motor_dict(self, mj):
        # read from json file
        # print('DEBUG get_motor_dict', self.ui.comboBox_MachineName.currentText())
        # print()
        motor = mj[self.ui.comboBox_MachineName.currentText()]["基本参数"]
        motor_dict = dict()
        motor_dict['DOWN_SAMPLE'] = 1 # set here but not implemented in c-simulation

        motor_dict['n_pp'] = n_pp = motor["极对数 [1]"]
        motor_dict['IN']   = IN   = motor["额定电流 [Arms]"]
        motor_dict['PW']   = PW   = motor["额定功率 [Watt]"]
        motor_dict['RPM']  = RPM  = motor["额定转速 [rpm]"]

        motor_dict['J_s']  = J_s  = motor["转动惯量 [kg.cm^2]"]*1e-4
        motor_dict['Udc']  = Udc  = motor["母线电压 [Vdc]"]

        if '感应' in motor['电机类型']:
            motor_dict['Rs']     = Rs     = motor["定子电阻 [Ohm]"]
            motor_dict['Rreq']   = Rreq   = motor["反伽马转子电阻 [Ohm]"]
            motor_dict['Lsigma'] = Lsigma = motor["反伽马漏电感 [mH]"]*1e-3
            motor_dict['Lmu']    = Lmu    = motor["定子D轴电感 [mH]"]*1e-3 - Lsigma
            motor_dict['KE']     = KE     = motor["额定反电势系数 [Wb]"]
            motor_dict['Ls']     = Lsigma + Lmu # this will be used in tuner.py for iteration for current BW

            motor_dict['flux_cmd_dc_part']   = KE                             * eval(self.ui.lineEdit_FluxCmdDetails.text())[0]*0.01
            motor_dict['flux_cmd_sine_part'] = motor_dict['flux_cmd_dc_part'] * eval(self.ui.lineEdit_FluxCmdDetails.text())[1]*0.01
            motor_dict['flux_cmd_sine_herz'] =                                  eval(self.ui.lineEdit_FluxCmdDetails.text())[2] # Hz

        elif '永磁' in motor['电机类型']:
            motor_dict['Rs'] = R  = motor["定子电阻 [Ohm]"]
            motor_dict['Ld'] = Ld = motor["定子D轴电感 [mH]"]*1e-3
            motor_dict['Lq'] = Lq = motor["定子Q轴电感 [mH]"]*1e-3
            motor_dict['KE'] = KE = motor["额定反电势系数 [Wb]"]
            motor_dict['Ls'] = Lq  # this will be used in tuner.py for iteration for current BW

        # below is by user GUI input
        motor_dict['CL_TS'] = CL_TS = eval(self.ui.lineEdit_CLTS.text())
        motor_dict['VL_TS'] = VL_TS = eval(self.ui.lineEdit_VLTS.text())
        motor_dict['EndTime'] = EndTime = eval(self.ui.lineEdit_EndTime.text())

        motor_dict['JLoadRatio']   = eval(self.ui.lineEdit_LoadInertiaPercentage.text())*0.01 #[%]
        motor_dict['Tload']        = eval(self.ui.lineEdit_LoadTorque.text()) #[Nm]
        motor_dict['ViscousCoeff'] = eval(self.ui.lineEdit_ViscousCoefficient.text()) #[Nm/(rad/s)]

        motor_dict['data_file_name_prefix'] = self.ui.lineEdit_OutputDataFileName.text()

        # pass to console
        AppFunctions.console_push_variable(self, {'motor_dict':motor_dict})

        # this will be passed to C based simulation
        return motor_dict

    ''' plot demo '''
    @Slot()
    def update_graph(self):
        if self.ui.MplWidget.canvas.axes is None:
           self.ui.MplWidget.canvas.axes = self.ui.MplWidget.canvas.figure.add_subplot(111)

        import random
        fs = 500
        f = random.randint(1, 100)
        ts = 1/fs
        length_of_signal = 100
        t = np.linspace(0,1,length_of_signal)
    
        cosinus_signal = np.cos(2*np.pi*f*t)
        sinus_signal = np.sin(2*np.pi*f*t)

        self.ui.MplWidget.canvas.axes.clear()
        self.ui.MplWidget.canvas.axes.plot(t, cosinus_signal)
        self.ui.MplWidget.canvas.axes.plot(t, sinus_signal)
        self.ui.MplWidget.canvas.axes.legend(('cosinus', 'sinus'),loc='upper right')
        self.ui.MplWidget.canvas.axes.set_title('Cosinus - Sinus Signal')
        self.ui.MplWidget.canvas.draw()
    ''' Lissajous plot '''
    @Slot()
    def update_LissajousPlot(self, signals=None, no_samples=None):
        if self.signals is None:
            # if self.checkBox_LissajousPlot.isChecked():

            # get lissajous plot data
            df_profiles, no_samples, no_traces = AppFunctions.get_dataFrame(self, self.data_file_name)
            signals = []
            for signal_name_pair in eval(self.ui.plainTextEdit_LissajousPlotSignals.toPlainText()):
                x_name, y_name = signal_name_pair
                signals.append( (df_profiles[x_name], df_profiles[y_name]) )

            # signals are updated when C-based simulation is run or when PlotPanel is updated.
            self.signals = signals
            self.no_samples = no_samples
        else:
            # update plot only, signals are the same as before
            signals    = self.signals
            no_samples = self.no_samples

        # get axis
        if self.ui.MplWidget.canvas.axes is None:
           self.ui.MplWidget.canvas.axes = self.ui.MplWidget.canvas.figure.add_subplot(111)

        # get start and end times
        self.ui.lcdNumber_LissajousStart.display(self.ui.horizontalSlider_LissajousTimeStart.value())
        self.ui.lcdNumber_LissajousEnd.display(self.ui.horizontalSlider_LissajousTimeEnd.value())
        b = int( self.ui.horizontalSlider_LissajousTimeStart.value() * 0.001 * no_samples)
        e = int( self.ui.horizontalSlider_LissajousTimeEnd.value()   * 0.001 * no_samples)

        # plot
        self.ui.MplWidget.canvas.axes.clear()
        self.ui.MplWidget.canvas.axes.set_aspect('equal', adjustable='box')
        for signal_pair in signals:
            x, y = signal_pair
            self.ui.MplWidget.canvas.axes.plot(x[b:e], y[b:e], alpha=0.6, lw=1)
        # self.ui.MplWidget.canvas.axes.legend(('cosinus', 'sinus'),loc='upper right')
        self.ui.MplWidget.canvas.axes.set_title('Lissajous Plot')
        self.ui.MplWidget.canvas.draw()

