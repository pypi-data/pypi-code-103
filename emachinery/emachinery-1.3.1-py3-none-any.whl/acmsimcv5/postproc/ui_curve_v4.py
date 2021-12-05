#%%
from pylab import plt, np, mpl
plt.figure(99); plt.plot([1,2,3]) # for sutpid sublime 4
# from scipy._lib.six import u
plt.style.use('classic')
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'STIXGeneral' # ['serif'] # ['Times New Roman']
mpl.rcParams['legend.fontsize'] = 13
mpl.rcParams['font.size'] = 16 # font size for xticks, yticks
fontdict = {'family' : 'Times New Roman', #'serif',
        'color' : 'darkblue',
        'weight' : 'normal',
        'size' : 16,}
import pandas as pd
import os
from scipy.optimize import curve_fit
# GLOBAL_R = 2.48785


def sigmoid_ori(x, a3):
    return 1 / (1+np.exp(-a3 * x))
def linear(x, a1, a2):
    return a1 * x + a2
def wt_sigmoid(x, a1, a2, a3):
    return a1 * x + a2 / (1+np.exp(-a3 * x)) - a2/2
def zyf_sigmoid(x, a1, a2, a3, a4, a5):
    return a1 * x + a2 / (1+np.exp(-a3 * x)) - a2/2 \
                  + a4 / (1+np.exp(-a5 * x)) - a4/2
def three_sigmoid(x, a1, a2, a3, a4, a5, a6, a7):
    return a1 * x + a2 / (1+np.exp(-a3 * x)) - a2/2 \
                  + a4 / (1+np.exp(-a5 * x)) - a4/2 \
                  + a6 / (1+np.exp(-a7 * x)) - a6/2
def fit_atan(x, a1, a2, a3):
    return a1*x + a2*np.arctan(a3*x)
def fit_tanh(x, a1, a2, a3):
    return a1*x + a2*np.tanh(a3*x)
def fit_atan_plus_tanh(x, a1, a2, a3, a4, a5):
    return a1*x + a2*np.arctan(a3*x) + a4*np.tanh(a5*x)
def fit_sigmoid_plus_atan(x, a1, a2, a3, a4, a5):
    return a1*x + a2 / (1+np.exp(-a3 * x)) - a2/2 + a4*np.arctan(a5*x)
def fit_sigmoid_plus_tanh(x, a1, a2, a3, a4, a5):
    return a1*x + a2 / (1+np.exp(-a3 * x)) + a4*np.tanh(a5*x)

