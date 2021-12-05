# %% 结论：两段直线没有意义，两个斜率对各次谐波的影响是同步的
from pylab import np, plt
plt.style.use('ggplot')

V_AMPL = 1.0
I_AMPL = 10.0
PERIOD = 0.1 # s
CL_TS = 1e-4
time = np.arange(0, PERIOD, CL_TS)
phase_angle = np.arange(-np.pi, np.pi, 2*np.pi / len(time))
phase_current = np.sin(phase_angle) * I_AMPL

""" By Phase Angle """
def trapezoidal(theta_A, theta_t, V_plateau):

    oneOver_theta_t = 1.0 / theta_t

    if theta_A > 0:
        if theta_A < theta_t:
            compensation = theta_A * V_plateau * oneOver_theta_t
        elif theta_A > np.pi - theta_t:
            compensation = (np.pi-theta_A) * V_plateau * oneOver_theta_t
        else:
            compensation = V_plateau
    else:
        if -theta_A < theta_t:
            compensation = -theta_A * -V_plateau * oneOver_theta_t
        elif -theta_A > np.pi - theta_t:
            compensation = (np.pi+theta_A) * -V_plateau * oneOver_theta_t
        else:
            compensation = -V_plateau
    return compensation

""" By Current Value """
def tratrapezoizoidal(current, 
        R_0=12.0, V_plateau=V_AMPL, 
        R_1=3.5, V_turning=V_AMPL*0.7, 
        I_turning=V_AMPL*0.7/12.0, I_plateau=V_AMPL*0.7/12.0 + V_AMPL*(1-0.7) / 3.5):
    # R_1 must be less than R_0
    # V_turning = \kappa * V_plateau
    # I_turning = V_turning / R_0
    # I_plateau = I_turning + (V_plateau - V_turning) / R_1

    if current > I_plateau:
        return V_plateau
    elif current < -I_plateau:
        return -V_plateau
    elif current > I_turning:
        return V_turning + R_1*(current - I_turning)
    elif current < -I_turning:
        return -V_turning + R_1*(current + I_turning)
    else:
        return current * R_0

fig_UIcurve = plt.figure(figsize=(20,6))

def sigmoid(x):
    a1 = 0
    a2 = I_AMPL*2
    a3 = 15
    return a1 * x + a2 / (1.0 + np.exp(-a3 * x)) - a2*0.5

for theta_t in [ 5.0 / 180 * np.pi,
                # 10.0 / 180 * np.pi,
                # 15.0 / 180 * np.pi,
                # 20.0 / 180 * np.pi,
                ]:

    uic_t = [trapezoidal(theta_A, theta_t, I_AMPL) for theta_A in phase_angle]
    fig_UIcurve.gca().plot(phase_current, uic_t)

uic_s = [sigmoid(current_value) for current_value in phase_current]
fig_UIcurve.gca().plot(phase_current, uic_s)

uic_tt = [tratrapezoizoidal(current_value) for current_value in phase_current]
fig_UIcurve.gca().plot(phase_current, uic_tt)

fig_timeDomain = plt.figure(figsize=(20,6))
fig_timeDomain.gca().plot(time, uic_t)
fig_timeDomain.gca().plot(time, uic_s)
fig_timeDomain.gca().plot(time, uic_tt)
fig_timeDomain.gca().plot(time, phase_current)

# %%
import sys
sys.path.insert(1, r'D:\DrH\Codes\visualize')
from DFT_CJH import myDFT_single_channel, DFT_CJH

ax = plt.figure(figsize=(20,6)).gca()

REPEAT = 10
time = np.arange(0, REPEAT*PERIOD, CL_TS)

signal = np.array(REPEAT*list(uic_t))
DFT_CJH(ax, time, signal, bool_use_dB=False)
signal = np.array(REPEAT*list(uic_tt))
DFT_CJH(ax, time, signal, bool_use_dB=False)
signal = np.array(REPEAT*list(uic_s))
DFT_CJH(ax, time, signal, bool_use_dB=False)

ax.set_xlim([0,200])
# ax.set_ylim([-50,5])

print(len(time), len(signal))

# %%
REPEAT = 1
time = np.arange(0, REPEAT*PERIOD, CL_TS)

# Free parameters
OPTION = 1
if OPTION == 1:
    kappa = 0.7
    R_0 = 12.0 # 另一种思路是给定 I_plateau，这样R_0就相应被确定了。
    R_1 = 3.5
    V_plateau = I_AMPL # = 1
elif OPTION == 2:
    V_plateau = I_AMPL # = 1
    kappa = 0.7
    I_plateau = 0.15 # 0.25 # [A]
    R_1 = 4.5
elif OPTION == 3:
    V_plateau = I_AMPL # = 1
    kappa = 0.7
    I_plateau = 0.15 # 0.25 # [A]
    R_0 = 12.0 # [Ohm]

harmonics = dict()
harmonics[1] = []
harmonics[5] = []
harmonics[7] = []
harmonics[11] = []
harmonics[13] = []
if OPTION == 1: # I_plateau is dependent parameter
    LIST_R_0 = np.arange(1.0, 10, 0.25)
    LIST_R_1 = np.arange(0.1, R_0, 0.1)
    LIST_R_1_RATIO = np.arange(0.2, 1.1, 0.2)
