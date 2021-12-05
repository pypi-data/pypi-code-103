# %%
import sys; 
sys.path.insert(1, r'D:\DrH\Codes\emachineryTestPYPI\emachinery\acmsimcv5\CJHAcademicPlot')
from __cjhAcademicPlotSettings import CJHStylePlot, pd, np, plt, os
sys.path.insert(1, r'D:\DrH\Codes\visualize')
from DFT_CJH import myDFT_single_channel, DFT_CJH

# %%
''' Current Function
'''
I_AMPL = 1.0
PERIOD = 0.02 # s
CL_TS = 1e-4
time = np.arange(0, PERIOD, CL_TS)
phase_angle = np.arange(-np.pi, np.pi, 2*np.pi / len(time))

def sigmoid(x, a1=0, a2=1, a3=10):
    return a1 * x + a2* (2 / (1.0 + np.exp(-a3 * x)) - 1)

""" Compensation Voltage Function By Current Value """

Ix = np.arange(0,2,0.01)
plt.figure(figsize=(20,6))
plt.plot(Ix, sigmoid(Ix, a2=4, a3=5))
plt.plot(Ix, sigmoid(Ix, a2=2, a3=10))
plt.plot(Ix, sigmoid(Ix, a2=1, a3=20))


#%% In time domain

def main():
    dict_label_dataframe = dict()

    I_AMPL_list = [1, 0.2]
    # I_AMPL_list = [1, ]
    # I_AMPL_list = [5, ]
    for key, I_AMPL in zip([str(el) for el in I_AMPL_list], I_AMPL_list):
        phase_current = np.sin(phase_angle) * I_AMPL
        ui_curve = [sigmoid(current_value) for current_value in phase_current]
        dict_label_dataframe.update(
            {
                key: [
                    pd.DataFrame({
                        'Time': time,
                        'Signal': phase_current
                    }), 
                    pd.DataFrame({
                        'Time': time,
                        'Signal': ui_curve
                    }), 
                ] # 如果不是一个list，则CSP会报错：TypeError: string indices must be integers
            }
        )

    def adjust_figure(axes_v):
        axes_v[0].set_ylim([-1.1,1.1])
        axes_v[1].set_ylim([-1.1,1.1])
    def adjust_ylabel(axes_v):
        axes_v[0].set_ylabel('[A] or [V]')
        axes_v[1].set_ylabel(None)
        # for ax in axes_v:
        #     ax.set_ylabel('[A] or [V]')

        axes_v[0].set_xlabel('Time, $t$ [s]\n(a)')
        axes_v[1].set_xlabel('Time, $t$ [s]\n(b)')

    csp = CJHStylePlot( ncols=len(I_AMPL_list), figsize=(5, 1.5)) #figsize=(4, 1.5) )
    csp.aca_plot(dict_label_dataframe, x='Time', y='Signal', 
                    adjust_figure=adjust_figure,
                    adjust_ylabel=adjust_ylabel)
    csp.aca_save(f'{os.path.dirname(__file__)}/compensation_voltage_shape', bool_sumatrapdf=True)

    return ui_curve, csp

ui_curve, csp = main()


# %%
""" 检查 sigmoid in time domain 随着 Ix 和 omega 的变化而变化的规律 """

sigma = lambda t, a3, Ix, omega: 2 / (1 + np.exp(-a3*Ix*np.sin(omega*t))) - 1

Ix = 2
omega = 50*2*np.pi

t = np.arange(0, 0.02, CL_TS)
ix = Ix*np.sin(omega*t)
Dx = sigma(t, a3=10, Ix=Ix, omega=omega)
plt.plot(t, ix)
plt.plot(t, Dx)

# %%

def basic_DFT_analysis(raw_data, Frequency):
    REPEAT = 10

    time = np.arange(0, REPEAT/Frequency, CL_TS)

    signal = np.array(REPEAT*list(raw_data))
    ax1 = ax_matrix[0]
    ax2 = ax_matrix[1]
    ax1.set_xlabel('Frequency [Hz]')
    ax1.set_ylabel('Amplitude [dB]')
    ax2.set_xlabel('Frequency [Hz]')
    ax2.set_ylabel('Phase [deg]')

    DFT_CJH(ax1, time, signal, bool_use_dB=False, ax2=ax2)

    ax1.set_xlim([0,200])
    # ax.set_ylim([-50,5])
    ax1.grid(1)
    ax2.grid(1)

    print(len(time), len(signal))

sigma = lambda t, a3, Ix, omega: 2 / (1 + np.exp(-a3*Ix*np.sin(omega*t))) - 1
Frequency = 10
t = np.arange(0, 1/Frequency, CL_TS)
fig, ax_matrix = plt.subplots(ncols=1, nrows=2, sharex=True, figsize=(20,6))
for Ix in [0.1, 0.5, 10]:
    Dx = sigma(t, a3=10, Ix=Ix, omega=Frequency*2*np.pi)
    basic_DFT_analysis(Dx, Frequency)