def analyze_ui_curve(i_data, u_data, _):
    ''' 拨乱反正，保证电流是从 -3, -1, 0, 1, 3 A 的顺序，电压同样调整顺序
    '''
    # 注意sort方法是直接修改对象本身的，所以要先改电压，再改电流
    # u_data.sort(key=dict(zip(u_data, i_data)).get) # old method
    # u_data = [el for _, el in sorted(zip(i_data, u_data), key=lambda pair: pair[0])] # new method
    u_data = [el for _, el in sorted(zip(i_data, u_data))] # new method shortest
    i_data.sort()
    # 倒序，负电流在前。
    x = i_data = i_data[::-1]
    y = u_data = u_data[::-1]
    xdata, ydata = np.asarray(x), np.asarray(y)
    plot_xdata = np.arange(min(xdata)*3, max(xdata)*3, 0.001)


    ''' Prepare figure for publication 
    '''

    # Figure 10
    plt.figure(10, figsize=(5,4))
    plt.title('U-I Curves')

    plt.grid(1)
    plt.plot(xdata, ydata, 'ko', label='original data', alpha=0.3)
    # Get fitting_func
    for index, fitting_func in enumerate([  wt_sigmoid, 
                                            #zyf_sigmoid, 
                                            #three_sigmoid, 
                                            #fit_atan, 
                                            #fit_tanh, 
                                            #fit_atan_plus_tanh, 
                                            #fit_sigmoid_plus_atan,
                                            #fit_sigmoid_plus_tanh,
                                        ]):
        ''' curve fitting
        '''
        try:
            popt, pcov = curve_fit(fitting_func, xdata, ydata)
            perr = np.sqrt(np.diag(pcov))
        except RuntimeError as e:
            print(e)
            continue

        print('index =', index)
        print('popt =', popt)
        # print('pcov =', pcov)
        # print('perr =', perr)
        print('\tSquare Error Sum:', sum( (fitting_func(xdata, *popt) - ydata)**2 ))
        print('\tAbs Error Sum:', sum( abs(fitting_func(xdata, *popt) - ydata) ))
        print()

        plt.plot(plot_xdata, fitting_func(plot_xdata, *popt),          'r--', alpha=0.8, label=str(index))
        plt.plot(plot_xdata, fitting_func(plot_xdata, 0.0, *popt[1:]), 'b-.', alpha=0.8, label=str(index), lw=2)

        # plt.plot(plot_xdata, wt_sigmoid(plot_xdata, *popt),                 'r--', alpha=0.8, label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt))
        # plt.plot(plot_xdata, wt_sigmoid(plot_xdata, 0.0, popt[1], popt[2]), 'b-.', alpha=0.8, label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt), lw=2)
        # plt.plot(plot_xdata, zyf_sigmoid(plot_xdata, *popt),          'r--', alpha=0.8, label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f, a4=%5.3f, a5=%5.3f' % tuple(popt))
        # plt.plot(plot_xdata, zyf_sigmoid(plot_xdata, 0.0, *popt[1:]), 'b-.', alpha=0.8, label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f, a4=%5.3f, a5=%5.3f' % tuple(popt), lw=2)
        # plt.plot(plot_xdata, three_sigmoid(plot_xdata, *popt),          'r--', alpha=0.8, label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f, a4=%5.3f, a5=%5.3f, a6=%5.3f, a7=%5.3f' % tuple(popt))
        # plt.plot(plot_xdata, three_sigmoid(plot_xdata, 0.0, *popt[1:]), 'b-.', alpha=0.8, label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f, a4=%5.3f, a5=%5.3f, a6=%5.3f, a7=%5.3f' % tuple(popt), lw=2)
        # plt.show()

    if True:
        plt.grid(1)
        plt.gca().lines[0].set_label('Measured data')
        plt.gca().lines[1].set_label('Fitted Sigmoid curve')
        plt.gca().lines[2].set_label('Fitted Sigmoid curve wo/ linear term')
        # plt.legend(loc='best')
        # plt.xlim([-5,5.1])
        # plt.ylim([-15,15.1])
        plt.xlabel('Phase $b$ current, $i_b$ [A]')
        plt.ylabel('Phase $b$ voltage, $u_{bn}$ [V]')

        # Note  D_b =  u_{bn,\\rm dist}
        # plt.annotate('$D_b$', xy=(3,6.5), xytext=(3,1), color='blue', size=24,
        #                 arrowprops = dict(facecolor ='blue', width=2),)

        plt.xlim([0,5])
        plt.ylim([0,25])
        plt.savefig(os.path.dirname(__file__)+f'/UIC-SlessInvPaper.pdf', dpi=400, bbox_inches = "tight")
        # fname = os.path.split(tag_selected)[-1]
        # plt.savefig(os.path.dirname(__file__)+f'/{fname}.pdf', dpi=400, bbox_inches = "tight")
        # plt.savefig(fr'D:\DrH\[00]GetWorking\200 The-ACM-Book\ACMBook_TEX\images\inverter-nonl-fitting-@{tag_selected}.pdf', dpi=400, bbox_inches = "tight")


    # Sub-figure for Slessinv.R1
    plt.figure(100+_, figsize=(5/2,4/2))
    if _ == 0:
        plt.title(r'INV2, $V_{dc}=150$ V')
    elif _ == 1:
        plt.title(r'INV2, $V_{dc}=300$ V')
    elif _ == 2:
        plt.title(r'INV1, $V_{dc}=150$ V')
    elif _ == 3:
        plt.title(r'INV1, $V_{dc}=300$ V')
    plt.grid(1)
    plt.plot(xdata, ydata, 'ko', label='original data', alpha=0.3)
    plt.plot(plot_xdata, fitting_func(plot_xdata, *popt),          'r--', alpha=0.8, label=str(index))
    plt.plot(plot_xdata, fitting_func(plot_xdata, 0.0, *popt[1:]), 'b-.', alpha=0.8, label=str(index), lw=2)
    plt.grid(1)
    plt.gca().lines[0].set_label('Measured data')
    plt.gca().lines[1].set_label('Fitted Sigmoid curve')
    plt.gca().lines[2].set_label('Fitted Sigmoid curve wo/ linear term')
    plt.xlabel('$i_b$ [A]')
    plt.ylabel('$u_{bn}$ [V]')
    plt.xlim([0,5])
    plt.ylim([0,25])
    plt.savefig(os.path.dirname(__file__)+f'/UIC-SlessInvPaper-{_}.pdf', dpi=400, bbox_inches = "tight")




    ''' draw the partial derivative w.r.t. a3
    '''
    if False:
        a2, a3 = popt[1], popt[2]
        plt.plot(x, a2*x*sigmoid_ori(x, a3)*(1-sigmoid_ori(x, a3)), 'k-.', label='derivative')

        popt_ori = popt[2]
        ''' 观察sigmoid的变化当a3变化
        '''
        # popt[2] = popt_ori * 1.2
        # plt.plot(x, wt_sigmoid(x, 0.0, popt[1], popt[2]), 'b-.', color='black', alpha=alpha,
        #      label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt), lw=2)
        # popt[2] = popt_ori * 0.8
        # plt.plot(x, wt_sigmoid(x, 0.0, popt[1], popt[2]), 'b-.', color='green', alpha=alpha,
        #      label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt), lw=2)
        popt[2] = popt_ori * 0.5
        plt.plot(x, wt_sigmoid(x, 0.0, popt[1], popt[2]), 'b-.', color='black', alpha=alpha,
                label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt), lw=2)
        popt[2] = popt_ori * 100
        plt.plot(x, wt_sigmoid(x, 0.0, popt[1], popt[2]), 'b-.', color='green', alpha=alpha,
                label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt), lw=2)
        popt[2] = popt_ori

