# %%
from pylab import np, plt, mpl
plt.style.use('ggplot')

mpl.rcParams['legend.fontsize'] = 10
mpl.rcParams['font.family'] = ['serif'] # default is sans-serif
mpl.rcParams['font.serif'] = ['Times New Roman']
font = {'family':'Times New Roman', 'weight':'normal', 'size':10}

# this changes font for ticks for my TEC-ISMB paper figures but has no effect here, why?
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = ['STIXGeneral', 'Times New Roman']
mpl.rcParams['font.size'] = 14.0
mpl.rcParams['legend.fontsize'] = 12.5

plt.style.use('ggplot') 



''' Current Function
'''
I_AMPL = 5.0
I_AMPL = 0.2
# I_AMPL = 1.2

PERIOD = 0.1 # s
CL_TS = 1e-4
time = np.arange(0, PERIOD, CL_TS)
phase_angle = np.arange(-np.pi, np.pi, 2*np.pi / len(time))
phase_current = np.sin(phase_angle) * I_AMPL

""" Compensation Voltage Function By Current Value """
def sigmoid(x, a1=0, a2=2, a3=10):
    return a1 * x + a2 / (1.0 + np.exp(-a3 * x)) - a2*0.5

def basic_drawings(cv_function):
    # u-i curve quadratic
    ui_curve = [cv_function(current_value) for current_value in phase_current]

    print('Figure: UI-Curve')
    fig_UIcurve = plt.figure(figsize=(20,6), facecolor='w')
    fig_UIcurve.gca().plot(phase_current, ui_curve)

    print('Figure: Time Domain')
    fig_timeDomain = plt.figure(figsize=(20,6), facecolor='w')
    fig_timeDomain.gca().plot(time, ui_curve)
    fig_timeDomain.gca().plot(time, phase_current)

    return ui_curve

ui_curve = basic_drawings(cv_function=sigmoid)


# %%
import sys
sys.path.insert(1, r'D:\DrH\Codes\visualize')
from DFT_CJH import myDFT_single_channel, DFT_CJH

REPEAT = 10

def basic_DFT_analysis(raw_data):

    time = np.arange(0, REPEAT*PERIOD, CL_TS)

    signal = np.array(REPEAT*list(raw_data))
    print('Figure: DFT')
    fig, ax_matrix = plt.subplots(ncols=1, nrows=2, sharex=True, figsize=(20,6))
    ax1 = ax_matrix[0]
    ax2 = ax_matrix[1]
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Amplitude [dB]')
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Phase [deg]')

    DFT_CJH(ax1, time, signal, bool_use_dB=False, ax2=ax2)

    # ax1.set_xlim([0,2000])
    ax1.set_xlim([0,200])
    # ax.set_ylim([-50,5])

    print(len(time), len(signal))

basic_DFT_analysis(ui_curve)

# %%
REPEAT = 1
time = np.arange(0, REPEAT*PERIOD, CL_TS)

# Free parameters
OPTION = 1
if OPTION == 1: # I_plateau is dependent parameter
    LIST_PARAM = np.arange(0.5, 10, 0.5)

def parametric_analysis_of_harmonic_content(ui_curve):

    fig_UIcurve.gca().plot(phase_current, ui_curve)
    fig_timeDomain.gca().plot(time, ui_curve)

    signal = np.array(REPEAT*list(ui_curve))
    dft_dict = myDFT_single_channel(time, signal)

    # print([el for el in dft_dict['ampl'][0:15]])
    # print([el for el in dft_dict['ampl'][0:15] if el>1e-5])

    if REPEAT == 1: # 如果REPEAT变了分辨率就变了，间隔也就变了哦。
        harmonics[ 1].append(dft_dict['ampl'][ 1]); #print(' 10 Hz', dft_dict['ampl'][ 1])
        harmonics[ 5].append(dft_dict['ampl'][ 5]); #print(' 50 Hz', dft_dict['ampl'][ 5])
        harmonics[ 7].append(dft_dict['ampl'][ 7]); #print(' 70 Hz', dft_dict['ampl'][ 7])
        harmonics[11].append(dft_dict['ampl'][11]); #print('110 Hz', dft_dict['ampl'][11])
        harmonics[13].append(dft_dict['ampl'][13]); #print('130 Hz', dft_dict['ampl'][13])

harmonics = dict()
harmonics[1] = []
harmonics[5] = []
harmonics[7] = []
harmonics[11] = []
harmonics[13] = []
fig_UIcurve = plt.figure(figsize=(20,6), facecolor='w')
fig_timeDomain = plt.figure(figsize=(20,6), facecolor='w')
for a3 in LIST_PARAM:

    # Dependent parameters
    if OPTION == 1:
        pass

    ui_curve = [sigmoid(current_value, a3=a3) for current_value in phase_current]
    parametric_analysis_of_harmonic_content(ui_curve)

plt.figure(figsize=(20,6), facecolor='w')
plt.plot(harmonics[ 1], '.-')
plt.figure(figsize=(20,6), facecolor='w')
plt.plot(harmonics[ 5], '.-')
plt.plot(harmonics[ 7], '.-')
plt.plot(harmonics[11], '.-')
plt.plot(harmonics[13], '.-')
plt.show()

# %%

REPEAT = 10

""" a3 错 """
ui_curve_1 = [sigmoid(current_value, a2=2, a3=10) for current_value in phase_current]
ui_curve_2 = [sigmoid(current_value, a2=2, a3=20) for current_value in phase_current]
basic_DFT_analysis(np.array(ui_curve_1) - np.array(ui_curve_2))

ui_curve_1 = [sigmoid(current_value, a2=2, a3=10) for current_value in phase_current]
ui_curve_2 = [sigmoid(current_value, a2=2, a3=5) for current_value in phase_current]
basic_DFT_analysis(np.array(ui_curve_1) - np.array(ui_curve_2))

'''还要注意到，a3变化所产生的效果是非线性的，当a3小到一定程度时，对谐波含量的影响会变大！'''

""" a2 错 """
ui_curve_1 = [sigmoid(current_value, a2=2, a3=10) for current_value in phase_current]
ui_curve_2 = [sigmoid(current_value, a2=2.5, a3=10) for current_value in phase_current]
basic_DFT_analysis(np.array(ui_curve_1) - np.array(ui_curve_2))

ui_curve_1 = [sigmoid(current_value, a2=2, a3=10) for current_value in phase_current]
ui_curve_2 = [sigmoid(current_value, a2=1.5, a3=10) for current_value in phase_current]
basic_DFT_analysis(np.array(ui_curve_1) - np.array(ui_curve_2))


''' 
初步结论，如果想辨识a3，最好用高次谐波电流去做检测，
因为a2误差导致的误差中除了基波含量以外最大的就是六次。
如果你用六次去校正a3，那a2的误差也会被你吃进去。
'''


# %%
ui_curve_1 = [sigmoid(current_value, a2=2, a3=10) for current_value in phase_current]
ui_curve_2 = [sigmoid(current_value, a2=1.8, a3=5) for current_value in phase_current]
raw_data = np.array(ui_curve_1) - np.array(ui_curve_2)
signal = np.array(REPEAT*list(raw_data))
time = np.arange(0, REPEAT*PERIOD, CL_TS)
dft_dict = myDFT_single_channel(
    time=time,
    signal=signal,
    bool_use_NFFT=False
)

# %%