# %%

def parametric_analysis_of_harmonic_content(raw_data, Frequency):
    REPEAT = 1
    time = np.arange(0, REPEAT/Frequency, CL_TS)
    signal = np.array(REPEAT*list(raw_data))
    dft_dict = myDFT_single_channel(time, signal)

    if REPEAT == 1: # 如果REPEAT变了分辨率就变了，间隔也就变了哦。
        harmonics[ 1].append(dft_dict['ampl'][ 1]); #print(' 10 Hz', dft_dict['ampl'][ 1])
        harmonics[ 5].append(dft_dict['ampl'][ 5]); #print(' 50 Hz', dft_dict['ampl'][ 5])
        harmonics[ 7].append(dft_dict['ampl'][ 7]); #print(' 70 Hz', dft_dict['ampl'][ 7])
        harmonics[11].append(dft_dict['ampl'][11]); #print('110 Hz', dft_dict['ampl'][11])
        harmonics[13].append(dft_dict['ampl'][13]); #print('130 Hz', dft_dict['ampl'][13])

# the problem
sigma = lambda t, a3, Ix, omega: 2 / (1 + np.exp(-a3*Ix*np.sin(omega*t))) - 1
Frequency = 10
CL_TS = 1e-4
t = np.arange(0, 1/Frequency, CL_TS)

# init
def init_harmonics_dict():
    harmonics = dict()
    for h in [1,5,7,11,13]:
        harmonics[h] = []
    return harmonics

a2_list = [1, 2, 4]
for a2 in a2_list:

    # iterate through different a3 values
    a3_list = [5,10,20,40]
    for a3 in a3_list:

        harmonics = init_harmonics_dict()

        # iterate through current peak value
        # Ix_list = [0.05, 0.1, 0.2, 0.4, 0.8, 1.6, 3.2, 6.4] #, 12.8, 25.6, 51.2, 102.4]
        Ix_list = np.arange(0.1, 6.31, 0.05) #, 12.8, 25.6, 51.2, 102.4]
        Ix_list = np.arange(0.1, 3, 0.05)
        for Ix in Ix_list:
            Dx = a2*sigma(t, a3=a3, Ix=Ix, omega=Frequency*2*np.pi)
            parametric_analysis_of_harmonic_content(Dx, Frequency)

        plt.figure(1, figsize=(8,6), facecolor='w')
        plt.plot(Ix_list, harmonics[1], '.--', label=f'$a_2={a2},~a_3={a3}$') # marker='$1$', 
        plt.legend()
        plt.title('Amplitude of the Fundamental Component in $\hat D_x(t)$')
        plt.grid(1)

        plt.figure(5, figsize=(20,6), facecolor='w')
        plt.plot(Ix_list, harmonics[5], '.--', label=f'$a_2={a2},~a_3={a3}$') # marker='$5$', 
        plt.legend()
        plt.title('5th order harmonic')
        plt.grid(1)

        plt.figure(11, figsize=(20,6), facecolor='w')
        plt.plot(Ix_list, harmonics[11], '.--', label=f'$a_2={a2},~a_3={a3}$') # marker='$11$', 
        plt.legend()
        plt.title('11th order harmonic')
        plt.grid(1)

        # plt.figure(7, figsize=(20,6), facecolor='w')
        # plt.plot(Ix_list, harmonics[7], '.-', label=f'$a_2={a2},~a_3={a3}$')
        # plt.legend()
        # plt.title('7th order harmonic')
        # plt.grid(1)

        # plt.figure(13, figsize=(20,6), facecolor='w')
        # plt.plot(Ix_list, harmonics[13], '.-', label=f'$a_2={a2},~a_3={a3}$')
        # plt.legend()
        # plt.title('13th order harmonic')
        # plt.grid(1)

        print(Ix_list[int(sum(np.array(harmonics[1])<1.209546*a2))-1] * a3)

    fig = plt.figure(1)
    plt.plot(Ix_list, np.zeros_like(Ix_list) + harmonics[1][-1] * 0.95, 'k--')
    plt.ylabel('Voltage [V]')
    plt.xlabel('Current Peak Value, $I_x$ [A]')
    # print(harmonics[1][-1] * 0.95)

csp.aca_save(f'{os.path.dirname(__file__)}/harmonic_contents', bool_sumatrapdf=True, fig=fig)


# %%

""" Analysis with Park&Sul Style 
    Voltage components as a function of a3Ix.
"""

fig, axes = plt.subplots(nrows=1, ncols=3, figsize=(9,3), facecolor='w', sharey=True)