def is_float(text):
    # by mathfac, https://stackoverflow.com/questions/354038/how-do-i-check-if-a-string-is-a-number-float
    try:
        float(text)
        # check for nan/infinity etc.
        if text.isalpha():
            return False
        return True
    except ValueError:
        return False


''' 决定用哪个数据
# 从字符串里提取出电流、电压数据
'''
def synthesize_ccs_memory_phaseCurrent(tag_selected):

    df_voltage = pd.read_csv(os.path.dirname(__file__)+'./逆变器非线性测试数据（保存内存）/'+tag_selected+'_Voltage.dat', skiprows=0)
    df_current = pd.read_csv(os.path.dirname(__file__)+'./逆变器非线性测试数据（保存内存）/'+tag_selected+'_Current.dat', skiprows=0)
    # print(df_voltage)
    # print(df_current)
    flatten = lambda t: [item for sublist in t for item in sublist]
    return flatten(df_current.values), flatten(df_voltage.values)




if __name__ == '__main__':
   
    ''' Select a tag
    '''
    # tag_selected = '20210622/OW_IPM_Inverter_80V_NoDeadTimeCompensation' # max I = 1.0 A
    # tag_selected = '20210622/OW_IPM_Inverter_180V_NoDeadTimeCompensation' # max I = 1.0 A
    # tag_selected = '20210623/OW_IPM_Inverter_80V_NoDeadTimeCompensation' # max I = 4.2 A
    # tag_selected = '20210623/OW_IPM_Inverter_180V_NoDeadTimeCompensation' # max I = 4.2 A

    # tag_selected = '20210725/SiC_Inverter_150V_NoDeadTimeCompensation'
    # tag_selected = '20210725/SiC_Inverter_300V_NoDeadTimeCompensation'

    # tag_selected = '20210725/OW-IPM_Inverter_100V_NoDeadTimeCompensation'
    # tag_selected = '20210725/OW-IPM_Inverter_150V_NoDeadTimeCompensation'
    # tag_selected = '20210725/OW-IPM_Inverter_300V_NoDeadTimeCompensation'

    ''' This is used for SlessInv paper.
    '''
    for _, tag_selected in enumerate(
                        ['20210725/SiC_Inverter_150V_NoDeadTimeCompensation',
                         '20210725/SiC_Inverter_300V_NoDeadTimeCompensation',
                         # '20210725/OW-IPM_Inverter_100V_NoDeadTimeCompensation',
                         '20210725/OW-IPM_Inverter_150V_NoDeadTimeCompensation',
                         '20210725/OW-IPM_Inverter_300V_NoDeadTimeCompensation']):

    # if False:

        phase_current_data, phase_voltage_data = dict(), dict()
        phase_current_data[tag_selected], \
        phase_voltage_data[tag_selected] = i_data, u_data = synthesize_ccs_memory_phaseCurrent(tag_selected)
        print('len(current) =', len(i_data))
        print('len(voltage) =', len(u_data))

        ''' LUT
        '''
        if True:
            ''' 生成二段式查表
            '''
            last_I = None
            I_incremental = None
            low_current_I_incremental_list = []
            low_current_voltage_list = []
            low_current_current_list = []
            high_current_I_incremental_list = []
            high_current_voltage_list = []
            high_current_current_list = []
            for index, ui_pair in enumerate(zip(u_data, i_data)):
                U, I = ui_pair
                if I <= 0:
                    continue
                # 只用正电流数据
                if last_I is not None:
                    if I_incremental is None:
                        I_BigStep = last_I - I
        
                    I_incremental = last_I - I
                    # print(f'{[index]} increment in I: {I_incremental:g} A')

                    if abs(I_incremental - I_BigStep) < 0.1*I_BigStep:
                        high_current_current_list.append(I)
                        high_current_voltage_list.append(U)
                        high_current_I_incremental_list.append(I_incremental)
                    else:
                        low_current_current_list.append(I)
                        low_current_voltage_list.append(U)
                        low_current_I_incremental_list.append(I_incremental)
                else:
                    print('Max I:', I)
                last_I = I
            average = lambda ell: sum(ell)/len(ell)
            # print(high_current_voltage_list)
            I_BigStep = average(high_current_I_incremental_list)
            # print(I_BigStep, 'A')
            # print(low_current_voltage_list)
            I_SmallStep = average(low_current_I_incremental_list)
            # print(I_SmallStep, 'A')

            ''' Fit high current data to a line 
            '''
            low_current_voltage_list  = np.asarray(low_current_voltage_list  )
            low_current_current_list  = np.asarray(low_current_current_list  )
            high_current_voltage_list = np.asarray(high_current_voltage_list )
            high_current_current_list = np.asarray(high_current_current_list )
            # print(low_current_current_list)
            # print(high_current_current_list)
            # quit()
            xdata = high_current_current_list[:10] # 前面10个点的电流、电压是最大的哦
            ydata = high_current_voltage_list[:10] # 前面10个点的电流、电压是最大的哦
            popt, pcov = curve_fit(linear, xdata, ydata)
            Fitted_R = popt[0]
            print('Fitting for Resistance')
            print('\tpopt =', popt)
            print('\tSquare Error Sum:', sum(    (linear(xdata, *popt) - ydata)**2 ))
            print('\tAbs Error Sum:',    sum( abs(linear(xdata, *popt) - ydata)    ))
            print('\t此处，Fitted_R 必须用大电流的结果来替代！！！')

            ''' The LUT Method Generator
            '''
            print('\t#define FITTED_R', Fitted_R)
            print('\t#define LUT_STEPSIZE_BIG ', I_BigStep)
            print('\t#define LUT_STEPSIZE_SMALL ', I_SmallStep)
            print('\t#define LUT_STEPSIZE_BIG_INVERSE ', 1.0/I_BigStep)
            print('\t#define LUT_STEPSIZE_SMALL_INVERSE ', 1.0/I_SmallStep)
            lut_lc_voltage = low_current_voltage_list - Fitted_R*low_current_current_list
            lut_hc_voltage = high_current_voltage_list - Fitted_R*high_current_current_list
            lut_lc_voltage = [0] + list(lut_lc_voltage[::-1])
            lut_hc_voltage = list(lut_hc_voltage[::-1])
            N_LC = len(lut_lc_voltage); print('Low current data points:', N_LC)
            N_HC = len(lut_hc_voltage); print('High current data points:', N_HC)
            print('\t#define LUT_N_LC ', N_LC)
            print('\t#define LUT_N_HC ', N_HC)
            print(f'\tREAL lut_lc_voltage[{N_LC}] = {{' + ', '.join(f'{el:g}' for el in lut_lc_voltage) + '};')
            print(f'\tREAL lut_hc_voltage[{N_HC}] = {{' + ', '.join(f'{el:g}' for el in lut_hc_voltage) + '};')

            plt.figure(21)
            plt.plot(xdata, ydata,                         'ko', alpha=0.8, label='Ori')
            plt.plot(high_current_current_list, high_current_voltage_list - Fitted_R*high_current_current_list, 'rx', alpha=0.8, label='Ori')
            plt.plot(low_current_current_list, low_current_voltage_list - Fitted_R*low_current_current_list, 'b^', alpha=0.8, label='Ori')
            plt.plot(xdata, linear(xdata, *popt),          'r--', alpha=0.8, label='Fit')
            plt.plot(xdata, linear(xdata, 0.0, *popt[1:]), 'b-.', alpha=0.8, label='Plateau', lw=2)

            LUT_N_LC = N_LC
            LUT_N_HC = N_HC
            LUT_STEPSIZE_BIG = I_BigStep
            LUT_STEPSIZE_SMALL = I_SmallStep
            LUT_STEPSIZE_BIG_INVERSE = 1.0/I_BigStep
            LUT_STEPSIZE_SMALL_INVERSE = 1.0/I_SmallStep
            LUT_I_TURNING_LC = LUT_N_LC*LUT_STEPSIZE_SMALL
            LUT_I_TURNING_HC = LUT_N_LC*LUT_STEPSIZE_SMALL + LUT_N_HC*LUT_STEPSIZE_BIG
            V_PLATEAU = lut_hc_voltage[-1]
            print('\t#define LUT_STEPSIZE_BIG',             I_BigStep)
            print('\t#define LUT_STEPSIZE_SMALL',           I_SmallStep)
            print('\t#define LUT_STEPSIZE_BIG_INVERSE',     1.0/I_BigStep)
            print('\t#define LUT_STEPSIZE_SMALL_INVERSE',   1.0/I_SmallStep)
            print('\t#define LUT_I_TURNING_LC',             LUT_N_LC*LUT_STEPSIZE_SMALL)
            print('\t#define LUT_I_TURNING_HC',             LUT_N_LC*LUT_STEPSIZE_SMALL + LUT_N_HC*LUT_STEPSIZE_BIG)
            print('\t#define V_PLATEAU',                    lut_hc_voltage[-1])
            def lookup_compensation_voltage_by_index(current_value):
                abs_current_value = abs(current_value)

                if abs_current_value < LUT_I_TURNING_LC:
                    float_index = abs_current_value * LUT_STEPSIZE_SMALL_INVERSE
                    index = int(float_index)
                    if index+1 >= LUT_N_LC:
                        # print('DEBUG', index)
                        slope = (lut_hc_voltage[0] - lut_lc_voltage[index]) * LUT_STEPSIZE_SMALL_INVERSE
                            # 经过下面的电流列表验证，这里确实应该是用LUT_STEPSIZE_SMALL_INVERSE
                            # print(low_current_current_list)
                            # print(high_current_current_list)
                            # quit()
                        # print('Turning voltages:', lut_hc_voltage[0], lut_lc_voltage[index])
                        # print(index, 'Low--')
                    else:
                        slope = (lut_lc_voltage[index+1] - lut_lc_voltage[index]) * LUT_STEPSIZE_SMALL_INVERSE
                        # print(index, 'Low')
                    return np.sign(current_value) * (lut_lc_voltage[index] + slope * (abs_current_value - index*LUT_STEPSIZE_SMALL))
                # elif abs_current_value < LUT_I_TURNING_HC:
                else:
                    float_index = (abs_current_value - LUT_I_TURNING_LC) * LUT_STEPSIZE_BIG_INVERSE
                    index = int(float_index)
                    if index+1 >= LUT_N_HC:
                        # print('Plateau')
                        return V_PLATEAU
                    else:
                        # print(index, 'High')
                        slope = (lut_hc_voltage[index+1] - lut_hc_voltage[index]) * LUT_STEPSIZE_BIG_INVERSE
                    return np.sign(current_value) * (lut_hc_voltage[index] + slope * (abs_current_value - LUT_I_TURNING_LC - index*LUT_STEPSIZE_BIG))

            plot_xdata = np.arange(0, max(xdata)+0.1, 1e-3)
            # plot_xdata = np.arange(0, max(xdata)+0.1, 0.5*LUT_STEPSIZE_SMALL)
            plt.figure(22)
            plt.title('LUT')
            plt.plot(plot_xdata, [lookup_compensation_voltage_by_index(el) for el in plot_xdata], 'k.', alpha=0.8, label='LUT')
            plt.plot(i_data, np.array(u_data)-Fitted_R*np.array(i_data), 'o', alpha=0.8, label='Ori')
            plt.grid()
            plt.legend()
            print('结论，电阻值辨识得用足够大的电流才靠谱！')
            # plt.show()

        ''' 描点、拟合、画图
        '''
        analyze_ui_curve(i_data, u_data, _)

    print('Note a2 in this script is inconsistent with the SlessInv paper.')
    plt.show()

# %%