elif OPTION == 2: # R_0 is dependent parameter
    LIST_R_1 = np.arange(2.5, 5.5, 0.2)
    LIST_I_plateau = np.arange(0.1, 0.6, 0.02)
elif OPTION == 3: # R_1 is dependent parameter
    LIST_R_0 = np.arange(0.5, 20, 0.5)
    LIST_I_plateau = np.arange(0.1, 0.6, 0.02)
LIST_kappa = np.arange(0.5, 0.95, 0.1)
fig_UIcurve = plt.figure(figsize=(20,6))
fig_timeDomain = plt.figure(figsize=(20,6))
LIST_I_plateau_plot = []

# LIST_PARAM = LIST_kappa
# for kappa in LIST_kappa:

# LIST_PARAM = LIST_I_plateau
# for I_plateau in LIST_PARAM:

# LIST_PARAM = LIST_R_1
# for R_1 in LIST_R_1:

# LIST_PARAM = LIST_R_0
# for R_0 in LIST_R_0:

# LIST_PARAM = LIST_R_1_RATIO
# for R_1_RATIO in LIST_R_1_RATIO:

for R_0 in [2, 5,  10, 100]:
    # for R_1_RATIO in [0.33, 1.0]:
    # for R_1_RATIO in [1.0, 1.5]:
    for R_1_RATIO in [1.0]:
        for kappa in [0.7]:
        #for kappa in [0.7]:
 
            # Dependent parameters
            V_turning = V_plateau*kappa
            if OPTION == 1:
                R_1 = R_1_RATIO * R_0
                I_plateau=V_turning/R_0 + (V_plateau-V_turning) / R_1
                I_turning = V_turning/R_0
            elif OPTION ==2:
                I_turning = I_plateau - (V_plateau-V_turning) / R_1
                R_0 = V_turning / I_turning

                print('R_0 =', R_0)
                if R_0<R_1:
                    R_0 = R_1 # become trapezoidal 
                    print(f'Put R_0=R_1={R_1}')
                    # continue

            elif OPTION ==3:
                I_turning = V_turning / R_0
                R_1 = V_turning / I_turning

                print('R_1, R_0 =', R_1, R_0)
                if R_0<R_1:
                    R_1 = R_0 # become trapezoidal 
                    print(f'Put R_1=R_0={R_0}')
                    # continue


            # uic_s = [sigmoid(current_value) for current_value in phase_current]
            # uic_t = [trapezoidal(theta_A, theta_t, AMPL) for theta_A in phase_angle]
            uic_tt = [tratrapezoizoidal(current_value, 
                            R_0=R_0, V_plateau=V_plateau,
                            R_1=R_1, V_turning=V_turning,
                            I_turning=I_turning, I_plateau=I_plateau,
                        ) for current_value in phase_current]

            fig_UIcurve.gca().plot(phase_current, uic_tt)
            fig_timeDomain.gca().plot(time, uic_tt)

            # signal = np.array(REPEAT*list(uic_s))
            # signal = np.array(REPEAT*list(uic_t))
            signal = np.array(REPEAT*list(uic_tt))

            dft_dict = myDFT_single_channel(time, signal)

            # print([el for el in dft_dict['ampl'][0:15]])
            # print([el for el in dft_dict['ampl'][0:15] if el>1e-5])

            if REPEAT == 1: # 如果REPEAT变了分辨率就变了，间隔也就变了哦。
                LIST_I_plateau_plot.append(I_plateau)
                harmonics[ 1].append(dft_dict['ampl'][ 1]); #print(' 10 Hz', dft_dict['ampl'][ 1])
                harmonics[ 5].append(dft_dict['ampl'][ 5]); #print(' 50 Hz', dft_dict['ampl'][ 5])
                harmonics[ 7].append(dft_dict['ampl'][ 7]); #print(' 70 Hz', dft_dict['ampl'][ 7])
                harmonics[11].append(dft_dict['ampl'][11]); #print('110 Hz', dft_dict['ampl'][11])
                harmonics[13].append(dft_dict['ampl'][13]); #print('130 Hz', dft_dict['ampl'][13])

# %%
# LIST_PARAM
# LIST_PARAM
# LIST_PARAM
# LIST_PARAM
# LIST_PARAM
plt.figure(figsize=(20,6))
plt.plot(harmonics[ 1], '.-')
plt.figure(figsize=(20,6))
plt.plot(harmonics[ 5], '.-')
plt.plot(harmonics[ 7], '.-')
plt.plot(harmonics[11], '.-')
plt.plot(harmonics[13], '.-')
plt.show()


# %%
from pylab import np, plt
def sigmoid(x, a1=0, a2=5, a3=10):
    return a1 * x + a2 / (1.0 + np.exp(-a3 * x)) - a2*0.5

x = np.arange(-10,10,1e-3)
for a3 in [1,3,5,7,9,100]:
    plt.plot(x, sigmoid(x, a3=a3))

# %%