a3Ix_list = np.arange(0, 80, 0.5)

for a2, alpha in zip([3,2,1], [1, 0.7, 0.5]):

    harmonics = init_harmonics_dict()

    for a3Ix in a3Ix_list:

        # iterate through current peak value
        Dx = a2*sigma(t, a3=a3Ix, Ix=1, omega=Frequency*2*np.pi)
        parametric_analysis_of_harmonic_content(Dx, Frequency)

    print(a3Ix_list[int(sum(np.array(harmonics[1])<1.209546*a2))-1] * 1) # 1.209546 is 95% of the max fundamental

    ax = axes[0]
    ax.plot(a3Ix_list, harmonics[1], '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.title.set_text('Fundamental')
    ax.grid(1)
    ax.set_xlabel('$a_3I_x$ [1]')

    ax = axes[1]
    ax.plot(a3Ix_list, np.array(harmonics[5]), '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.title.set_text('5th order harmonic')
    ax.grid(1)
    ax.set_xlabel('$a_3I_x$ [1]')

    ax = axes[2]
    ax.plot(a3Ix_list, np.array(harmonics[11]), '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.title.set_text('11th order harmonic')
    ax.grid(1)
    ax.set_xlabel('$a_3I_x$ [1]')

    # plt.figure(7, figsize=(20,6), facecolor='w')
    # plt.plot(a3Ix_list, harmonics[7], '.-', label=f'$a_2={a2}$'
    # plt.legend()
    # plt.title('7th order harmonic')
    # plt.grid(1)
    # plt.xlabel('$a_3I_x$')

    # plt.figure(13, figsize=(20,6), facecolor='w')
    # plt.plot(a3Ix_list, harmonics[13], '.-', label=f'$a_2={a2}$'
    # plt.legend()
    # plt.title('13th order harmonic')
    # plt.grid(1)
    # plt.xlabel('$a_3I_x$')

    axes[0].plot(a3Ix_list, np.zeros_like(a3Ix_list) + harmonics[1][-1] * 0.95, 'k--')

axes[0].set_ylabel('Voltage [V]')
plt.plot([], [], ' ', label="From top to bottom")
plt.legend()

csp.aca_save(f'{os.path.dirname(__file__)}/harmonic_contents_by_a3Ix', bool_sumatrapdf=True, fig=fig)

#%%

""" 重制，谐波和基波的比例既然不变，这个信息就要利用起来。
"""
import matplotlib.ticker as mtick

#fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(8,3), facecolor='w', sharey=False)
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,3), facecolor='w', sharey=False)
fig.subplots_adjust(wspace=0.5)

a3Ix_list = np.arange(0.5, 80, 0.5)

for a2, alpha in zip([3,2,1], [1, 0.7, 0.5]):

    harmonics = init_harmonics_dict()

    for a3Ix in a3Ix_list:

        # iterate through current peak value
        Dx = a2*sigma(t, a3=a3Ix, Ix=1, omega=Frequency*2*np.pi)
        parametric_analysis_of_harmonic_content(Dx, Frequency)

    print(a3Ix_list[int(sum(np.array(harmonics[1])<1.209546*a2))-1] * 1) # 1.209546 is 95% of the max fundamental

    ax = axes[0]
    ax.plot(a3Ix_list, harmonics[1], '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.title.set_text('Fundamental')
    ax.grid(1)
    ax.set_xlabel('$a_3I_x^*$ [1]\n(a)')

    ax = axes[1]
    ax.plot(a3Ix_list, np.array(harmonics[5]) / np.array(harmonics[1]), '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.plot(a3Ix_list, np.array(harmonics[11]) / np.array(harmonics[1]), '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.plot(a3Ix_list, np.array(harmonics[7]) / np.array(harmonics[1]), '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.plot(a3Ix_list, np.array(harmonics[13]) / np.array(harmonics[1]), '-', label=f'$a_2={a2}$', alpha=alpha)
    ax.title.set_text('Harmonics')
    ax.grid(1)
    ax.set_xlabel('$a_3I_x^*$ [1]\n(b)')

    axes[0].plot(a3Ix_list, np.zeros_like(a3Ix_list) + harmonics[1][-1] * 0.95, 'k--')

axes[0].set_ylabel('Voltage [V]')
axes[1].set_ylabel('Harmonic to\nFundamental Ratio [%]')
plt.plot([], [], ' ', label="From top to bottom")
# plt.legend()
axes[1].yaxis.set_major_formatter(mtick.PercentFormatter(xmax=1.0, decimals=0))

csp.aca_save(f'{os.path.dirname(__file__)}/harmonic_contents_by_a3Ix_ratio', bool_sumatrapdf=True, fig=fig)

# %%
