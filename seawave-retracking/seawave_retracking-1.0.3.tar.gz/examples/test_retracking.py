import sys, os
import numpy as np
sys.path.append(".")

from seawave_retracking import pulses, config
import matplotlib.pyplot as plt

# name_folder = 'Krym_2021/16_Oct_17_34'
# name_folder= 'Krym_2021/900s_impulses'
name_folder= 'examples/impulses'
f = pulses.get_files('%s/.*.txt' % name_folder)
# f = ['%s/prepared/600khz_150s.dat' % name_folder]

# ImpulseDuration = {
#     "20khz": 0.37*1e-3, 
#     "40khz": 0.18*1e-3, 
#     "80khz": 0.09*1e-3, 
#     "100khz": 0.08*1e-3, 
#     "200khz": 0.04*1e-3, 
#     "600khz": 0.013*1e-3, 
#     "20": 0.37*1e-3, 
#     "40": 0.18*1e-3, 
#     "80": 0.09*1e-3, 
#     "100": 0.08*1e-3, 
#     "200": 0.04*1e-3, 
#     "600": 0.013*1e-3, 
# } 

# WaveLength = {
#     "20khz": 6.9*1e-2, 
#     "40khz": 3.48*1e-2, 
#     "80khz": 1.74*1e-2, 
#     "100khz": 1.5*1e-2, 
#     "200khz": 0.75*1e-2, 
#     "600khz": 0.25*1e-2, 
#     "20": 6.9*1e-2, 
#     "40": 3.48*1e-2, 
#     "80": 1.74*1e-2, 
#     "100": 1.5*1e-2, 
#     "200": 0.75*1e-2, 
#     "600": 0.25*1e-2, 
# } 

# GainWidth = {
#     "20khz": 90*np.sqrt(2), 
#     "40khz": 45*np.sqrt(2),
#     "80khz": 22.5*np.sqrt(2),
#     "100khz": 28*np.sqrt(2),
#     "200khz": 14*np.sqrt(2),
#     "600khz": 4.6*np.sqrt(2),
#     "20": 90*np.sqrt(2), 
#     "40": 45*np.sqrt(2),
#     "80": 22.5*np.sqrt(2),
#     "100": 28*np.sqrt(2),
#     "200": 14*np.sqrt(2),
#     "600": 4.6*np.sqrt(2)
# } 


# # print(f)


pulse = []

config['Dataset']['RetrackingFileName'] = "%s/impulses" % name_folder

Ax = np.zeros(len(f))
w = np.zeros(len(f))
# invslopes = np.zeros(len(f))
# dsigma = np.zeros(len(f))

for i in range(len(f)):
    key = os.path.basename(f[i]).split('_')[0].split('.')[0]
    name = os.path.basename(f[i])
    # config['Radar']['WaveLength'] = WaveLength[key]
    # config['Radar']['GainWidth'] = GainWidth[key]
    # config['Radar']['ImpulseDuration'] =  ImpulseDuration[key]
    pulse.append(pulses.karaev(config, file=f[i]))
    plt.figure()
    t = pulse[-1].time
    P = pulse[-1].power
    Pest = pulse[-1].pulse(t, *pulse[-1].popt)
    plt.plot(t, P, label="raw")
    plt.plot(t, Pest, label="estimated")
    plt.ylabel("$P, V^2$")
    plt.xlabel("$t, s$")
    plt.legend()
    plt.title("%s" % (name.split("_")[0]))
    print('%s : %.5f, %.2f, %.2f' % (name, pulse[-1].varslopes, pulse[-1].swh, pulse[-1].height/2))
    # print('%s : %s' % (name, pulse[-1].popt))
    
    plt.savefig("%s/%s_%d.png" % (name_folder, name.split("_")[0], i))

    # Ax[i] = pulse[-1].popt[1]
    # w[i] = WaveLength[key]
    
    # dH = 0.001
    # H = 30
    # dsigma[i] = np.abs(2 * Ax[i] *  H * dH / (pulse[-1].varslopes))
    
    
# plt.figure()
# # print(2*pulse[-1].tau*1500)
# idx = np.argsort(w)
# idx = np.flip(idx)
# w = w[idx]
# # plt.plot(dsigma)
# plt.savefig("%s/%s.png" % (name_folder, 'dsigma'))

# plt.figure()
# idx = np.argsort(w)
# pulse = np.array(pulse, dtype=object)[idx].tolist()
# for i in range(w.size):
#     print(pulse[i].src, w[i])

# plt.plot(w[idx], Ax[idx])
# plt.plot(w[idx], 1/(2*Ax[idx]*pulse[0].height**2))
# plt.savefig("%s/%s.png" % (name_folder, 'Ax'))


pulses.to_xlsx(pulse)