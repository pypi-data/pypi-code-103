# %%
from pylab import np, plt
plt.style.use('ggplot')

I_AMPL = 5.0
PERIOD = 0.1 # s
CL_TS = 1e-4
time = np.arange(0, PERIOD, CL_TS)
phase_angle = np.arange(-np.pi, np.pi, 2*np.pi / len(time))
phase_current = np.sin(phase_angle) * I_AMPL


""" By Current Value """
def sigmoid(x, a1=0, a2=5, a3=10):
    return a1 * x + a2 / (1.0 + np.exp(-a3 * x)) - a2*0.5

bool_printed = False
def quadratic(current, I_turning, V_turning, I_plateau, V_plateau):
    slope = (V_plateau - V_turning) / (I_plateau - I_turning)
    a1 = 2*V_turning/I_turning - slope
    a2 = (V_turning - I_turning*slope)/I_turning**2
    global bool_printed
    if not bool_printed:
        print(a1, a2)
        bool_printed = True
    abs_current = abs(current)
    if abs_current < I_turning:
        return np.sign(current)*(a1*abs_current - a2*abs_current**2) # nonlinear
    elif abs_current < I_plateau:
        # V_turning = a1*current - a2*current**2
        # slope = a1 - 2*a2*I_turning
        return np.sign(current)*(V_turning + slope*(abs_current-I_turning))
    else:
        return np.sign(current)*V_plateau

# u-i curve quadratic
RATIO_TURNING_1 = 0.8
RATIO_TURNING_0 = 0.9
uic_q = [quadratic(current_value, 
                        I_turning= 2*RATIO_TURNING_0*RATIO_TURNING_1,
                        V_turning=10*RATIO_TURNING_0,
                        I_plateau= 2, 
                        V_plateau=10
                    ) for current_value in phase_current]
fig_UIcurve = plt.figure(figsize=(20,6))
fig_UIcurve.gca().plot(phase_current, uic_q)

fig_timeDomain = plt.figure(figsize=(20,6))
fig_timeDomain.gca().plot(time, uic_q)
fig_timeDomain.gca().plot(time, phase_current)

# %%
import sys
sys.path.insert(1, r'D:\DrH\Codes\visualize')
from DFT_CJH import myDFT_single_channel, DFT_CJH

ax = plt.figure(figsize=(20,6)).gca()

REPEAT = 10
time = np.arange(0, REPEAT*PERIOD, CL_TS)

signal = np.array(REPEAT*list(uic_q))
DFT_CJH(ax, time, signal, bool_use_dB=False)

ax.set_xlim([0,200])
# ax.set_ylim([-50,5])

print(len(time), len(signal))

# %%
REPEAT = 1
time = np.arange(0, REPEAT*PERIOD, CL_TS)

harmonics = dict()
harmonics[1] = []
harmonics[5] = []
harmonics[7] = []
harmonics[11] = []
harmonics[13] = []

# Free parameters
OPTION = 1
if OPTION == 1: # I_plateau is dependent parameter
    LIST_PARAM = LIST_I_Plateau = np.arange(0.1, 2, 0.05)

fig_UIcurve = plt.figure(figsize=(20,6))
fig_timeDomain = plt.figure(figsize=(20,6))

for I_plateau in LIST_I_Plateau:

    # Dependent parameters
    if OPTION == 1:
        pass

    uic_q = [quadratic(current_value, 
                        I_turning= 2*RATIO_TURNING_0*RATIO_TURNING_1,
                        V_turning=10*RATIO_TURNING_0,
                        I_plateau= I_plateau, 
                        V_plateau=10
                    ) for current_value in phase_current]

    fig_UIcurve.gca().plot(phase_current, uic_q)
    fig_timeDomain.gca().plot(time, uic_q)

    signal = np.array(REPEAT*list(uic_q))
    dft_dict = myDFT_single_channel(time, signal)

    # print([el for el in dft_dict['ampl'][0:15]])
    # print([el for el in dft_dict['ampl'][0:15] if el>1e-5])

    if REPEAT == 1: # 如果REPEAT变了分辨率就变了，间隔也就变了哦。
        harmonics[ 1].append(dft_dict['ampl'][ 1]); #print(' 10 Hz', dft_dict['ampl'][ 1])
        harmonics[ 5].append(dft_dict['ampl'][ 5]); #print(' 50 Hz', dft_dict['ampl'][ 5])
        harmonics[ 7].append(dft_dict['ampl'][ 7]); #print(' 70 Hz', dft_dict['ampl'][ 7])
        harmonics[11].append(dft_dict['ampl'][11]); #print('110 Hz', dft_dict['ampl'][11])
        harmonics[13].append(dft_dict['ampl'][13]); #print('130 Hz', dft_dict['ampl'][13])

# %%
plt.figure(figsize=(20,6))
plt.plot(harmonics[ 1], '.-')
plt.figure(figsize=(20,6))
plt.plot(harmonics[ 5], '.-')
plt.plot(harmonics[ 7], '.-')
plt.plot(harmonics[11], '.-')
plt.plot(harmonics[13], '.-')
plt.show()

# %%
