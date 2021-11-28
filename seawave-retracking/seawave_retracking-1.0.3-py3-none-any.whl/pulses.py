from matplotlib.pyplot import xscale
import numpy as np
import re
import os
import pandas as pd

from scipy.optimize import curve_fit
from scipy.special import erf, erfc


from  . import config

import logging
logger = logging.getLogger(__name__)

def get_files(file, **kwargs):
    """
    Рекурсивный поиск данных по регулярному выражению 
    """
    # file = file.replace('\\', os.path.sep)
    # file = file.replace('/', os.path.sep)
    path, file = os.path.split(file)

    path = os.path.abspath(path)

    # file = os.path.join(path, file)
    rx = re.compile(file)


    _files_ = []
    for root, dirs, files in os.walk(path, **kwargs):
        for file in files:
            tmpfile = os.path.join(root, file)
            _files_ += rx.findall(tmpfile)
    
    for file in _files_:
        logger.info("Found file: %s" % file)
    
    if not _files_:
        logger.error("No files found")

    return _files_

def to_xlsx(pulses):
    files = []

    if not pulses:
        logger.error("No processed pulses")
        return 

    for i in range(len(pulses)):
        files.append(pulses[i].src)
    

    
    # columns = pd.MultiIndex.from_product([ files, ["t", "P", "Pest"] ])

    
    df = pd.DataFrame(columns=["SWH", "H", "VarSlopes"], index=files)
    exmode = 'w'
    for i, f in enumerate(files):
        columns = pd.MultiIndex.from_product([ [files[i]], ["t", "P", "Pest"] ])
        df0 = pd.DataFrame(columns=columns)
        t = pulses[i].time
        ptype = pulses[i].type
        df0[f, "t"] = pd.Series(t)
        df0[f, "P"] = pd.Series(pulses[i].power)
        df0[f, "Pest"] = pd.Series(pulses[i].pulse(t, *pulses[i].popt))

        df.iloc[i][0] = pulses[i].swh
        df.iloc[i][1] = pulses[i].height/2
        df.iloc[i][2] = pulses[i].varslopes
        excel_name = "%s_%s.xlsx" % (config["Dataset"]["RetrackingFileName"], ptype)
        if i:
            exmode = 'a'

        with pd.ExcelWriter(excel_name, mode=exmode, engine='openpyxl') as writer:  
            df0.to_excel(writer, sheet_name='raw %d' % i)

    with pd.ExcelWriter(excel_name, mode='a', engine='openpyxl') as writer:
            print(ptype)
            df.to_excel(writer, sheet_name=ptype)

    

class pulse(object):
    def __init__(self, config, **kwargs):
        # Скорость света/звука
        self.c = config['Constants']['WaveSpeed']
        self.tau = config["Radar"]["ImpulseDuration"]
        self.delta = np.deg2rad(config["Radar"]["GainWidth"])
        self.type = type(self).__name__

        if 'file' in kwargs:
            try:
                df = pd.read_csv(kwargs['file'], sep="\s+", comment="#")
                self.time = df.iloc[:,0].values
                self.power = df.iloc[:,1].values
                self.curve_fit(**kwargs)
            except:
                self.time = None
                self.power= None
                self.popt = [None, None, None, None, None]
                self.pcov = None

            self.src = kwargs['file']
        elif 't' in kwargs and 'P' in kwargs:
            self.time = kwargs["t"]
            self.power = kwargs["P"]
            self.src = ""
            self.curve_fit(**kwargs)

    def curve_fit(self, **kwargs):
        pass

class brown(pulse):
    def __init__(self, config, **kwargs):
        super().__init__(config, **kwargs)

    @staticmethod
    def pulse(t, A, alpha, tau, sigma_l, T):
        """
        Точная аппроксимация формулы Брауна.
        В отличии от Брауна не привязяна к абсолютному времени. 
        См. отчет по Ростову за 2020 год

        """
        return A * np.exp( -alpha * (t-tau) ) * (1 + erf( (t-tau)/sigma_l ) ) + T

    @property
    def height(self):
        """
        Вычисление высоты от антенны до поверхности воды
        """
        # Скорость света/звука [м/с]
        if self.popt[2] != None:
            tau = self.popt[2] 
            c = self.c
            return tau*c
        else:
            return None

    @property
    def swh(self):

        """
        Вычисление высоты значительного волнения
        """
        # Скорость света/звука [м/с]
        if self.popt[3] != None:
            c = self.c
            # Длительность импульса [с]
            sigma_l = self.popt[3]
            T = config["Radar"]["ImpulseDuration"]
            theta = np.deg2rad(config["Radar"]["GainWidth"])
            sigma_p = 0.425 * T 
            sigma_c = sigma_l/np.sqrt(2)
            sigma_s = np.sqrt((sigma_c**2 - sigma_p**2))*c/2
            factor = np.sqrt(0.425/(2*np.sin(theta/2)**2/np.log(2)))
            # return 4*sigma_s * factor
            return 4*sigma_s
        else:
            return None

    @property
    def varelev(self):
        if self.swh != None:
            return (self.swh/4)**2
        else:
            return None

    @property
    def varslopes(self):
        return None

    def curve_fit(self, **kwargs):

        t = self.time
        power = self.power

        p0 = [power.max(), 1, (t.max() + t.min())/2, (t[-1]-t[0])/t.size, 0]
        bounds = ((0, 0, t.min(), t.min(), 0),
                  (power.max(), np.inf, t.max(), t.max(), power.min()))
        self.popt, self.pcov = curve_fit(self.pulse, 
                            xdata=t,
                            ydata=power,
                            p0=p0,
                        )
        

class karaev(pulse):
    def __init__(self, config, *args, **kwargs):
        super().__init__(config, **kwargs)

    @staticmethod
    def slopes_coeff(varslopes, H, delta):
        # Вычисление коэффициента Ax через дисперсию наклонов, высоту и ширину ДН
        return 1/(2*varslopes*H**2) + 5.52/(delta**2*H**2)

    @property
    def varslopes(self):
        # Вычисление дисперсии наклонов через Ах, высоту и ширину ДН
        
        # H -- высота до поверхности в метрах
        # slopes_coeff -- коэффициент, восстановленный во время ретрекинга
        # delta -- ширина ДН
        if self.popt[1] != None:
            H = self.height
            slopes_coeff = self.popt[1]
            
            delta = self.delta
            invvarslopes = 2*(slopes_coeff*H**2 - 5.52/delta**2)
            return 1/invvarslopes
            # return self.popt[1]
        else:
            return None

    @property
    def height(self):
        if self.popt[2] != None:
            return self.popt[2]
        else:
            return None

    @property
    def varelev(self):

        if self.popt[0] != None:
            return self.popt[0]
        else:
            return None

    @property
    def swh(self):
        if self.popt[0] != None:
            return 4*np.sqrt(self.popt[0])
        else:
            return None

    
    def curve_fit(self, **kwargs):
        t = self.time
        power = self.power

        

        if 'H0' not in kwargs:
            Hmin = t.min()*self.c
            Hmax = t.max()*self.c
            H0 = t[np.argmax(power)]*self.c
        else:
            H0 = kwargs['H0']
            Hmin = 0.99999*H0
            Hmax = 1.00001*H0


        sigma0max = np.max(power)
        P0 = np.inf

        if 'Ax0' not in kwargs:
            # Axmin = self.slopes_coeff(0.043, H0, self.delta)
            # Axmax = self.slopes_coeff(0.02, H0, self.delta)
            Axmin = 0
            Axmax = 0.5
            Ax0 = Axmin
        else:
            Ax0 = kwargs['Ax0']
            Axmin = 0.9*kwargs['Ax0']
            Axmax = 1.1*kwargs['Ax0']
        

        if 'varelev0' not in kwargs:
            varelevmin = 0.0
            varelevmax = 1.5
            varelev0 = varelevmin
        else:
            varelev0 = kwargs['varelev0']
            varelevmin = varelev0*0.9
            varelevmax = varelev0*1.1

        
        self.popt, self.pcov = curve_fit(self.pulse, 
                    xdata=t,
                    ydata=power,
                    p0=[varelev0, Ax0, H0, sigma0max, 0],
                    bounds = ( 
                                (varelevmin, Axmin, Hmin, 0, 0),
                                (varelevmax, Axmax, Hmax, np.inf, np.inf),
                    ), 
                    jac='3-point', 
                    # loss='cauchy', 
                    method='trf', 
                    # max_nfev = 100000,
                    # ftol=1e-15, xtol=1e-15, gtol=1e-15,
                    
                )
# x_scale = (1e-12, 1e-18, 1e-6, 1, 1)


    def pulse(self, t, varelev, slopes_coeff, H, sigma0, noise):


        # delta = self.delta
        # slopes_coeff = self.slopes_coeff(varslopes, H, delta)
        if np.all(t == None):
            return None

        F = np.zeros(t.size, dtype="longdouble")
        

        
        c = self.c
        t = t.copy()
        t -= H/c

        F[np.where(t == None)] = None
        t = t[np.where(t != None)]
        
        idx = -slopes_coeff*H*c*t + 2*varelev*slopes_coeff**2*H**2 >= np.log(np.finfo(np.longdouble).max)
        F[idx] = 0

        idx = -slopes_coeff*H*c*t + 2*varelev*slopes_coeff**2*H**2 < np.log(np.finfo(np.longdouble).max)
        t = t[idx]

        t_pulse = self.tau
        
        

        F[idx] +=  np.exp(-slopes_coeff*H*c*t + 2*varelev*slopes_coeff**2*H**2, dtype="longdouble") * \
        (erfc( slopes_coeff*H*np.sqrt(2*varelev) + (t_pulse - t)*c/(2*np.sqrt(2*varelev))) )
        

        # F[idx] += erf(
        #     (t_pulse - t)*c/(2*np.sqrt(2*varelev))
        # ) + \
        #      erf(
        #          t*c/(2*np.sqrt(2*varelev))
        #         )

        # # # <3 это подгодиан, чтобы не было большой машинной ошибки
        # if slopes_coeff*H*np.sqrt(2*varelev) < 2:
        #     F[idx] -= np.exp(-slopes_coeff*H*c*t + 2*varelev*slopes_coeff**2*H**2, dtype='longdouble') *\
        #     (
        #             erf( slopes_coeff*H*np.sqrt(2*varelev) + (t_pulse - t)*c/(2*np.sqrt(2*varelev)))
        #             -
        #             erf( slopes_coeff*H*np.sqrt(2*varelev) - t*c/(2*np.sqrt(2*varelev)))
        #         )

        return sigma0/2 * F + noise
