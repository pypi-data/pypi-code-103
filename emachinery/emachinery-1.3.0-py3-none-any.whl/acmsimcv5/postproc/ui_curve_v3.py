from pylab import plt, np, mpl
plt.style.use('classic')
mpl.rcParams['mathtext.fontset'] = 'stix'
mpl.rcParams['font.family'] = 'STIXGeneral' # ['serif'] # ['Times New Roman']
mpl.rcParams['legend.fontsize'] = 13
mpl.rcParams['font.size'] = 16 # font size for xticks, yticks
fontdict = {'family' : 'Times New Roman', #'serif',
        'color' : 'darkblue',
        'weight' : 'normal',
        'size' : 16,}

from scipy.optimize import curve_fit
# GLOBAL_R q= 1.705
GLOBAL_R = 2.48785
def sigmoid_ori(x, a3):
    return 1 / (1+np.exp(-a3 * x))
def linear(x, a1, a2):
    return a1 * x + a2
def wt_sigmoid(x, a1, a2, a3):
    return a1 * x + a2 / (1+np.exp(-a3 * x)) - a2/2
    # a1,a2,a3 = [1.28430164 8.99347107 5.37783655]
def my_sigmoid(x, a2, a3):
    return GLOBAL_R * x + a2 / (1+np.exp(-a3 * x)) - a2/2
    # a1,a2,a3 = [1.28430164 8.99347107 5.37783655]
def my_curve_fitting(xdata, ydata, alpha=1.0, color='b'):

    sigmoid_used = my_sigmoid
    xdata = np.asarray(xdata)
    if True:
        popt, pcov = curve_fit(wt_sigmoid, xdata, ydata) # bounds=(0, [3., 1., 0.5])) # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
    elif False:
        popt, pcov = curve_fit(linear, xdata, ydata)
        popt = popt[0], popt[1], 15.355
    else:
        popt, pcov = curve_fit(my_sigmoid, xdata, ydata) # bounds=(0, [3., 1., 0.5])) # https://docs.scipy.org/doc/scipy/reference/generated/scipy.optimize.curve_fit.html
        popt = GLOBAL_R, popt[0], popt[1]

    print('a1,a2,a3 =', popt)
    plt.plot(xdata, ydata, 'ko', label='original data', alpha=alpha)
    x = np.arange(min(xdata)*3, max(xdata)*3, 0.001)
    plt.plot(x, wt_sigmoid(x, *popt), 'r--', alpha=alpha,
         label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt))
    plt.plot(x, wt_sigmoid(x, 0.0, popt[1], popt[2]), 'b-.', color=color, alpha=alpha,
         label='fit: a1=%5.3f, a2=%5.3f, a3=%5.3f' % tuple(popt), lw=2)

    if '180' in tag_selected and 'SiC' in tag_selected:
        plt.grid()
        plt.gca().lines[0].set_label('Measured data')
        plt.gca().lines[1].set_label('Fitted Sigmoid curve')
        plt.gca().lines[2].set_label('Fitted Sigmoid curve wo/ linear term')
        plt.legend(loc='best')
        plt.xlim([-5,5.1])
        plt.ylim([-15,15.1])
        plt.xlabel('Phase $b$ current, $i_b$ [A]')
        plt.ylabel('Phase $b$ voltage [V]')
        # Note  D_b =  u_{bn,\\rm dist}
        plt.annotate('$D_b$', xy=(3,6.5), xytext=(3,1), color='blue', size=24,
                        arrowprops = dict(facecolor ='blue', width=2),)
        plt.savefig(fr'D:\DrH\[00]GetWorking\200 The-ACM-Book\ACMBook_TEX\images\inverter-nonl-fitting-@{tag_selected}.pdf', dpi=400, bbox_inches = "tight")    

    print('\nslope is:', wt_sigmoid(100, *popt) - wt_sigmoid(99, *popt), end='\n\n')

    if False:
        ''' draw the partial derivative w.r.t. a3
        '''
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

    return popt
def analyze_ui_curve(tag_selected, plot_style='k-o'):

    i_data = list( phase_current_data[tag_selected] )
    u_data = list( phase_voltage_data[tag_selected] )

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

    # 点太多了！只拟合一部分数据！
    if tag_selected=='Mini6PhaseIPMInverter-528-0927-phaseB-80V[294-Points]-1A-[ADC offset-compensated]':
        M = int(0.5*len(x))
        L = 30
        # x = i_data = x[M-L: M+L]
        # y = u_data = y[M-L: M+L]

        # for linear fit
        # x = i_data = x[:-220]
        # y = u_data = y[:-220]

    if tag_selected=='SiC-529-0957-phase-B-80V-[ADC-gain-Tuned]':
        M = int(0.5*len(x))
        # L = 30
        # x = i_data = x[M-L: M+L]
        # y = u_data = y[M-L: M+L]

        # for linear fit
        # x = i_data = x[:-70]
        # y = u_data = y[:-70]

    # Figure 1
    plt.figure(1)
    a1, a2, a3 = my_curve_fitting(x, y, alpha=0.8)
    R = a1
    print('R =', R, a1, GLOBAL_R)
    plt.grid(True)
    plt.xlabel('Current [A]')
    plt.ylabel('Voltage [V]')    


    # Figure 11 and Figure 12
    fig11 = plt.figure(11)
    ax1 = fig11.gca()
    # print(i_data)
    # print()
    # print(u_data)
    ax1.plot(i_data, u_data, plot_style, label=tag_selected)
    ax1.set_xlabel('Current [A]')
    ax1.set_ylabel('Voltage [V]')

    voltage_to_compensate = np.array(u_data) - np.array(i_data)*R
    fig12 = plt.figure(12)
    ax2 = fig12.gca()
    ax2.plot(i_data, voltage_to_compensate, plot_style, label=tag_selected)
    ax2.set_xlabel('Current [A]')
    ax2.set_ylabel('Voltage [V]')

    print('#define LENGTH_OF_LUT ', len(i_data))
    print('REAL lut_current_ctrl[LENGTH_OF_LUT] = {' + ', '.join(f'{el:g}' for el in i_data[::-1]) + '};')
    print('REAL lut_voltage_ctrl[LENGTH_OF_LUT] = {' + ', '.join(f'{el:g}' for el in voltage_to_compensate[::-1]) + '};')
    print()

    for fig in [fig11, fig12]:
        fig.gca().legend()
        fig.gca().grid()
        # fig.gca().set_xlim([0,4.5])
        # fig.gca().set_ylim([0,11])
    return a1, a2, a3
def convert_beta_to_phase_B_quantities(beta):
    # 正确的关系应该是 ibeta = (2/3) * sqrt(3)/2 * (ib - ic) 
    #                       = (2/3) * sqrt(3) ib
    #                       = 2 / sqrt(3) ib
    phase_B = np.asarray(beta) * np.sqrt(3) / 2
    # phase_B = np.asarray(beta) * SIN_2PI_SLASH_3 # 这个是直接根据反变换得到的。
    return phase_B
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
def synthesize_ccs_expression_betaAxisCurrent(ccs_expression):
    beta_current = []
    beta_voltage = []
    bool_collecting_current = False
    bool_collecting_voltage = False
    for index, el in enumerate(ccs_expression.split('\n')):
        value = el[el.find('float')+5:el.find('0x')].strip()
        if is_float(value):
            value = float(value) 
        else:
            continue

        if '[0]' in el and index<20: # assume current has more than 20 points
            # print('beginning of current')
            bool_collecting_current = True

        if '[0]' in el and index>20:
            # print('beginning of voltage')
            bool_collecting_voltage = True
            bool_collecting_current = False

        if bool_collecting_current:
            beta_current.append(value)

        if bool_collecting_voltage:
            beta_voltage.append(value)

    return convert_beta_to_phase_B_quantities(beta_current), \
           convert_beta_to_phase_B_quantities(beta_voltage)

def synthesize_ccs_expression_phaseCurrent(ccs_expression):
    phase_current = []
    phase_voltage = []
    bool_collecting_current = False
    bool_collecting_voltage = False
    for index, el in enumerate(ccs_expression.split('\n')):
        value = el[el.find('float')+5:el.find('0x')].strip()
        if is_float(value):
            value = float(value) 
        else:
            continue

        if '[0]' in el and index<20: # assume current has more than 20 points
            # print('beginning of current')
            bool_collecting_current = True

        if '[0]' in el and index>20:
            # print('beginning of voltage')
            bool_collecting_voltage = True
            bool_collecting_current = False

        if bool_collecting_current:
            phase_current.append(value)

        if bool_collecting_voltage:
            phase_voltage.append(value)

    return phase_current, phase_voltage

# SIN_2PI_SLASH_3 = 0.86602540378443871
# SIN_DASH_2PI_SLASH_3 = -0.86602540378443871

if __name__ == '__main__':
    ''' CCS Expressions
    '''
    ccs_expressions = dict()

    tag = 'SiC-404-1400-phaseB-180V'
    # 404-1400
    ccs_expressions[tag] = '''
        [0] float   3.63730597  0x0000AB9C@Data 
        [1] float   3.45543242  0x0000AB9E@Data 
        [2] float   3.27357244  0x0000ABA0@Data 
        [3] float   3.09168482  0x0000ABA2@Data 
        [4] float   2.90983176  0x0000ABA4@Data 
        [5] float   2.72796631  0x0000ABA6@Data 
        [6] float   2.54608202  0x0000ABA8@Data 
        [7] float   2.36424494  0x0000ABAA@Data 
        [8] float   2.18238902  0x0000ABAC@Data 
        [9] float   2.00051045  0x0000ABAE@Data 
        [10]    float   1.81867373  0x0000ABB0@Data 
        [11]    float   1.63679731  0x0000ABB2@Data 
        [12]    float   1.45493102  0x0000ABB4@Data 
        [13]    float   1.27303982  0x0000ABB6@Data 
        [14]    float   1.09120989  0x0000ABB8@Data 
        [15]    float   0.909343362 0x0000ABBA@Data 
        [16]    float   0.727471292 0x0000ABBC@Data 
        [17]    float   0.545610487 0x0000ABBE@Data 
        [18]    float   0.363728911 0x0000ABC0@Data 
        [19]    float   0.181912392 0x0000ABC2@Data 
        [20]    float   -3.63731217 0x0000ABC4@Data 
        [21]    float   -3.45544195 0x0000ABC6@Data 
        [22]    float   -3.27359009 0x0000ABC8@Data 
        [23]    float   -3.09173226 0x0000ABCA@Data 
        [24]    float   -2.9098258  0x0000ABCC@Data 
        [25]    float   -2.72798967 0x0000ABCE@Data 
        [26]    float   -2.54610777 0x0000ABD0@Data 
        [27]    float   -2.36421275 0x0000ABD2@Data 
        [28]    float   -2.18235493 0x0000ABD4@Data 
        [29]    float   -2.00049496 0x0000ABD6@Data 
        [30]    float   -1.81867516 0x0000ABD8@Data 
        [31]    float   -1.63679326 0x0000ABDA@Data 
        [32]    float   -1.45494831 0x0000ABDC@Data 
        [33]    float   -1.2730732  0x0000ABDE@Data 
        [34]    float   -1.09117186 0x0000ABE0@Data 
        [35]    float   -0.90930897 0x0000ABE2@Data 
        [36]    float   -0.727452219    0x0000ABE4@Data 
        [37]    float   -0.545594692    0x0000ABE6@Data 
        [38]    float   -0.363719016    0x0000ABE8@Data 
        [39]    float   -0.181852937    0x0000ABEA@Data 

        [0] float   13.0438643  0x0000AC00@Data 
        [1] float   12.7948027  0x0000AC02@Data 
        [2] float   12.5535326  0x0000AC04@Data 
        [3] float   12.3157082  0x0000AC06@Data 
        [4] float   12.0765467  0x0000AC08@Data 
        [5] float   11.8307734  0x0000AC0A@Data 
        [6] float   11.5731659  0x0000AC0C@Data 
        [7] float   11.3238297  0x0000AC0E@Data 
        [8] float   11.05233    0x0000AC10@Data 
        [9] float   10.7761841  0x0000AC12@Data 
        [10]    float   10.4857903  0x0000AC14@Data 
        [11]    float   10.1873112  0x0000AC16@Data 
        [12]    float   9.86334038  0x0000AC18@Data 
        [13]    float   9.51670074  0x0000AC1A@Data 
        [14]    float   9.1240406   0x0000AC1C@Data 
        [15]    float   8.67337132  0x0000AC1E@Data 
        [16]    float   8.10403538  0x0000AC20@Data 
        [17]    float   7.32084227  0x0000AC22@Data 
        [18]    float   5.92091846  0x0000AC24@Data 
        [19]    float   2.58650565  0x0000AC26@Data 
        [20]    float   -13.1488333 0x0000AC28@Data 
        [21]    float   -12.8997259 0x0000AC2A@Data 
        [22]    float   -12.6568251 0x0000AC2C@Data 
        [23]    float   -12.4078951 0x0000AC2E@Data 
        [24]    float   -12.1559563 0x0000AC30@Data 
        [25]    float   -11.900712  0x0000AC32@Data 
        [26]    float   -11.6493034 0x0000AC34@Data 
        [27]    float   -11.3891516 0x0000AC36@Data 
        [28]    float   -11.1243477 0x0000AC38@Data 
        [29]    float   -10.8451681 0x0000AC3A@Data 
        [30]    float   -10.561676  0x0000AC3C@Data 
        [31]    float   -10.260046  0x0000AC3E@Data 
        [32]    float   -9.94065475 0x0000AC40@Data 
        [33]    float   -9.59283257 0x0000AC42@Data 
        [34]    float   -9.20984173 0x0000AC44@Data 
        [35]    float   -8.76293468 0x0000AC46@Data 
        [36]    float   -8.21562099 0x0000AC48@Data 
        [37]    float   -7.48506212 0x0000AC4A@Data 
        [38]    float   -6.25160313 0x0000AC4C@Data 
        [39]    float   -3.47886968 0x0000AC4E@Data
    '''
    # 404-1400: repeat-inv-nonl-identification-make-sure-rotor-rotate-180-deg
    ccs_expressions[tag] = '''
        [0] float   3.63729286  0x0000AB9C@Data 
        [1] float   3.45543337  0x0000AB9E@Data 
        [2] float   3.27355313  0x0000ABA0@Data 
        [3] float   3.09171224  0x0000ABA2@Data 
        [4] float   2.90981054  0x0000ABA4@Data 
        [5] float   2.72795534  0x0000ABA6@Data 
        [6] float   2.54611993  0x0000ABA8@Data 
        [7] float   2.36424923  0x0000ABAA@Data 
        [8] float   2.18240905  0x0000ABAC@Data 
        [9] float   2.00054502  0x0000ABAE@Data 
        [10]    float   1.81867599  0x0000ABB0@Data 
        [11]    float   1.63680041  0x0000ABB2@Data 
        [12]    float   1.45490539  0x0000ABB4@Data 
        [13]    float   1.27306211  0x0000ABB6@Data 
        [14]    float   1.09137404  0x0000ABB8@Data 
        [15]    float   0.909286559 0x0000ABBA@Data 
        [16]    float   0.727455974 0x0000ABBC@Data 
        [17]    float   0.545618057 0x0000ABBE@Data 
        [18]    float   0.363722801 0x0000ABC0@Data 
        [19]    float   0.181827158 0x0000ABC2@Data 
        [20]    float   -3.63728571 0x0000ABC4@Data 
        [21]    float   -3.45542717 0x0000ABC6@Data 
        [22]    float   -3.27356195 0x0000ABC8@Data 
        [23]    float   -3.09170318 0x0000ABCA@Data 
        [24]    float   -2.90983438 0x0000ABCC@Data 
        [25]    float   -2.72799897 0x0000ABCE@Data 
        [26]    float   -2.54610944 0x0000ABD0@Data 
        [27]    float   -2.36423349 0x0000ABD2@Data 
        [28]    float   -2.18237829 0x0000ABD4@Data 
        [29]    float   -2.00052166 0x0000ABD6@Data 
        [30]    float   -1.81866062 0x0000ABD8@Data 
        [31]    float   -1.63681281 0x0000ABDA@Data 
        [32]    float   -1.45491719 0x0000ABDC@Data 
        [33]    float   -1.27306914 0x0000ABDE@Data 
        [34]    float   -1.09117019 0x0000ABE0@Data 
        [35]    float   -0.909320414    0x0000ABE2@Data 
        [36]    float   -0.727435648    0x0000ABE4@Data 
        [37]    float   -0.545579553    0x0000ABE6@Data 
        [38]    float   -0.363732666    0x0000ABE8@Data 
        [39]    float   -0.181860745    0x0000ABEA@Data 

        [0] float   13.1755095  0x0000AC00@Data 
        [1] float   12.9325647  0x0000AC02@Data 
        [2] float   12.6917152  0x0000AC04@Data 
        [3] float   12.4487648  0x0000AC06@Data 
        [4] float   12.2026997  0x0000AC08@Data 
        [5] float   11.9476185  0x0000AC0A@Data 
        [6] float   11.6863184  0x0000AC0C@Data 
        [7] float   11.4314375  0x0000AC0E@Data 
        [8] float   11.1573305  0x0000AC10@Data 
        [9] float   10.881176   0x0000AC12@Data 
        [10]    float   10.58671    0x0000AC14@Data 
        [11]    float   10.2872744  0x0000AC16@Data 
        [12]    float   9.96420193  0x0000AC18@Data 
        [13]    float   9.61152554  0x0000AC1A@Data 
        [14]    float   9.20501137  0x0000AC1C@Data 
        [15]    float   8.75306892  0x0000AC1E@Data 
        [16]    float   8.17843342  0x0000AC20@Data 
        [17]    float   7.38231182  0x0000AC22@Data 
        [18]    float   5.95819044  0x0000AC24@Data 
        [19]    float   2.544662    0x0000AC26@Data 
        [20]    float   -13.1424265 0x0000AC28@Data 
        [21]    float   -12.9039965 0x0000AC2A@Data 
        [22]    float   -12.6651793 0x0000AC2C@Data 
        [23]    float   -12.4205627 0x0000AC2E@Data 
        [24]    float   -12.1723251 0x0000AC30@Data 
        [25]    float   -11.9200411 0x0000AC32@Data 
        [26]    float   -11.6631927 0x0000AC34@Data 
        [27]    float   -11.400959  0x0000AC36@Data 
        [28]    float   -11.1318483 0x0000AC38@Data 
        [29]    float   -10.8492031 0x0000AC3A@Data 
        [30]    float   -10.5676336 0x0000AC3C@Data 
        [31]    float   -10.2654238 0x0000AC3E@Data 
        [32]    float   -9.9474268  0x0000AC40@Data 
        [33]    float   -9.60289478 0x0000AC42@Data 
        [34]    float   -9.22563171 0x0000AC44@Data 
        [35]    float   -8.78132057 0x0000AC46@Data 
        [36]    float   -8.23554802 0x0000AC48@Data 
        [37]    float   -7.50510931 0x0000AC4A@Data 
        [38]    float   -6.26323414 0x0000AC4C@Data 
        [39]    float   -3.48698163 0x0000AC4E@Data 
    '''

    tag = 'SiC-414-1700-phaseB-20V'
    # 414-1700
    ccs_expressions[tag] = '''
        i_data_R1   float[50]   [3.63730574,3.4554615,3.27352619,3.09168673,2.90984678...]  0x0000AC1C@Data 
            [0] float   3.63730574  0x0000AC1C@Data 
            [1] float   3.4554615   0x0000AC1E@Data 
            [2] float   3.27352619  0x0000AC20@Data 
            [3] float   3.09168673  0x0000AC22@Data 
            [4] float   2.90984678  0x0000AC24@Data 
            [5] float   2.72798347  0x0000AC26@Data 
            [6] float   2.54611516  0x0000AC28@Data 
            [7] float   2.36425161  0x0000AC2A@Data 
            [8] float   2.18234968  0x0000AC2C@Data 
            [9] float   2.00048637  0x0000AC2E@Data 
            [10]    float   1.81863487  0x0000AC30@Data 
            [11]    float   1.63679731  0x0000AC32@Data 
            [12]    float   1.45492446  0x0000AC34@Data 
            [13]    float   1.27303374  0x0000AC36@Data 
            [14]    float   1.09120083  0x0000AC38@Data 
            [15]    float   0.909314513 0x0000AC3A@Data 
            [16]    float   0.727460504 0x0000AC3C@Data 
            [17]    float   0.545578897 0x0000AC3E@Data 
            [18]    float   0.363728672 0x0000AC40@Data 
            [19]    float   0.181850672 0x0000AC42@Data 
            [20]    float   -3.63723135 0x0000AC44@Data 
            [21]    float   -3.45539689 0x0000AC46@Data 
            [22]    float   -3.27355623 0x0000AC48@Data 
            [23]    float   -3.09167385 0x0000AC4A@Data 
            [24]    float   -2.90984964 0x0000AC4C@Data 
            [25]    float   -2.72803402 0x0000AC4E@Data 
            [26]    float   -2.54609847 0x0000AC50@Data 
            [27]    float   -2.36424041 0x0000AC52@Data 
            [28]    float   -2.18237424 0x0000AC54@Data 
            [29]    float   -2.00048876 0x0000AC56@Data 
            [30]    float   -1.81865489 0x0000AC58@Data 
            [31]    float   -1.63676381 0x0000AC5A@Data 
            [32]    float   -1.45489383 0x0000AC5C@Data 
            [33]    float   -1.27305698 0x0000AC5E@Data 
            [34]    float   -1.09121633 0x0000AC60@Data 
            [35]    float   -0.90932107 0x0000AC62@Data 
            [36]    float   -0.727443755    0x0000AC64@Data 
            [37]    float   -0.545589983    0x0000AC66@Data 
            [38]    float   -0.363734603    0x0000AC68@Data 
            [39]    float   -0.181877434    0x0000AC6A@Data 

            [0] float   5.74601936  0x0000AC80@Data 
            [1] float   5.52868891  0x0000AC82@Data 
            [2] float   5.313025    0x0000AC84@Data 
            [3] float   5.10348177  0x0000AC86@Data 
            [4] float   4.88542366  0x0000AC88@Data 
            [5] float   4.66787148  0x0000AC8A@Data 
            [6] float   4.44983244  0x0000AC8C@Data 
            [7] float   4.23577213  0x0000AC8E@Data 
            [8] float   4.0186758   0x0000AC90@Data 
            [9] float   3.80177093  0x0000AC92@Data 
            [10]    float   3.58355403  0x0000AC94@Data 
            [11]    float   3.36824822  0x0000AC96@Data 
            [12]    float   3.14764524  0x0000AC98@Data 
            [13]    float   2.92531514  0x0000AC9A@Data 
            [14]    float   2.69799185  0x0000AC9C@Data 
            [15]    float   2.47029567  0x0000AC9E@Data 
            [16]    float   2.22905397  0x0000ACA0@Data 
            [17]    float   1.96887064  0x0000ACA2@Data 
            [18]    float   1.67734015  0x0000ACA4@Data 
            [19]    float   1.26687074  0x0000ACA6@Data 
            [20]    float   -5.92496777 0x0000ACA8@Data 
            [21]    float   -5.70774078 0x0000ACAA@Data 
            [22]    float   -5.49062443 0x0000ACAC@Data 
            [23]    float   -5.27258587 0x0000ACAE@Data 
            [24]    float   -5.05030537 0x0000ACB0@Data 
            [25]    float   -4.82586861 0x0000ACB2@Data 
            [26]    float   -4.60219622 0x0000ACB4@Data 
            [27]    float   -4.3749032  0x0000ACB6@Data 
            [28]    float   -4.14504957 0x0000ACB8@Data 
            [29]    float   -3.91519785 0x0000ACBA@Data 
            [30]    float   -3.68602252 0x0000ACBC@Data 
            [31]    float   -3.45333815 0x0000ACBE@Data 
            [32]    float   -3.22258997 0x0000ACC0@Data 
            [33]    float   -2.98600006 0x0000ACC2@Data 
            [34]    float   -2.75101399 0x0000ACC4@Data 
            [35]    float   -2.51083159 0x0000ACC6@Data 
            [36]    float   -2.26278925 0x0000ACC8@Data 
            [37]    float   -1.99922812 0x0000ACCA@Data 
            [38]    float   -1.70548534 0x0000ACCC@Data 
            [39]    float   -1.29366708 0x0000ACCE@Data 
    '''
    # 414-1700: repeat
    ccs_expressions[tag] = '''
        i_data_R1   float[50]   [3.63723469,3.45548892,3.27357769,3.09167337,2.90985751...] 0x0000AC1C@Data 
            [0] float   3.63723469  0x0000AC1C@Data 
            [1] float   3.45548892  0x0000AC1E@Data 
            [2] float   3.27357769  0x0000AC20@Data 
            [3] float   3.09167337  0x0000AC22@Data 
            [4] float   2.90985751  0x0000AC24@Data 
            [5] float   2.72800183  0x0000AC26@Data 
            [6] float   2.5461185   0x0000AC28@Data 
            [7] float   2.36423445  0x0000AC2A@Data 
            [8] float   2.18241501  0x0000AC2C@Data 
            [9] float   2.00049663  0x0000AC2E@Data 
            [10]    float   1.81866586  0x0000AC30@Data 
            [11]    float   1.636814    0x0000AC32@Data 
            [12]    float   1.45490062  0x0000AC34@Data 
            [13]    float   1.27304387  0x0000AC36@Data 
            [14]    float   1.09120071  0x0000AC38@Data 
            [15]    float   0.909338892 0x0000AC3A@Data 
            [16]    float   0.727436602 0x0000AC3C@Data 
            [17]    float   0.545606494 0x0000AC3E@Data 
            [18]    float   0.36370784  0x0000AC40@Data 
            [19]    float   0.181864589 0x0000AC42@Data 
            [20]    float   -3.63731313 0x0000AC44@Data 
            [21]    float   -3.45541072 0x0000AC46@Data 
            [22]    float   -3.27354217 0x0000AC48@Data 
            [23]    float   -3.09173226 0x0000AC4A@Data 
            [24]    float   -2.90987349 0x0000AC4C@Data 
            [25]    float   -2.72796798 0x0000AC4E@Data 
            [26]    float   -2.54609203 0x0000AC50@Data 
            [27]    float   -2.36424756 0x0000AC52@Data 
            [28]    float   -2.18234658 0x0000AC54@Data 
            [29]    float   -2.00054741 0x0000AC56@Data 
            [30]    float   -1.81869578 0x0000AC58@Data 
            [31]    float   -1.63678086 0x0000AC5A@Data 
            [32]    float   -1.45491767 0x0000AC5C@Data 
            [33]    float   -1.27305961 0x0000AC5E@Data 
            [34]    float   -1.09120941 0x0000AC60@Data 
            [35]    float   -0.909334362    0x0000AC62@Data 
            [36]    float   -0.727467537    0x0000AC64@Data 
            [37]    float   -0.545610368    0x0000AC66@Data 
            [38]    float   -0.363717496    0x0000AC68@Data 
            [39]    float   -0.181877375    0x0000AC6A@Data 

            [0] float   5.88333368  0x0000AC80@Data 
            [1] float   5.65644455  0x0000AC82@Data 
            [2] float   5.43310261  0x0000AC84@Data 
            [3] float   5.21348286  0x0000AC86@Data 
            [4] float   4.98741961  0x0000AC88@Data 
            [5] float   4.76386881  0x0000AC8A@Data 
            [6] float   4.53828716  0x0000AC8C@Data 
            [7] float   4.31564569  0x0000AC8E@Data 
            [8] float   4.09140778  0x0000AC90@Data 
            [9] float   3.8643415   0x0000AC92@Data 
            [10]    float   3.63798952  0x0000AC94@Data 
            [11]    float   3.41466737  0x0000AC96@Data 
            [12]    float   3.18602204  0x0000AC98@Data 
            [13]    float   2.95658207  0x0000AC9A@Data 
            [14]    float   2.72322559  0x0000AC9C@Data 
            [15]    float   2.48941088  0x0000AC9E@Data 
            [16]    float   2.24424171  0x0000ACA0@Data 
            [17]    float   1.98046374  0x0000ACA2@Data 
            [18]    float   1.68413496  0x0000ACA4@Data 
            [19]    float   1.27063942  0x0000ACA6@Data 
            [20]    float   -5.90329504 0x0000ACA8@Data 
            [21]    float   -5.67932034 0x0000ACAA@Data 
            [22]    float   -5.45552015 0x0000ACAC@Data 
            [23]    float   -5.23024321 0x0000ACAE@Data 
            [24]    float   -5.00153589 0x0000ACB0@Data 
            [25]    float   -4.77276611 0x0000ACB2@Data 
            [26]    float   -4.54950714 0x0000ACB4@Data 
            [27]    float   -4.32142353 0x0000ACB6@Data 
            [28]    float   -4.09509563 0x0000ACB8@Data 
            [29]    float   -3.86573029 0x0000ACBA@Data 
            [30]    float   -3.63881087 0x0000ACBC@Data 
            [31]    float   -3.41105318 0x0000ACBE@Data 
            [32]    float   -3.18097854 0x0000ACC0@Data 
            [33]    float   -2.95012712 0x0000ACC2@Data 
            [34]    float   -2.71735096 0x0000ACC4@Data 
            [35]    float   -2.48133469 0x0000ACC6@Data 
            [36]    float   -2.23403168 0x0000ACC8@Data 
            [37]    float   -1.97334933 0x0000ACCA@Data 
            [38]    float   -1.68327832 0x0000ACCC@Data 
            [39]    float   -1.27944911 0x0000ACCE@Data 
        '''


    tag = 'Mini6PhaseIPMInverter-429-1245-phaseB-180V'
    ccs_expressions[tag] = '''
        [0] float   3.63732219  0x0000AC1C@Data 
        [1] float   3.45547128  0x0000AC1E@Data 
        [2] float   3.27362514  0x0000AC20@Data 
        [3] float   3.0917027   0x0000AC22@Data 
        [4] float   2.90981627  0x0000AC24@Data 
        [5] float   2.72798514  0x0000AC26@Data 
        [6] float   2.5460887   0x0000AC28@Data 
        [7] float   2.36423945  0x0000AC2A@Data 
        [8] float   2.18237519  0x0000AC2C@Data 
        [9] float   2.00051022  0x0000AC2E@Data 
        [10]    float   1.81866193  0x0000AC30@Data 
        [11]    float   1.63678253  0x0000AC32@Data 
        [12]    float   1.45487738  0x0000AC34@Data 
        [13]    float   1.27304924  0x0000AC36@Data 
        [14]    float   1.09116697  0x0000AC38@Data 
        [15]    float   0.909277499 0x0000AC3A@Data 
        [16]    float   0.727471948 0x0000AC3C@Data 
        [17]    float   0.545563459 0x0000AC3E@Data 
        [18]    float   0.3637169   0x0000AC40@Data 
        [19]    float   0.181829289 0x0000AC42@Data 
        [20]    float   -3.63726854 0x0000AC44@Data 
        [21]    float   -3.45543623 0x0000AC46@Data 
        [22]    float   -3.27361178 0x0000AC48@Data 
        [23]    float   -3.09168482 0x0000AC4A@Data 
        [24]    float   -2.90986919 0x0000AC4C@Data 
        [25]    float   -2.72797275 0x0000AC4E@Data 
        [26]    float   -2.54607701 0x0000AC50@Data 
        [27]    float   -2.36429834 0x0000AC52@Data 
        [28]    float   -2.18234611 0x0000AC54@Data 
        [29]    float   -2.0005219  0x0000AC56@Data 
        [30]    float   -1.81865013 0x0000AC58@Data 
        [31]    float   -1.6368382  0x0000AC5A@Data 
        [32]    float   -1.45493996 0x0000AC5C@Data 
        [33]    float   -1.27303433 0x0000AC5E@Data 
        [34]    float   -1.09123051 0x0000AC60@Data 
        [35]    float   -0.90939784 0x0000AC62@Data 
        [36]    float   -0.727446318    0x0000AC64@Data 
        [37]    float   -0.545586884    0x0000AC66@Data 
        [38]    float   -0.363688529    0x0000AC68@Data 
        [39]    float   -0.181830421    0x0000AC6A@Data 

        [0] float   14.061305   0x0000AC80@Data 
        [1] float   13.8478937  0x0000AC82@Data 
        [2] float   13.6306372  0x0000AC84@Data 
        [3] float   13.4035368  0x0000AC86@Data 
        [4] float   13.1867685  0x0000AC88@Data 
        [5] float   12.9642916  0x0000AC8A@Data 
        [6] float   12.7359104  0x0000AC8C@Data 
        [7] float   12.5129395  0x0000AC8E@Data 
        [8] float   12.2784081  0x0000AC90@Data 
        [9] float   12.058156   0x0000AC92@Data 
        [10]    float   11.8181324  0x0000AC94@Data 
        [11]    float   11.57623    0x0000AC96@Data 
        [12]    float   11.3376446  0x0000AC98@Data 
        [13]    float   11.0844069  0x0000AC9A@Data 
        [14]    float   10.8278837  0x0000AC9C@Data 
        [15]    float   10.5501795  0x0000AC9E@Data 
        [16]    float   10.23769    0x0000ACA0@Data 
        [17]    float   9.880126    0x0000ACA2@Data 
        [18]    float   9.4016819   0x0000ACA4@Data 
        [19]    float   8.54157066  0x0000ACA6@Data 
        [20]    float   -14.0781918 0x0000ACA8@Data 
        [21]    float   -13.8599644 0x0000ACAA@Data 
        [22]    float   -13.6287451 0x0000ACAC@Data 
        [23]    float   -13.4091187 0x0000ACAE@Data 
        [24]    float   -13.1820641 0x0000ACB0@Data 
        [25]    float   -12.9590559 0x0000ACB2@Data 
        [26]    float   -12.742506  0x0000ACB4@Data 
        [27]    float   -12.5088987 0x0000ACB6@Data 
        [28]    float   -12.2849665 0x0000ACB8@Data 
        [29]    float   -12.0481472 0x0000ACBA@Data 
        [30]    float   -11.8182993 0x0000ACBC@Data 
        [31]    float   -11.5794659 0x0000ACBE@Data 
        [32]    float   -11.3273678 0x0000ACC0@Data 
        [33]    float   -11.0715933 0x0000ACC2@Data 
        [34]    float   -10.7959871 0x0000ACC4@Data 
        [35]    float   -10.5260715 0x0000ACC6@Data 
        [36]    float   -10.2261162 0x0000ACC8@Data 
        [37]    float   -9.85917568 0x0000ACCA@Data 
        [38]    float   -9.35707951 0x0000ACCC@Data 
        [39]    float   -8.39540958 0x0000ACCE@Data 
    '''


    tag = 'Mini6PhaseIPMInverter-528-0927-phaseB-80V'
    ccs_expressions[tag] = '''
        [0] float   3.63733578  0x0000AB1C@Data 
        [1] float   3.45550728  0x0000AB1E@Data 
        [2] float   3.27359462  0x0000AB20@Data 
        [3] float   3.09172297  0x0000AB22@Data 
        [4] float   2.90984821  0x0000AB24@Data 
        [5] float   2.7279675   0x0000AB26@Data 
        [6] float   2.54615569  0x0000AB28@Data 
        [7] float   2.36431432  0x0000AB2A@Data 
        [8] float   2.18240976  0x0000AB2C@Data 
        [9] float   2.00056934  0x0000AB2E@Data 
        [10]    float   1.81861091  0x0000AB30@Data 
        [11]    float   1.63678157  0x0000AB32@Data 
        [12]    float   1.45490265  0x0000AB34@Data 
        [13]    float   1.27309632  0x0000AB36@Data 
        [14]    float   1.09114826  0x0000AB38@Data 
        [15]    float   0.909252882 0x0000AB3A@Data 
        [16]    float   0.727468848 0x0000AB3C@Data 
        [17]    float   0.545609295 0x0000AB3E@Data 
        [18]    float   0.363777637 0x0000AB40@Data 
        [19]    float   0.181891367 0x0000AB42@Data 
        [20]    float   -3.63733006 0x0000AB44@Data 
        [21]    float   -3.45540857 0x0000AB46@Data 
        [22]    float   -3.27358961 0x0000AB48@Data 
        [23]    float   -3.09172726 0x0000AB4A@Data 
        [24]    float   -2.90980005 0x0000AB4C@Data 
        [25]    float   -2.72804475 0x0000AB4E@Data 
        [26]    float   -2.54610014 0x0000AB50@Data 
        [27]    float   -2.36422682 0x0000AB52@Data 
        [28]    float   -2.18238235 0x0000AB54@Data 
        [29]    float   -2.00052428 0x0000AB56@Data 
        [30]    float   -1.81866443 0x0000AB58@Data 
        [31]    float   -1.63677192 0x0000AB5A@Data 
        [32]    float   -1.45494795 0x0000AB5C@Data 
        [33]    float   -1.27309716 0x0000AB5E@Data 
        [34]    float   -1.09122181 0x0000AB60@Data 
        [35]    float   -0.90928036 0x0000AB62@Data 
        [36]    float   -0.727465987    0x0000AB64@Data 
        [37]    float   -0.545618832    0x0000AB66@Data 
        [38]    float   -0.363722324    0x0000AB68@Data 
        [39]    float   -0.181859985    0x0000AB6A@Data 

        [0] float   9.16318321  0x0000AB80@Data 
        [1] float   8.95464993  0x0000AB82@Data 
        [2] float   8.73911476  0x0000AB84@Data 
        [3] float   8.51909733  0x0000AB86@Data 
        [4] float   8.29693127  0x0000AB88@Data 
        [5] float   8.07912636  0x0000AB8A@Data 
        [6] float   7.86203766  0x0000AB8C@Data 
        [7] float   7.64032841  0x0000AB8E@Data 
        [8] float   7.41292477  0x0000AB90@Data 
        [9] float   7.19714785  0x0000AB92@Data 
        [10]    float   6.97566557  0x0000AB94@Data 
        [11]    float   6.74546051  0x0000AB96@Data 
        [12]    float   6.51359987  0x0000AB98@Data 
        [13]    float   6.275702    0x0000AB9A@Data 
        [14]    float   6.03611231  0x0000AB9C@Data 
        [15]    float   5.78787088  0x0000AB9E@Data 
        [16]    float   5.52931166  0x0000ABA0@Data 
        [17]    float   5.2530961   0x0000ABA2@Data 
        [18]    float   4.93029308  0x0000ABA4@Data 
        [19]    float   4.42584944  0x0000ABA6@Data 
        [20]    float   -9.2525959  0x0000ABA8@Data 
        [21]    float   -9.03854179 0x0000ABAA@Data 
        [22]    float   -8.81896591 0x0000ABAC@Data 
        [23]    float   -8.5980978  0x0000ABAE@Data 
        [24]    float   -8.37911606 0x0000ABB0@Data 
        [25]    float   -8.16014481 0x0000ABB2@Data 
        [26]    float   -7.94015789 0x0000ABB4@Data 
        [27]    float   -7.7188158  0x0000ABB6@Data 
        [28]    float   -7.5004859  0x0000ABB8@Data 
        [29]    float   -7.27689505 0x0000ABBA@Data 
        [30]    float   -7.05069399 0x0000ABBC@Data 
        [31]    float   -6.82616901 0x0000ABBE@Data 
        [32]    float   -6.59170771 0x0000ABC0@Data 
        [33]    float   -6.35672903 0x0000ABC2@Data 
        [34]    float   -6.1167841  0x0000ABC4@Data 
        [35]    float   -5.87173557 0x0000ABC6@Data 
        [36]    float   -5.6260972  0x0000ABC8@Data 
        [37]    float   -5.35200548 0x0000ABCA@Data 
        [38]    float   -5.04272366 0x0000ABCC@Data 
        [39]    float   -4.63113546 0x0000ABCE@Data 
    '''

    tag = 'Mini6PhaseIPMInverter-528-0927-phaseB-80V[294-Points]-3A'
    ccs_expressions[tag] = '''
        [0] float   2.59806228  0x0000A89C@Data 
        [1] float   2.5804565   0x0000A89E@Data 
        [2] float   2.56271172  0x0000A8A0@Data 
        [3] float   2.54501009  0x0000A8A2@Data 
        [4] float   2.52740335  0x0000A8A4@Data 
        [5] float   2.50973678  0x0000A8A6@Data 
        [6] float   2.49205446  0x0000A8A8@Data 
        [7] float   2.47432828  0x0000A8AA@Data 
        [8] float   2.45668769  0x0000A8AC@Data 
        [9] float   2.43903637  0x0000A8AE@Data 
        [10]    float   2.42136955  0x0000A8B0@Data 
        [11]    float   2.40369368  0x0000A8B2@Data 
        [12]    float   2.38595033  0x0000A8B4@Data 
        [13]    float   2.36838555  0x0000A8B6@Data 
        [14]    float   2.35065484  0x0000A8B8@Data 
        [15]    float   2.33293128  0x0000A8BA@Data 
        [16]    float   2.31531239  0x0000A8BC@Data 
        [17]    float   2.29761171  0x0000A8BE@Data 
        [18]    float   2.27993131  0x0000A8C0@Data 
        [19]    float   2.26228046  0x0000A8C2@Data 
        [20]    float   2.24461126  0x0000A8C4@Data 
        [21]    float   2.22694254  0x0000A8C6@Data 
        [22]    float   2.20927691  0x0000A8C8@Data 
        [23]    float   2.19161582  0x0000A8CA@Data 
        [24]    float   2.17388129  0x0000A8CC@Data 
        [25]    float   2.15624619  0x0000A8CE@Data 
        [26]    float   2.13857198  0x0000A8D0@Data 
        [27]    float   2.12088847  0x0000A8D2@Data 
        [28]    float   2.10317135  0x0000A8D4@Data 
        [29]    float   2.08552408  0x0000A8D6@Data 
        [30]    float   2.06790447  0x0000A8D8@Data 
        [31]    float   2.05014443  0x0000A8DA@Data 
        [32]    float   2.03252435  0x0000A8DC@Data 
        [33]    float   2.01482701  0x0000A8DE@Data 
        [34]    float   1.99714267  0x0000A8E0@Data 
        [35]    float   1.97949088  0x0000A8E2@Data 
        [36]    float   1.96180999  0x0000A8E4@Data 
        [37]    float   1.9441154   0x0000A8E6@Data 
        [38]    float   1.92645812  0x0000A8E8@Data 
        [39]    float   1.9088372   0x0000A8EA@Data 
        [40]    float   1.89113212  0x0000A8EC@Data 
        [41]    float   1.87346756  0x0000A8EE@Data 
        [42]    float   1.85576427  0x0000A8F0@Data 
        [43]    float   1.83806944  0x0000A8F2@Data 
        [44]    float   1.82040417  0x0000A8F4@Data 
        [45]    float   1.80275166  0x0000A8F6@Data 
        [46]    float   1.78508902  0x0000A8F8@Data 
        [47]    float   1.7673645   0x0000A8FA@Data 
        [48]    float   1.74971604  0x0000A8FC@Data 
        [49]    float   1.7320751   0x0000A8FE@Data 
        [50]    float   1.71435511  0x0000A900@Data 
        [51]    float   1.69669688  0x0000A902@Data 
        [52]    float   1.67901433  0x0000A904@Data 
        [53]    float   1.66134644  0x0000A906@Data 
        [54]    float   1.64366949  0x0000A908@Data 
        [55]    float   1.62598634  0x0000A90A@Data 
        [56]    float   1.60832882  0x0000A90C@Data 
        [57]    float   1.59066784  0x0000A90E@Data 
        [58]    float   1.57300329  0x0000A910@Data 
        [59]    float   1.55532181  0x0000A912@Data 
        [60]    float   1.53762591  0x0000A914@Data 
        [61]    float   1.51992357  0x0000A916@Data 
        [62]    float   1.50225854  0x0000A918@Data 
        [63]    float   1.48467171  0x0000A91A@Data 
        [64]    float   1.46695983  0x0000A91C@Data 
        [65]    float   1.44929385  0x0000A91E@Data 
        [66]    float   1.43160284  0x0000A920@Data 
        [67]    float   1.41390693  0x0000A922@Data 
        [68]    float   1.39625323  0x0000A924@Data 
        [69]    float   1.37861681  0x0000A926@Data 
        [70]    float   1.36090219  0x0000A928@Data 
        [71]    float   1.34318912  0x0000A92A@Data 
        [72]    float   1.32549894  0x0000A92C@Data 
        [73]    float   1.30788815  0x0000A92E@Data 
        [74]    float   1.29021037  0x0000A930@Data 
        [75]    float   1.27254379  0x0000A932@Data 
        [76]    float   1.25483429  0x0000A934@Data 
        [77]    float   1.23715842  0x0000A936@Data 
        [78]    float   1.21953523  0x0000A938@Data 
        [79]    float   1.20183933  0x0000A93A@Data 
        [80]    float   1.18410397  0x0000A93C@Data 
        [81]    float   1.16650605  0x0000A93E@Data 
        [82]    float   1.14879298  0x0000A940@Data 
        [83]    float   1.13111722  0x0000A942@Data 
        [84]    float   1.11350203  0x0000A944@Data 
        [85]    float   1.09576774  0x0000A946@Data 
        [86]    float   1.07814562  0x0000A948@Data 
        [87]    float   1.06042886  0x0000A94A@Data 
        [88]    float   1.04275215  0x0000A94C@Data 
        [89]    float   1.02507508  0x0000A94E@Data 
        [90]    float   1.00741708  0x0000A950@Data 
        [91]    float   0.989750981 0x0000A952@Data 
        [92]    float   0.972093344 0x0000A954@Data 
        [93]    float   0.954402924 0x0000A956@Data 
        [94]    float   0.936734498 0x0000A958@Data 
        [95]    float   0.919037402 0x0000A95A@Data 
        [96]    float   0.901361883 0x0000A95C@Data 
        [97]    float   0.883682251 0x0000A95E@Data 
        [98]    float   0.866026103 0x0000A960@Data 
        [99]    float   0.848392725 0x0000A962@Data 
        [100]   float   0.830660522 0x0000A964@Data 
        [101]   float   0.812983036 0x0000A966@Data 
        [102]   float   0.795346081 0x0000A968@Data 
        [103]   float   0.777648032 0x0000A96A@Data 
        [104]   float   0.759972274 0x0000A96C@Data 
        [105]   float   0.742322445 0x0000A96E@Data 
        [106]   float   0.724653125 0x0000A970@Data 
        [107]   float   0.706965387 0x0000A972@Data 
        [108]   float   0.689249098 0x0000A974@Data 
        [109]   float   0.671650767 0x0000A976@Data 
        [110]   float   0.653971434 0x0000A978@Data 
        [111]   float   0.636277437 0x0000A97A@Data 
        [112]   float   0.618586779 0x0000A97C@Data 
        [113]   float   0.600960732 0x0000A97E@Data 
        [114]   float   0.583224475 0x0000A980@Data 
        [115]   float   0.56562084  0x0000A982@Data 
        [116]   float   0.547870338 0x0000A984@Data 
        [117]   float   0.530236065 0x0000A986@Data 
        [118]   float   0.512529373 0x0000A988@Data 
        [119]   float   0.494901925 0x0000A98A@Data 
        [120]   float   0.477174938 0x0000A98C@Data 
        [121]   float   0.459529817 0x0000A98E@Data 
        [122]   float   0.441861928 0x0000A990@Data 
        [123]   float   0.424156308 0x0000A992@Data 
        [124]   float   0.406519294 0x0000A994@Data 
        [125]   float   0.388834357 0x0000A996@Data 
        [126]   float   0.371170819 0x0000A998@Data 
        [127]   float   0.353475749 0x0000A99A@Data 
        [128]   float   0.335830599 0x0000A99C@Data 
        [129]   float   0.318131119 0x0000A99E@Data 
        [130]   float   0.300454825 0x0000A9A0@Data 
        [131]   float   0.28280285  0x0000A9A2@Data 
        [132]   float   0.265152395 0x0000A9A4@Data 
        [133]   float   0.247416914 0x0000A9A6@Data 
        [134]   float   0.229741052 0x0000A9A8@Data 
        [135]   float   0.212102383 0x0000A9AA@Data 
        [136]   float   0.194426715 0x0000A9AC@Data 
        [137]   float   0.176731139 0x0000A9AE@Data 
        [138]   float   0.159073949 0x0000A9B0@Data 
        [139]   float   0.14140594  0x0000A9B2@Data 
        [140]   float   0.123707585 0x0000A9B4@Data 
        [141]   float   0.106034338 0x0000A9B6@Data 
        [142]   float   0.088366285 0x0000A9B8@Data 
        [143]   float   0.070687063 0x0000A9BA@Data 
        [144]   float   0.0529728234    0x0000A9BC@Data 
        [145]   float   0.0361390263    0x0000A9BE@Data 
        [146]   float   0.018234212 0x0000A9C0@Data 
        [147]   float   -2.59804797 0x0000A9C2@Data 
        [148]   float   -2.58045149 0x0000A9C4@Data 
        [149]   float   -2.56271744 0x0000A9C6@Data 
        [150]   float   -2.54506707 0x0000A9C8@Data 
        [151]   float   -2.52736902 0x0000A9CA@Data 
        [152]   float   -2.50970435 0x0000A9CC@Data 
        [153]   float   -2.49201775 0x0000A9CE@Data 
        [154]   float   -2.47431421 0x0000A9D0@Data 
        [155]   float   -2.45670342 0x0000A9D2@Data 
        [156]   float   -2.43902206 0x0000A9D4@Data 
        [157]   float   -2.42133069 0x0000A9D6@Data 
        [158]   float   -2.40368032 0x0000A9D8@Data 
        [159]   float   -2.38601041 0x0000A9DA@Data 
        [160]   float   -2.36834025 0x0000A9DC@Data 
        [161]   float   -2.35069299 0x0000A9DE@Data 
        [162]   float   -2.33294344 0x0000A9E0@Data 
        [163]   float   -2.31531811 0x0000A9E2@Data 
        [164]   float   -2.2976315  0x0000A9E4@Data 
        [165]   float   -2.27992153 0x0000A9E6@Data 
        [166]   float   -2.26226687 0x0000A9E8@Data 
        [167]   float   -2.24456191 0x0000A9EA@Data 
        [168]   float   -2.2269187  0x0000A9EC@Data 
        [169]   float   -2.20923471 0x0000A9EE@Data 
        [170]   float   -2.1915431  0x0000A9F0@Data 
        [171]   float   -2.17385268 0x0000A9F2@Data 
        [172]   float   -2.15620613 0x0000A9F4@Data 
        [173]   float   -2.13857985 0x0000A9F6@Data 
        [174]   float   -2.12087035 0x0000A9F8@Data 
        [175]   float   -2.10317039 0x0000A9FA@Data 
        [176]   float   -2.08558154 0x0000A9FC@Data 
        [177]   float   -2.06784678 0x0000A9FE@Data 
        [178]   float   -2.05023026 0x0000AA00@Data 
        [179]   float   -2.0325079  0x0000AA02@Data 
        [180]   float   -2.01481962 0x0000AA04@Data 
        [181]   float   -1.99713814 0x0000AA06@Data 
        [182]   float   -1.97944605 0x0000AA08@Data 
        [183]   float   -1.9617883  0x0000AA0A@Data 
        [184]   float   -1.94411707 0x0000AA0C@Data 
        [185]   float   -1.92641711 0x0000AA0E@Data 
        [186]   float   -1.90876079 0x0000AA10@Data 
        [187]   float   -1.89109576 0x0000AA12@Data 
        [188]   float   -1.8734566  0x0000AA14@Data 
        [189]   float   -1.855775   0x0000AA16@Data 
        [190]   float   -1.83806431 0x0000AA18@Data 
        [191]   float   -1.8204484  0x0000AA1A@Data 
        [192]   float   -1.80270493 0x0000AA1C@Data 
        [193]   float   -1.78508472 0x0000AA1E@Data 
        [194]   float   -1.76741672 0x0000AA20@Data 
        [195]   float   -1.74972224 0x0000AA22@Data 
        [196]   float   -1.73207533 0x0000AA24@Data 
        [197]   float   -1.71435392 0x0000AA26@Data 
        [198]   float   -1.69667876 0x0000AA28@Data 
        [199]   float   -1.67901933 0x0000AA2A@Data 
        [200]   float   -1.66137254 0x0000AA2C@Data 
        [201]   float   -1.64371562 0x0000AA2E@Data 
        [202]   float   -1.6260339  0x0000AA30@Data 
        [203]   float   -1.60836446 0x0000AA32@Data 
        [204]   float   -1.59064794 0x0000AA34@Data 
        [205]   float   -1.57293653 0x0000AA36@Data 
        [206]   float   -1.55533946 0x0000AA38@Data 
        [207]   float   -1.53763688 0x0000AA3A@Data 
        [208]   float   -1.5199182  0x0000AA3C@Data 
        [209]   float   -1.50227702 0x0000AA3E@Data 
        [210]   float   -1.48459756 0x0000AA40@Data 
        [211]   float   -1.46699142 0x0000AA42@Data 
        [212]   float   -1.44927061 0x0000AA44@Data 
        [213]   float   -1.43157864 0x0000AA46@Data 
        [214]   float   -1.41385531 0x0000AA48@Data 
        [215]   float   -1.39622402 0x0000AA4A@Data 
        [216]   float   -1.37860644 0x0000AA4C@Data 
        [217]   float   -1.36086226 0x0000AA4E@Data 
        [218]   float   -1.34323263 0x0000AA50@Data 
        [219]   float   -1.32554698 0x0000AA52@Data 
        [220]   float   -1.30790317 0x0000AA54@Data 
        [221]   float   -1.29017675 0x0000AA56@Data 
        [222]   float   -1.27253997 0x0000AA58@Data 
        [223]   float   -1.25484228 0x0000AA5A@Data 
        [224]   float   -1.23715353 0x0000AA5C@Data 
        [225]   float   -1.21952999 0x0000AA5E@Data 
        [226]   float   -1.20185757 0x0000AA60@Data 
        [227]   float   -1.18415666 0x0000AA62@Data 
        [228]   float   -1.16647458 0x0000AA64@Data 
        [229]   float   -1.14881527 0x0000AA66@Data 
        [230]   float   -1.13111377 0x0000AA68@Data 
        [231]   float   -1.11337864 0x0000AA6A@Data 
        [232]   float   -1.09581196 0x0000AA6C@Data 
        [233]   float   -1.07811081 0x0000AA6E@Data 
        [234]   float   -1.06048262 0x0000AA70@Data 
        [235]   float   -1.04279149 0x0000AA72@Data 
        [236]   float   -1.0250839  0x0000AA74@Data 
        [237]   float   -1.00738382 0x0000AA76@Data 
        [238]   float   -0.989731073    0x0000AA78@Data 
        [239]   float   -0.972059965    0x0000AA7A@Data 
        [240]   float   -0.954417348    0x0000AA7C@Data 
        [241]   float   -0.936706662    0x0000AA7E@Data 
        [242]   float   -0.919041455    0x0000AA80@Data 
        [243]   float   -0.901311398    0x0000AA82@Data 
        [244]   float   -0.88371104 0x0000AA84@Data 
        [245]   float   -0.865968108    0x0000AA86@Data 
        [246]   float   -0.848370612    0x0000AA88@Data 
        [247]   float   -0.830644131    0x0000AA8A@Data 
        [248]   float   -0.812997103    0x0000AA8C@Data 
        [249]   float   -0.795328677    0x0000AA8E@Data 
        [250]   float   -0.7776528  0x0000AA90@Data 
        [251]   float   -0.759964406    0x0000AA92@Data 
        [252]   float   -0.742327869    0x0000AA94@Data 
        [253]   float   -0.724647045    0x0000AA96@Data 
        [254]   float   -0.706961274    0x0000AA98@Data 
        [255]   float   -0.689306796    0x0000AA9A@Data 
        [256]   float   -0.671641171    0x0000AA9C@Data 
        [257]   float   -0.653937936    0x0000AA9E@Data 
        [258]   float   -0.636235893    0x0000AAA0@Data 
        [259]   float   -0.618575871    0x0000AAA2@Data 
        [260]   float   -0.600881338    0x0000AAA4@Data 
        [261]   float   -0.583240449    0x0000AAA6@Data 
        [262]   float   -0.565547884    0x0000AAA8@Data 
        [263]   float   -0.547898233    0x0000AAAA@Data 
        [264]   float   -0.53020525 0x0000AAAC@Data 
        [265]   float   -0.512528121    0x0000AAAE@Data 
        [266]   float   -0.494833052    0x0000AAB0@Data 
        [267]   float   -0.47719714 0x0000AAB2@Data 
        [268]   float   -0.459502965    0x0000AAB4@Data 
        [269]   float   -0.441848546    0x0000AAB6@Data 
        [270]   float   -0.424174577    0x0000AAB8@Data 
        [271]   float   -0.406544179    0x0000AABA@Data 
        [272]   float   -0.388857573    0x0000AABC@Data 
        [273]   float   -0.37117061 0x0000AABE@Data 
        [274]   float   -0.353468776    0x0000AAC0@Data 
        [275]   float   -0.335768819    0x0000AAC2@Data 
        [276]   float   -0.318145394    0x0000AAC4@Data 
        [277]   float   -0.300460428    0x0000AAC6@Data 
        [278]   float   -0.282823294    0x0000AAC8@Data 
        [279]   float   -0.26507163 0x0000AACA@Data 
        [280]   float   -0.24748227 0x0000AACC@Data 
        [281]   float   -0.229748532    0x0000AACE@Data 
        [282]   float   -0.212101549    0x0000AAD0@Data 
        [283]   float   -0.194437698    0x0000AAD2@Data 
        [284]   float   -0.176721677    0x0000AAD4@Data 
        [285]   float   -0.15906021 0x0000AAD6@Data 
        [286]   float   -0.141362682    0x0000AAD8@Data 
        [287]   float   -0.123709843    0x0000AADA@Data 
        [288]   float   -0.106046051    0x0000AADC@Data 
        [289]   float   -0.0883834362   0x0000AADE@Data 
        [290]   float   -0.0706889331   0x0000AAE0@Data 
        [291]   float   -0.0529967509   0x0000AAE2@Data 
        [292]   float   -0.035327781    0x0000AAE4@Data 
        [293]   float   -0.0176932476   0x0000AAE6@Data 

        [0] float   8.49796295  0x0000AAF4@Data 
        [1] float   8.47324276  0x0000AAF6@Data 
        [2] float   8.44746494  0x0000AAF8@Data 
        [3] float   8.42363644  0x0000AAFA@Data 
        [4] float   8.39948177  0x0000AAFC@Data 
        [5] float   8.3715744   0x0000AAFE@Data 
        [6] float   8.34673595  0x0000AB00@Data 
        [7] float   8.32256126  0x0000AB02@Data 
        [8] float   8.2960701   0x0000AB04@Data 
        [9] float   8.26931095  0x0000AB06@Data 
        [10]    float   8.24798965  0x0000AB08@Data 
        [11]    float   8.22233486  0x0000AB0A@Data 
        [12]    float   8.20199108  0x0000AB0C@Data 
        [13]    float   8.17060471  0x0000AB0E@Data 
        [14]    float   8.14575863  0x0000AB10@Data 
        [15]    float   8.12412167  0x0000AB12@Data 
        [16]    float   8.09865761  0x0000AB14@Data 
        [17]    float   8.07534695  0x0000AB16@Data 
        [18]    float   8.0507431   0x0000AB18@Data 
        [19]    float   8.02590561  0x0000AB1A@Data 
        [20]    float   7.99794388  0x0000AB1C@Data 
        [21]    float   7.97407866  0x0000AB1E@Data 
        [22]    float   7.95093822  0x0000AB20@Data 
        [23]    float   7.92200613  0x0000AB22@Data 
        [24]    float   7.89956856  0x0000AB24@Data 
        [25]    float   7.87114 0x0000AB26@Data 
        [26]    float   7.84813452  0x0000AB28@Data 
        [27]    float   7.82318068  0x0000AB2A@Data 
        [28]    float   7.7978797   0x0000AB2C@Data 
        [29]    float   7.77578354  0x0000AB2E@Data 
        [30]    float   7.74766827  0x0000AB30@Data 
        [31]    float   7.72209692  0x0000AB32@Data 
        [32]    float   7.69655418  0x0000AB34@Data 
        [33]    float   7.67075491  0x0000AB36@Data 
        [34]    float   7.64532518  0x0000AB38@Data 
        [35]    float   7.61730099  0x0000AB3A@Data 
        [36]    float   7.59147024  0x0000AB3C@Data 
        [37]    float   7.5662322   0x0000AB3E@Data 
        [38]    float   7.54304218  0x0000AB40@Data 
        [39]    float   7.51763344  0x0000AB42@Data 
        [40]    float   7.49091959  0x0000AB44@Data 
        [41]    float   7.46660137  0x0000AB46@Data 
        [42]    float   7.43946028  0x0000AB48@Data 
        [43]    float   7.41332722  0x0000AB4A@Data 
        [44]    float   7.38874483  0x0000AB4C@Data 
        [45]    float   7.36784792  0x0000AB4E@Data 
        [46]    float   7.34188032  0x0000AB50@Data 
        [47]    float   7.31681108  0x0000AB52@Data 
        [48]    float   7.29275894  0x0000AB54@Data 
        [49]    float   7.26759529  0x0000AB56@Data 
        [50]    float   7.24278641  0x0000AB58@Data 
        [51]    float   7.21583796  0x0000AB5A@Data 
        [52]    float   7.19181919  0x0000AB5C@Data 
        [53]    float   7.16313124  0x0000AB5E@Data 
        [54]    float   7.13818884  0x0000AB60@Data 
        [55]    float   7.11049461  0x0000AB62@Data 
        [56]    float   7.08459091  0x0000AB64@Data 
        [57]    float   7.05713367  0x0000AB66@Data 
        [58]    float   7.03177738  0x0000AB68@Data 
        [59]    float   7.0056262   0x0000AB6A@Data 
        [60]    float   6.98167801  0x0000AB6C@Data 
        [61]    float   6.95714283  0x0000AB6E@Data 
        [62]    float   6.92839718  0x0000AB70@Data 
        [63]    float   6.90276051  0x0000AB72@Data 
        [64]    float   6.87460756  0x0000AB74@Data 
        [65]    float   6.85169983  0x0000AB76@Data 
        [66]    float   6.82429886  0x0000AB78@Data 
        [67]    float   6.79919291  0x0000AB7A@Data 
        [68]    float   6.7707386   0x0000AB7C@Data 
        [69]    float   6.74316454  0x0000AB7E@Data 
        [70]    float   6.71785975  0x0000AB80@Data 
        [71]    float   6.69027042  0x0000AB82@Data 
        [72]    float   6.66458321  0x0000AB84@Data 
        [73]    float   6.63674021  0x0000AB86@Data 
        [74]    float   6.61179733  0x0000AB88@Data 
        [75]    float   6.58520031  0x0000AB8A@Data 
        [76]    float   6.55670452  0x0000AB8C@Data 
        [77]    float   6.53028488  0x0000AB8E@Data 
        [78]    float   6.50442982  0x0000AB90@Data 
        [79]    float   6.47319794  0x0000AB92@Data 
        [80]    float   6.44870949  0x0000AB94@Data 
        [81]    float   6.42105293  0x0000AB96@Data 
        [82]    float   6.39228296  0x0000AB98@Data 
        [83]    float   6.3638382   0x0000AB9A@Data 
        [84]    float   6.336555    0x0000AB9C@Data 
        [85]    float   6.31293726  0x0000AB9E@Data 
        [86]    float   6.28169823  0x0000ABA0@Data 
        [87]    float   6.25426674  0x0000ABA2@Data 
        [88]    float   6.2291894   0x0000ABA4@Data 
        [89]    float   6.20233583  0x0000ABA6@Data 
        [90]    float   6.17567348  0x0000ABA8@Data 
        [91]    float   6.1472702   0x0000ABAA@Data 
        [92]    float   6.11902189  0x0000ABAC@Data 
        [93]    float   6.09100914  0x0000ABAE@Data 
        [94]    float   6.06256008  0x0000ABB0@Data 
        [95]    float   6.0345521   0x0000ABB2@Data 
        [96]    float   6.00590563  0x0000ABB4@Data 
        [97]    float   5.97914124  0x0000ABB6@Data 
        [98]    float   5.94859028  0x0000ABB8@Data 
        [99]    float   5.91788054  0x0000ABBA@Data 
        [100]   float   5.89247179  0x0000ABBC@Data 
        [101]   float   5.86256313  0x0000ABBE@Data 
        [102]   float   5.83354521  0x0000ABC0@Data 
        [103]   float   5.80502748  0x0000ABC2@Data 
        [104]   float   5.77535677  0x0000ABC4@Data 
        [105]   float   5.74511051  0x0000ABC6@Data 
        [106]   float   5.71506548  0x0000ABC8@Data 
        [107]   float   5.68366385  0x0000ABCA@Data 
        [108]   float   5.65565062  0x0000ABCC@Data 
        [109]   float   5.6246047   0x0000ABCE@Data 
        [110]   float   5.59566212  0x0000ABD0@Data 
        [111]   float   5.56346273  0x0000ABD2@Data 
        [112]   float   5.53286219  0x0000ABD4@Data 
        [113]   float   5.50224638  0x0000ABD6@Data 
        [114]   float   5.47470427  0x0000ABD8@Data 
        [115]   float   5.44240141  0x0000ABDA@Data 
        [116]   float   5.41067219  0x0000ABDC@Data 
        [117]   float   5.37720823  0x0000ABDE@Data 
        [118]   float   5.34428215  0x0000ABE0@Data 
        [119]   float   5.31394768  0x0000ABE2@Data 
        [120]   float   5.28090191  0x0000ABE4@Data 
        [121]   float   5.24606323  0x0000ABE6@Data 
        [122]   float   5.21202803  0x0000ABE8@Data 
        [123]   float   5.1752224   0x0000ABEA@Data 
        [124]   float   5.13997698  0x0000ABEC@Data 
        [125]   float   5.10498619  0x0000ABEE@Data 
        [126]   float   5.06647015  0x0000ABF0@Data 
        [127]   float   5.0277276   0x0000ABF2@Data 
        [128]   float   4.98637629  0x0000ABF4@Data 
        [129]   float   4.95000648  0x0000ABF6@Data 
        [130]   float   4.90807295  0x0000ABF8@Data 
        [131]   float   4.86020756  0x0000ABFA@Data 
        [132]   float   4.82597589  0x0000ABFC@Data 
        [133]   float   4.77181768  0x0000ABFE@Data 
        [134]   float   4.71634483  0x0000AC00@Data 
        [135]   float   4.65278769  0x0000AC02@Data 
        [136]   float   4.58984756  0x0000AC04@Data 
        [137]   float   4.51937389  0x0000AC06@Data 
        [138]   float   4.43693829  0x0000AC08@Data 
        [139]   float   4.34285975  0x0000AC0A@Data 
        [140]   float   4.22656107  0x0000AC0C@Data 
        [141]   float   4.08144999  0x0000AC0E@Data 
        [142]   float   3.87561131  0x0000AC10@Data 
        [143]   float   3.55853701  0x0000AC12@Data 
        [144]   float   3.04968977  0x0000AC14@Data 
        [145]   float   1.26347184  0x0000AC16@Data 
        [146]   float   -0.866171062    0x0000AC18@Data 
        [147]   float   -8.59370136 0x0000AC1A@Data 
        [148]   float   -8.56597137 0x0000AC1C@Data 
        [149]   float   -8.5425272  0x0000AC1E@Data 
        [150]   float   -8.51799488 0x0000AC20@Data 
        [151]   float   -8.49084187 0x0000AC22@Data 
        [152]   float   -8.46846485 0x0000AC24@Data 
        [153]   float   -8.44403458 0x0000AC26@Data 
        [154]   float   -8.41942596 0x0000AC28@Data 
        [155]   float   -8.3936615  0x0000AC2A@Data 
        [156]   float   -8.36715508 0x0000AC2C@Data 
        [157]   float   -8.34282303 0x0000AC2E@Data 
        [158]   float   -8.31815243 0x0000AC30@Data 
        [159]   float   -8.29449177 0x0000AC32@Data 
        [160]   float   -8.26863766 0x0000AC34@Data 
        [161]   float   -8.24246883 0x0000AC36@Data 
        [162]   float   -8.21654224 0x0000AC38@Data 
        [163]   float   -8.19283295 0x0000AC3A@Data 
        [164]   float   -8.16980362 0x0000AC3C@Data 
        [165]   float   -8.14331055 0x0000AC3E@Data 
        [166]   float   -8.11776161 0x0000AC40@Data 
        [167]   float   -8.09288979 0x0000AC42@Data 
        [168]   float   -8.06832409 0x0000AC44@Data 
        [169]   float   -8.04399109 0x0000AC46@Data 
        [170]   float   -8.01552868 0x0000AC48@Data 
        [171]   float   -7.99400282 0x0000AC4A@Data 
        [172]   float   -7.96236134 0x0000AC4C@Data 
        [173]   float   -7.94054127 0x0000AC4E@Data 
        [174]   float   -7.9139123  0x0000AC50@Data 
        [175]   float   -7.88831139 0x0000AC52@Data 
        [176]   float   -7.86055803 0x0000AC54@Data 
        [177]   float   -7.83972168 0x0000AC56@Data 
        [178]   float   -7.81448698 0x0000AC58@Data 
        [179]   float   -7.78715563 0x0000AC5A@Data 
        [180]   float   -7.7638011  0x0000AC5C@Data 
        [181]   float   -7.74176836 0x0000AC5E@Data 
        [182]   float   -7.71464586 0x0000AC60@Data 
        [183]   float   -7.68744135 0x0000AC62@Data 
        [184]   float   -7.6628499  0x0000AC64@Data 
        [185]   float   -7.63457346 0x0000AC66@Data 
        [186]   float   -7.60957718 0x0000AC68@Data 
        [187]   float   -7.58270645 0x0000AC6A@Data 
        [188]   float   -7.5572834  0x0000AC6C@Data 
        [189]   float   -7.53497219 0x0000AC6E@Data 
        [190]   float   -7.51233578 0x0000AC70@Data 
        [191]   float   -7.48729038 0x0000AC72@Data 
        [192]   float   -7.46017647 0x0000AC74@Data 
        [193]   float   -7.43484926 0x0000AC76@Data 
        [194]   float   -7.40679407 0x0000AC78@Data 
        [195]   float   -7.38105965 0x0000AC7A@Data 
        [196]   float   -7.35451841 0x0000AC7C@Data 
        [197]   float   -7.33132124 0x0000AC7E@Data 
        [198]   float   -7.30293798 0x0000AC80@Data 
        [199]   float   -7.27813148 0x0000AC82@Data 
        [200]   float   -7.25355959 0x0000AC84@Data 
        [201]   float   -7.2265048  0x0000AC86@Data 
        [202]   float   -7.19927645 0x0000AC88@Data 
        [203]   float   -7.1735568  0x0000AC8A@Data 
        [204]   float   -7.14938974 0x0000AC8C@Data 
        [205]   float   -7.12205648 0x0000AC8E@Data 
        [206]   float   -7.09484768 0x0000AC90@Data 
        [207]   float   -7.06638384 0x0000AC92@Data 
        [208]   float   -7.04169989 0x0000AC94@Data 
        [209]   float   -7.01525259 0x0000AC96@Data 
        [210]   float   -6.98900461 0x0000AC98@Data 
        [211]   float   -6.96283245 0x0000AC9A@Data 
        [212]   float   -6.9369545  0x0000AC9C@Data 
        [213]   float   -6.90947247 0x0000AC9E@Data 
        [214]   float   -6.88453436 0x0000ACA0@Data 
        [215]   float   -6.85605764 0x0000ACA2@Data 
        [216]   float   -6.82909107 0x0000ACA4@Data 
        [217]   float   -6.80410528 0x0000ACA6@Data 
        [218]   float   -6.77652311 0x0000ACA8@Data 
        [219]   float   -6.74907112 0x0000ACAA@Data 
        [220]   float   -6.72287655 0x0000ACAC@Data 
        [221]   float   -6.69532347 0x0000ACAE@Data 
        [222]   float   -6.66903782 0x0000ACB0@Data 
        [223]   float   -6.64197063 0x0000ACB2@Data 
        [224]   float   -6.61687565 0x0000ACB4@Data 
        [225]   float   -6.58838415 0x0000ACB6@Data 
        [226]   float   -6.56192827 0x0000ACB8@Data 
        [227]   float   -6.53500509 0x0000ACBA@Data 
        [228]   float   -6.50735235 0x0000ACBC@Data 
        [229]   float   -6.48217869 0x0000ACBE@Data 
        [230]   float   -6.45247936 0x0000ACC0@Data 
        [231]   float   -6.42863417 0x0000ACC2@Data 
        [232]   float   -6.40067434 0x0000ACC4@Data 
        [233]   float   -6.37317705 0x0000ACC6@Data 
        [234]   float   -6.34580374 0x0000ACC8@Data 
        [235]   float   -6.31827068 0x0000ACCA@Data 
        [236]   float   -6.29172134 0x0000ACCC@Data 
        [237]   float   -6.26477575 0x0000ACCE@Data 
        [238]   float   -6.23474979 0x0000ACD0@Data 
        [239]   float   -6.20904541 0x0000ACD2@Data 
        [240]   float   -6.17859888 0x0000ACD4@Data 
        [241]   float   -6.15090275 0x0000ACD6@Data 
        [242]   float   -6.12245989 0x0000ACD8@Data 
        [243]   float   -6.09381342 0x0000ACDA@Data 
        [244]   float   -6.06434584 0x0000ACDC@Data 
        [245]   float   -6.03889942 0x0000ACDE@Data 
        [246]   float   -6.00909996 0x0000ACE0@Data 
        [247]   float   -5.98215628 0x0000ACE2@Data 
        [248]   float   -5.95365047 0x0000ACE4@Data 
        [249]   float   -5.9242692  0x0000ACE6@Data 
        [250]   float   -5.89493561 0x0000ACE8@Data 
        [251]   float   -5.86694431 0x0000ACEA@Data 
        [252]   float   -5.83917093 0x0000ACEC@Data 
        [253]   float   -5.81205416 0x0000ACEE@Data 
        [254]   float   -5.78335142 0x0000ACF0@Data 
        [255]   float   -5.75320148 0x0000ACF2@Data 
        [256]   float   -5.72310352 0x0000ACF4@Data 
        [257]   float   -5.69189215 0x0000ACF6@Data 
        [258]   float   -5.66814327 0x0000ACF8@Data 
        [259]   float   -5.63731623 0x0000ACFA@Data 
        [260]   float   -5.60702944 0x0000ACFC@Data 
        [261]   float   -5.57599306 0x0000ACFE@Data 
        [262]   float   -5.54789877 0x0000AD00@Data 
        [263]   float   -5.5144825  0x0000AD02@Data 
        [264]   float   -5.48313141 0x0000AD04@Data 
        [265]   float   -5.45052052 0x0000AD06@Data 
        [266]   float   -5.42043591 0x0000AD08@Data 
        [267]   float   -5.38626146 0x0000AD0A@Data 
        [268]   float   -5.35399246 0x0000AD0C@Data 
        [269]   float   -5.32200861 0x0000AD0E@Data 
        [270]   float   -5.28886604 0x0000AD10@Data 
        [271]   float   -5.25536013 0x0000AD12@Data 
        [272]   float   -5.21822214 0x0000AD14@Data 
        [273]   float   -5.1832242  0x0000AD16@Data 
        [274]   float   -5.14509296 0x0000AD18@Data 
        [275]   float   -5.10998535 0x0000AD1A@Data 
        [276]   float   -5.07071972 0x0000AD1C@Data 
        [277]   float   -5.03158855 0x0000AD1E@Data 
        [278]   float   -4.99216223 0x0000AD20@Data 
        [279]   float   -4.94829273 0x0000AD22@Data 
        [280]   float   -4.90237951 0x0000AD24@Data 
        [281]   float   -4.85998535 0x0000AD26@Data 
        [282]   float   -4.80894995 0x0000AD28@Data 
        [283]   float   -4.75941658 0x0000AD2A@Data 
        [284]   float   -4.71294165 0x0000AD2C@Data 
        [285]   float   -4.65561104 0x0000AD2E@Data 
        [286]   float   -4.58927107 0x0000AD30@Data 
        [287]   float   -4.51741695 0x0000AD32@Data 
        [288]   float   -4.43137407 0x0000AD34@Data 
        [289]   float   -4.3326683  0x0000AD36@Data 
        [290]   float   -4.21366549 0x0000AD38@Data 
        [291]   float   -4.05729866 0x0000AD3A@Data 
        [292]   float   -3.83687472 0x0000AD3C@Data 
        [293]   float   -3.53709388 0x0000AD3E@Data 
    '''

    tag = 'Mini6PhaseIPMInverter-528-0927-phaseB-80V[294-Points]-1A-[ADC offset]'
    ccs_expressions[tag] = '''
        [0] float   0.86600697  0x0000A89C@Data 
        [1] float   0.860197544 0x0000A89E@Data 
        [2] float   0.854231298 0x0000A8A0@Data 
        [3] float   0.848360002 0x0000A8A2@Data 
        [4] float   0.842451751 0x0000A8A4@Data 
        [5] float   0.836556792 0x0000A8A6@Data 
        [6] float   0.830727041 0x0000A8A8@Data 
        [7] float   0.824801445 0x0000A8AA@Data 
        [8] float   0.818903387 0x0000A8AC@Data 
        [9] float   0.813013494 0x0000A8AE@Data 
        [10]    float   0.807167947 0x0000A8B0@Data 
        [11]    float   0.801200807 0x0000A8B2@Data 
        [12]    float   0.795315385 0x0000A8B4@Data 
        [13]    float   0.789418697 0x0000A8B6@Data 
        [14]    float   0.783558547 0x0000A8B8@Data 
        [15]    float   0.777629197 0x0000A8BA@Data 
        [16]    float   0.77172941  0x0000A8BC@Data 
        [17]    float   0.765884936 0x0000A8BE@Data 
        [18]    float   0.760014534 0x0000A8C0@Data 
        [19]    float   0.754084527 0x0000A8C2@Data 
        [20]    float   0.748221457 0x0000A8C4@Data 
        [21]    float   0.742308438 0x0000A8C6@Data 
        [22]    float   0.736452758 0x0000A8C8@Data 
        [23]    float   0.730553687 0x0000A8CA@Data 
        [24]    float   0.7246539   0x0000A8CC@Data 
        [25]    float   0.718754768 0x0000A8CE@Data 
        [26]    float   0.712851048 0x0000A8D0@Data 
        [27]    float   0.70698911  0x0000A8D2@Data 
        [28]    float   0.701073527 0x0000A8D4@Data 
        [29]    float   0.695175588 0x0000A8D6@Data 
        [30]    float   0.689302623 0x0000A8D8@Data 
        [31]    float   0.683419645 0x0000A8DA@Data 
        [32]    float   0.677476883 0x0000A8DC@Data 
        [33]    float   0.671612918 0x0000A8DE@Data 
        [34]    float   0.665699661 0x0000A8E0@Data 
        [35]    float   0.659845114 0x0000A8E2@Data 
        [36]    float   0.653944731 0x0000A8E4@Data 
        [37]    float   0.648046851 0x0000A8E6@Data 
        [38]    float   0.642163336 0x0000A8E8@Data 
        [39]    float   0.636274993 0x0000A8EA@Data 
        [40]    float   0.630371034 0x0000A8EC@Data 
        [41]    float   0.624517083 0x0000A8EE@Data 
        [42]    float   0.618621409 0x0000A8F0@Data 
        [43]    float   0.612675726 0x0000A8F2@Data 
        [44]    float   0.606782913 0x0000A8F4@Data 
        [45]    float   0.600878596 0x0000A8F6@Data 
        [46]    float   0.595063806 0x0000A8F8@Data 
        [47]    float   0.589144409 0x0000A8FA@Data 
        [48]    float   0.583245575 0x0000A8FC@Data 
        [49]    float   0.577322185 0x0000A8FE@Data 
        [50]    float   0.571449816 0x0000A900@Data 
        [51]    float   0.565598428 0x0000A902@Data 
        [52]    float   0.559666514 0x0000A904@Data 
        [53]    float   0.553792179 0x0000A906@Data 
        [54]    float   0.547919989 0x0000A908@Data 
        [55]    float   0.542019129 0x0000A90A@Data 
        [56]    float   0.536109447 0x0000A90C@Data 
        [57]    float   0.530223191 0x0000A90E@Data 
        [58]    float   0.524289787 0x0000A910@Data 
        [59]    float   0.518462896 0x0000A912@Data 
        [60]    float   0.512558401 0x0000A914@Data 
        [61]    float   0.506663859 0x0000A916@Data 
        [62]    float   0.500809073 0x0000A918@Data 
        [63]    float   0.494880289 0x0000A91A@Data 
        [64]    float   0.489000767 0x0000A91C@Data 
        [65]    float   0.483099163 0x0000A91E@Data 
        [66]    float   0.477211326 0x0000A920@Data 
        [67]    float   0.471311241 0x0000A922@Data 
        [68]    float   0.46538645  0x0000A924@Data 
        [69]    float   0.459516436 0x0000A926@Data 
        [70]    float   0.453632981 0x0000A928@Data 
        [71]    float   0.447743446 0x0000A92A@Data 
        [72]    float   0.441851795 0x0000A92C@Data 
        [73]    float   0.435962051 0x0000A92E@Data 
        [74]    float   0.430069417 0x0000A930@Data 
        [75]    float   0.424164146 0x0000A932@Data 
        [76]    float   0.418282717 0x0000A934@Data 
        [77]    float   0.412412107 0x0000A936@Data 
        [78]    float   0.40654102  0x0000A938@Data 
        [79]    float   0.40060702  0x0000A93A@Data 
        [80]    float   0.394710302 0x0000A93C@Data 
        [81]    float   0.388824075 0x0000A93E@Data 
        [82]    float   0.382949829 0x0000A940@Data 
        [83]    float   0.37706089  0x0000A942@Data 
        [84]    float   0.371149093 0x0000A944@Data 
        [85]    float   0.365253061 0x0000A946@Data 
        [86]    float   0.359360695 0x0000A948@Data 
        [87]    float   0.353486717 0x0000A94A@Data 
        [88]    float   0.347574741 0x0000A94C@Data 
        [89]    float   0.341671497 0x0000A94E@Data 
        [90]    float   0.335793793 0x0000A950@Data 
        [91]    float   0.329915076 0x0000A952@Data 
        [92]    float   0.324048966 0x0000A954@Data 
        [93]    float   0.31814304  0x0000A956@Data 
        [94]    float   0.312208712 0x0000A958@Data 
        [95]    float   0.306390375 0x0000A95A@Data 
        [96]    float   0.30045718  0x0000A95C@Data 
        [97]    float   0.294562727 0x0000A95E@Data 
        [98]    float   0.288656801 0x0000A960@Data 
        [99]    float   0.282776684 0x0000A962@Data 
        [100]   float   0.276923835 0x0000A964@Data 
        [101]   float   0.271027386 0x0000A966@Data 
        [102]   float   0.265150338 0x0000A968@Data 
        [103]   float   0.259218663 0x0000A96A@Data 
        [104]   float   0.253314078 0x0000A96C@Data 
        [105]   float   0.247413516 0x0000A96E@Data 
        [106]   float   0.241553813 0x0000A970@Data 
        [107]   float   0.235636741 0x0000A972@Data 
        [108]   float   0.229754791 0x0000A974@Data 
        [109]   float   0.223856553 0x0000A976@Data 
        [110]   float   0.217992365 0x0000A978@Data 
        [111]   float   0.212050587 0x0000A97A@Data 
        [112]   float   0.206167161 0x0000A97C@Data 
        [113]   float   0.200307727 0x0000A97E@Data 
        [114]   float   0.194442675 0x0000A980@Data 
        [115]   float   0.188541308 0x0000A982@Data 
        [116]   float   0.182645917 0x0000A984@Data 
        [117]   float   0.176746562 0x0000A986@Data 
        [118]   float   0.170858234 0x0000A988@Data 
        [119]   float   0.164936662 0x0000A98A@Data 
        [120]   float   0.159061998 0x0000A98C@Data 
        [121]   float   0.153167218 0x0000A98E@Data 
        [122]   float   0.147299901 0x0000A990@Data 
        [123]   float   0.141395569 0x0000A992@Data 
        [124]   float   0.135500759 0x0000A994@Data 
        [125]   float   0.129664779 0x0000A996@Data 
        [126]   float   0.123686455 0x0000A998@Data 
        [127]   float   0.117811725 0x0000A99A@Data 
        [128]   float   0.111945078 0x0000A99C@Data 
        [129]   float   0.105981827 0x0000A99E@Data 
        [130]   float   0.100143343 0x0000A9A0@Data 
        [131]   float   0.094244808 0x0000A9A2@Data 
        [132]   float   0.0883650705    0x0000A9A4@Data 
        [133]   float   0.0825411752    0x0000A9A6@Data 
        [134]   float   0.076566495 0x0000A9A8@Data 
        [135]   float   0.0707654878    0x0000A9AA@Data 
        [136]   float   0.0647584274    0x0000A9AC@Data 
        [137]   float   0.0589883141    0x0000A9AE@Data 
        [138]   float   0.053028062 0x0000A9B0@Data 
        [139]   float   0.0472641177    0x0000A9B2@Data 
        [140]   float   0.0413398258    0x0000A9B4@Data 
        [141]   float   0.0356914662    0x0000A9B6@Data 
        [142]   float   0.0298973061    0x0000A9B8@Data 
        [143]   float   0.0238785371    0x0000A9BA@Data 
        [144]   float   0.0178308953    0x0000A9BC@Data 
        [145]   float   0.0118945874    0x0000A9BE@Data 
        [146]   float   0.00604146719   0x0000A9C0@Data 
        [147]   float   -0.866025805    0x0000A9C2@Data 
        [148]   float   -0.860146463    0x0000A9C4@Data 
        [149]   float   -0.854252756    0x0000A9C6@Data 
        [150]   float   -0.848372102    0x0000A9C8@Data 
        [151]   float   -0.842422366    0x0000A9CA@Data 
        [152]   float   -0.836532414    0x0000A9CC@Data 
        [153]   float   -0.830651164    0x0000A9CE@Data 
        [154]   float   -0.824804902    0x0000A9D0@Data 
        [155]   float   -0.818862379    0x0000A9D2@Data 
        [156]   float   -0.813012481    0x0000A9D4@Data 
        [157]   float   -0.807098806    0x0000A9D6@Data 
        [158]   float   -0.801217258    0x0000A9D8@Data 
        [159]   float   -0.795300782    0x0000A9DA@Data 
        [160]   float   -0.78942287 0x0000A9DC@Data 
        [161]   float   -0.783519089    0x0000A9DE@Data 
        [162]   float   -0.777681291    0x0000A9E0@Data 
        [163]   float   -0.771733463    0x0000A9E2@Data 
        [164]   float   -0.765917242    0x0000A9E4@Data 
        [165]   float   -0.759959757    0x0000A9E6@Data 
        [166]   float   -0.754081905    0x0000A9E8@Data 
        [167]   float   -0.74819988 0x0000A9EA@Data 
        [168]   float   -0.742320359    0x0000A9EC@Data 
        [169]   float   -0.736393869    0x0000A9EE@Data 
        [170]   float   -0.730540454    0x0000A9F0@Data 
        [171]   float   -0.724613309    0x0000A9F2@Data 
        [172]   float   -0.718766391    0x0000A9F4@Data 
        [173]   float   -0.712851822    0x0000A9F6@Data 
        [174]   float   -0.70696497 0x0000A9F8@Data 
        [175]   float   -0.701045752    0x0000A9FA@Data 
        [176]   float   -0.695153892    0x0000A9FC@Data 
        [177]   float   -0.6893242  0x0000A9FE@Data 
        [178]   float   -0.683337033    0x0000AA00@Data 
        [179]   float   -0.67751044 0x0000AA02@Data 
        [180]   float   -0.671573997    0x0000AA04@Data 
        [181]   float   -0.665718734    0x0000AA06@Data 
        [182]   float   -0.659826338    0x0000AA08@Data 
        [183]   float   -0.653955936    0x0000AA0A@Data 
        [184]   float   -0.648063302    0x0000AA0C@Data 
        [185]   float   -0.642120183    0x0000AA0E@Data 
        [186]   float   -0.636262357    0x0000AA10@Data 
        [187]   float   -0.630370796    0x0000AA12@Data 
        [188]   float   -0.624466598    0x0000AA14@Data 
        [189]   float   -0.618578494    0x0000AA16@Data 
        [190]   float   -0.612736106    0x0000AA18@Data 
        [191]   float   -0.606793344    0x0000AA1A@Data 
        [192]   float   -0.600890577    0x0000AA1C@Data 
        [193]   float   -0.595032692    0x0000AA1E@Data 
        [194]   float   -0.58912164 0x0000AA20@Data 
        [195]   float   -0.583250463    0x0000AA22@Data 
        [196]   float   -0.577315092    0x0000AA24@Data 
        [197]   float   -0.571417511    0x0000AA26@Data 
        [198]   float   -0.565543234    0x0000AA28@Data 
        [199]   float   -0.559683859    0x0000AA2A@Data 
        [200]   float   -0.553759634    0x0000AA2C@Data 
        [201]   float   -0.547907412    0x0000AA2E@Data 
        [202]   float   -0.542013824    0x0000AA30@Data 
        [203]   float   -0.536075234    0x0000AA32@Data 
        [204]   float   -0.530237377    0x0000AA34@Data 
        [205]   float   -0.524331152    0x0000AA36@Data 
        [206]   float   -0.518415272    0x0000AA38@Data 
        [207]   float   -0.51250875 0x0000AA3A@Data 
        [208]   float   -0.506633818    0x0000AA3C@Data 
        [209]   float   -0.500779212    0x0000AA3E@Data 
        [210]   float   -0.494909137    0x0000AA40@Data 
        [211]   float   -0.488972694    0x0000AA42@Data 
        [212]   float   -0.483123422    0x0000AA44@Data 
        [213]   float   -0.477206379    0x0000AA46@Data 
        [214]   float   -0.471329719    0x0000AA48@Data 
        [215]   float   -0.46542874 0x0000AA4A@Data 
        [216]   float   -0.459519744    0x0000AA4C@Data 
        [217]   float   -0.453638405    0x0000AA4E@Data 
        [218]   float   -0.447747111    0x0000AA50@Data 
        [219]   float   -0.441863716    0x0000AA52@Data 
        [220]   float   -0.435927838    0x0000AA54@Data 
        [221]   float   -0.430050194    0x0000AA56@Data 
        [222]   float   -0.424152851    0x0000AA58@Data 
        [223]   float   -0.418320447    0x0000AA5A@Data 
        [224]   float   -0.412322998    0x0000AA5C@Data 
        [225]   float   -0.40646705 0x0000AA5E@Data 
        [226]   float   -0.400580466    0x0000AA60@Data 
        [227]   float   -0.394747227    0x0000AA62@Data 
        [228]   float   -0.388823837    0x0000AA64@Data 
        [229]   float   -0.382930607    0x0000AA66@Data 
        [230]   float   -0.377038956    0x0000AA68@Data 
        [231]   float   -0.371166945    0x0000AA6A@Data 
        [232]   float   -0.365302831    0x0000AA6C@Data 
        [233]   float   -0.359397501    0x0000AA6E@Data 
        [234]   float   -0.353496641    0x0000AA70@Data 
        [235]   float   -0.347564399    0x0000AA72@Data 
        [236]   float   -0.341719717    0x0000AA74@Data 
        [237]   float   -0.335776091    0x0000AA76@Data 
        [238]   float   -0.329871953    0x0000AA78@Data 
        [239]   float   -0.324028641    0x0000AA7A@Data 
        [240]   float   -0.318119735    0x0000AA7C@Data 
        [241]   float   -0.312205762    0x0000AA7E@Data 
        [242]   float   -0.30634734 0x0000AA80@Data 
        [243]   float   -0.300485939    0x0000AA82@Data 
        [244]   float   -0.294569463    0x0000AA84@Data 
        [245]   float   -0.288667142    0x0000AA86@Data 
        [246]   float   -0.282817423    0x0000AA88@Data 
        [247]   float   -0.276864409    0x0000AA8A@Data 
        [248]   float   -0.270992845    0x0000AA8C@Data 
        [249]   float   -0.265154809    0x0000AA8E@Data 
        [250]   float   -0.259191304    0x0000AA90@Data 
        [251]   float   -0.253358126    0x0000AA92@Data 
        [252]   float   -0.247455806    0x0000AA94@Data 
        [253]   float   -0.241571799    0x0000AA96@Data 
        [254]   float   -0.235672742    0x0000AA98@Data 
        [255]   float   -0.229751527    0x0000AA9A@Data 
        [256]   float   -0.223844528    0x0000AA9C@Data 
        [257]   float   -0.217971742    0x0000AA9E@Data 
        [258]   float   -0.212110996    0x0000AAA0@Data 
        [259]   float   -0.206192434    0x0000AAA2@Data 
        [260]   float   -0.200315416    0x0000AAA4@Data 
        [261]   float   -0.194414511    0x0000AAA6@Data 
        [262]   float   -0.188522264    0x0000AAA8@Data 
        [263]   float   -0.182624772    0x0000AAAA@Data 
        [264]   float   -0.176756084    0x0000AAAC@Data 
        [265]   float   -0.170833394    0x0000AAAE@Data 
        [266]   float   -0.164979443    0x0000AAB0@Data 
        [267]   float   -0.159066692    0x0000AAB2@Data 
        [268]   float   -0.153162345    0x0000AAB4@Data 
        [269]   float   -0.147283673    0x0000AAB6@Data 
        [270]   float   -0.141336769    0x0000AAB8@Data 
        [271]   float   -0.135496289    0x0000AABA@Data 
        [272]   float   -0.129614547    0x0000AABC@Data 
        [273]   float   -0.123702779    0x0000AABE@Data 
        [274]   float   -0.117813796    0x0000AAC0@Data 
        [275]   float   -0.111933798    0x0000AAC2@Data 
        [276]   float   -0.106044225    0x0000AAC4@Data 
        [277]   float   -0.100165963    0x0000AAC6@Data 
        [278]   float   -0.0942676589   0x0000AAC8@Data 
        [279]   float   -0.0883318037   0x0000AACA@Data 
        [280]   float   -0.0824574754   0x0000AACC@Data 
        [281]   float   -0.076660879    0x0000AACE@Data 
        [282]   float   -0.070723258    0x0000AAD0@Data 
        [283]   float   -0.0647760406   0x0000AAD2@Data 
        [284]   float   -0.0588856116   0x0000AAD4@Data 
        [285]   float   -0.0530399121   0x0000AAD6@Data 
        [286]   float   -0.047145471    0x0000AAD8@Data 
        [287]   float   -0.0412267074   0x0000AADA@Data 
        [288]   float   -0.0353087038   0x0000AADC@Data 
        [289]   float   -0.0295187682   0x0000AADE@Data 
        [290]   float   -0.0235772878   0x0000AAE0@Data 
        [291]   float   -0.0177018438   0x0000AAE2@Data 
        [292]   float   -0.0118004028   0x0000AAE4@Data 
        [293]   float   -0.00580472359  0x0000AAE6@Data 

        [0] float   5.92992067  0x0000AAF4@Data 
        [1] float   5.91866446  0x0000AAF6@Data 
        [2] float   5.91006184  0x0000AAF8@Data 
        [3] float   5.90019274  0x0000AAFA@Data 
        [4] float   5.89218664  0x0000AAFC@Data 
        [5] float   5.88362122  0x0000AAFE@Data 
        [6] float   5.87293053  0x0000AB00@Data 
        [7] float   5.8630724   0x0000AB02@Data 
        [8] float   5.85494614  0x0000AB04@Data 
        [9] float   5.84541845  0x0000AB06@Data 
        [10]    float   5.83665228  0x0000AB08@Data 
        [11]    float   5.8273654   0x0000AB0A@Data 
        [12]    float   5.81873178  0x0000AB0C@Data 
        [13]    float   5.80802965  0x0000AB0E@Data 
        [14]    float   5.79664373  0x0000AB10@Data 
        [15]    float   5.7884388   0x0000AB12@Data 
        [16]    float   5.77995777  0x0000AB14@Data 
        [17]    float   5.7697072   0x0000AB16@Data 
        [18]    float   5.75875235  0x0000AB18@Data 
        [19]    float   5.75014544  0x0000AB1A@Data 
        [20]    float   5.7393918   0x0000AB1C@Data 
        [21]    float   5.73293018  0x0000AB1E@Data 
        [22]    float   5.7225318   0x0000AB20@Data 
        [23]    float   5.7118392   0x0000AB22@Data 
        [24]    float   5.70227385  0x0000AB24@Data 
        [25]    float   5.69212627  0x0000AB26@Data 
        [26]    float   5.68220234  0x0000AB28@Data 
        [27]    float   5.67192554  0x0000AB2A@Data 
        [28]    float   5.66289282  0x0000AB2C@Data 
        [29]    float   5.65230083  0x0000AB2E@Data 
        [30]    float   5.64232111  0x0000AB30@Data 
        [31]    float   5.63330269  0x0000AB32@Data 
        [32]    float   5.6244936   0x0000AB34@Data 
        [33]    float   5.61259174  0x0000AB36@Data 
        [34]    float   5.6032896   0x0000AB38@Data 
        [35]    float   5.59213018  0x0000AB3A@Data 
        [36]    float   5.58163452  0x0000AB3C@Data 
        [37]    float   5.57239199  0x0000AB3E@Data 
        [38]    float   5.56303453  0x0000AB40@Data 
        [39]    float   5.55117083  0x0000AB42@Data 
        [40]    float   5.54258251  0x0000AB44@Data 
        [41]    float   5.53277397  0x0000AB46@Data 
        [42]    float   5.52136898  0x0000AB48@Data 
        [43]    float   5.51138449  0x0000AB4A@Data 
        [44]    float   5.50295591  0x0000AB4C@Data 
        [45]    float   5.49322796  0x0000AB4E@Data 
        [46]    float   5.47904491  0x0000AB50@Data 
        [47]    float   5.47322559  0x0000AB52@Data 
        [48]    float   5.4646306   0x0000AB54@Data 
        [49]    float   5.45636749  0x0000AB56@Data 
        [50]    float   5.44469166  0x0000AB58@Data 
        [51]    float   5.43232727  0x0000AB5A@Data 
        [52]    float   5.42131853  0x0000AB5C@Data 
        [53]    float   5.4113884   0x0000AB5E@Data 
        [54]    float   5.40052509  0x0000AB60@Data 
        [55]    float   5.39011908  0x0000AB62@Data 
        [56]    float   5.37748575  0x0000AB64@Data 
        [57]    float   5.36809683  0x0000AB66@Data 
        [58]    float   5.35781479  0x0000AB68@Data 
        [59]    float   5.34487391  0x0000AB6A@Data 
        [60]    float   5.33454418  0x0000AB6C@Data 
        [61]    float   5.32813597  0x0000AB6E@Data 
        [62]    float   5.31772041  0x0000AB70@Data 
        [63]    float   5.3054285   0x0000AB72@Data 
        [64]    float   5.29412699  0x0000AB74@Data 
        [65]    float   5.28332424  0x0000AB76@Data 
        [66]    float   5.2718873   0x0000AB78@Data 
        [67]    float   5.26046991  0x0000AB7A@Data 
        [68]    float   5.24987364  0x0000AB7C@Data 
        [69]    float   5.23766518  0x0000AB7E@Data 
        [70]    float   5.22540951  0x0000AB80@Data 
        [71]    float   5.21502829  0x0000AB82@Data 
        [72]    float   5.20206642  0x0000AB84@Data 
        [73]    float   5.18970633  0x0000AB86@Data 
        [74]    float   5.17948675  0x0000AB88@Data 
        [75]    float   5.16906643  0x0000AB8A@Data 
        [76]    float   5.15451384  0x0000AB8C@Data 
        [77]    float   5.14369202  0x0000AB8E@Data 
        [78]    float   5.13217688  0x0000AB90@Data 
        [79]    float   5.12138224  0x0000AB92@Data 
        [80]    float   5.10864258  0x0000AB94@Data 
        [81]    float   5.09755421  0x0000AB96@Data 
        [82]    float   5.08670139  0x0000AB98@Data 
        [83]    float   5.07533932  0x0000AB9A@Data 
        [84]    float   5.06220055  0x0000AB9C@Data 
        [85]    float   5.05051184  0x0000AB9E@Data 
        [86]    float   5.0323925   0x0000ABA0@Data 
        [87]    float   5.02009535  0x0000ABA2@Data 
        [88]    float   5.00589037  0x0000ABA4@Data 
        [89]    float   4.99266052  0x0000ABA6@Data 
        [90]    float   4.98074961  0x0000ABA8@Data 
        [91]    float   4.97208595  0x0000ABAA@Data 
        [92]    float   4.95418835  0x0000ABAC@Data 
        [93]    float   4.94484711  0x0000ABAE@Data 
        [94]    float   4.93286276  0x0000ABB0@Data 
        [95]    float   4.91407394  0x0000ABB2@Data 
        [96]    float   4.89981461  0x0000ABB4@Data 
        [97]    float   4.88066959  0x0000ABB6@Data 
        [98]    float   4.86627817  0x0000ABB8@Data 
        [99]    float   4.85396481  0x0000ABBA@Data 
        [100]   float   4.8445859   0x0000ABBC@Data 
        [101]   float   4.83590174  0x0000ABBE@Data 
        [102]   float   4.81760406  0x0000ABC0@Data 
        [103]   float   4.80109262  0x0000ABC2@Data 
        [104]   float   4.7834034   0x0000ABC4@Data 
        [105]   float   4.76695776  0x0000ABC6@Data 
        [106]   float   4.74921989  0x0000ABC8@Data 
        [107]   float   4.73093987  0x0000ABCA@Data 
        [108]   float   4.71105242  0x0000ABCC@Data 
        [109]   float   4.69296217  0x0000ABCE@Data 
        [110]   float   4.67336798  0x0000ABD0@Data 
        [111]   float   4.65337896  0x0000ABD2@Data 
        [112]   float   4.63305998  0x0000ABD4@Data 
        [113]   float   4.61081314  0x0000ABD6@Data 
        [114]   float   4.58835125  0x0000ABD8@Data 
        [115]   float   4.56612396  0x0000ABDA@Data 
        [116]   float   4.54176378  0x0000ABDC@Data 
        [117]   float   4.5160799   0x0000ABDE@Data 
        [118]   float   4.49006844  0x0000ABE0@Data 
        [119]   float   4.46408892  0x0000ABE2@Data 
        [120]   float   4.43635988  0x0000ABE4@Data 
        [121]   float   4.40816641  0x0000ABE6@Data 
        [122]   float   4.3743577   0x0000ABE8@Data 
        [123]   float   4.34195042  0x0000ABEA@Data 
        [124]   float   4.30485106  0x0000ABEC@Data 
        [125]   float   4.26854467  0x0000ABEE@Data 
        [126]   float   4.22855997  0x0000ABF0@Data 
        [127]   float   4.18507242  0x0000ABF2@Data 
        [128]   float   4.13825798  0x0000ABF4@Data 
        [129]   float   4.08585882  0x0000ABF6@Data 
        [130]   float   4.01747036  0x0000ABF8@Data 
        [131]   float   3.9518342   0x0000ABFA@Data 
        [132]   float   3.87490988  0x0000ABFC@Data 
        [133]   float   3.78743052  0x0000ABFE@Data 
        [134]   float   3.6795032   0x0000AC00@Data 
        [135]   float   3.56468153  0x0000AC02@Data 
        [136]   float   3.441401    0x0000AC04@Data 
        [137]   float   3.28855085  0x0000AC06@Data 
        [138]   float   3.05977392  0x0000AC08@Data 
        [139]   float   2.70512319  0x0000AC0A@Data 
        [140]   float   2.10457587  0x0000AC0C@Data 
        [141]   float   1.25320137  0x0000AC0E@Data 
        [142]   float   0.563560903 0x0000AC10@Data 
        [143]   float   -0.232684121    0x0000AC12@Data 
        [144]   float   -0.877381504    0x0000AC14@Data 
        [145]   float   -1.6001364  0x0000AC16@Data 
        [146]   float   -2.3848052  0x0000AC18@Data 
        [147]   float   -6.02172184 0x0000AC1A@Data 
        [148]   float   -6.01136446 0x0000AC1C@Data 
        [149]   float   -6.00309134 0x0000AC1E@Data 
        [150]   float   -5.99089432 0x0000AC20@Data 
        [151]   float   -5.98306513 0x0000AC22@Data 
        [152]   float   -5.97450113 0x0000AC24@Data 
        [153]   float   -5.96361303 0x0000AC26@Data 
        [154]   float   -5.9555769  0x0000AC28@Data 
        [155]   float   -5.94554901 0x0000AC2A@Data 
        [156]   float   -5.93653679 0x0000AC2C@Data 
        [157]   float   -5.92829037 0x0000AC2E@Data 
        [158]   float   -5.91899204 0x0000AC30@Data 
        [159]   float   -5.90928125 0x0000AC32@Data 
        [160]   float   -5.89950085 0x0000AC34@Data 
        [161]   float   -5.89001036 0x0000AC36@Data 
        [162]   float   -5.8812871  0x0000AC38@Data 
        [163]   float   -5.87093401 0x0000AC3A@Data 
        [164]   float   -5.85992479 0x0000AC3C@Data 
        [165]   float   -5.85257244 0x0000AC3E@Data 
        [166]   float   -5.84332848 0x0000AC40@Data 
        [167]   float   -5.83493328 0x0000AC42@Data 
        [168]   float   -5.82537794 0x0000AC44@Data 
        [169]   float   -5.81838274 0x0000AC46@Data 
        [170]   float   -5.80952168 0x0000AC48@Data 
        [171]   float   -5.79733324 0x0000AC4A@Data 
        [172]   float   -5.78962231 0x0000AC4C@Data 
        [173]   float   -5.77854156 0x0000AC4E@Data 
        [174]   float   -5.77110958 0x0000AC50@Data 
        [175]   float   -5.76089001 0x0000AC52@Data 
        [176]   float   -5.7509408  0x0000AC54@Data 
        [177]   float   -5.74085236 0x0000AC56@Data 
        [178]   float   -5.73092604 0x0000AC58@Data 
        [179]   float   -5.72010756 0x0000AC5A@Data 
        [180]   float   -5.7136178  0x0000AC5C@Data 
        [181]   float   -5.70110607 0x0000AC5E@Data 
        [182]   float   -5.69292974 0x0000AC60@Data 
        [183]   float   -5.68302107 0x0000AC62@Data 
        [184]   float   -5.67344904 0x0000AC64@Data 
        [185]   float   -5.66431522 0x0000AC66@Data 
        [186]   float   -5.65729523 0x0000AC68@Data 
        [187]   float   -5.64803219 0x0000AC6A@Data 
        [188]   float   -5.63753128 0x0000AC6C@Data 
        [189]   float   -5.6275053  0x0000AC6E@Data 
        [190]   float   -5.61847305 0x0000AC70@Data 
        [191]   float   -5.60687971 0x0000AC72@Data 
        [192]   float   -5.59741831 0x0000AC74@Data 
        [193]   float   -5.58612919 0x0000AC76@Data 
        [194]   float   -5.57549858 0x0000AC78@Data 
        [195]   float   -5.56789732 0x0000AC7A@Data 
        [196]   float   -5.55788374 0x0000AC7C@Data 
        [197]   float   -5.54605627 0x0000AC7E@Data 
        [198]   float   -5.53692245 0x0000AC80@Data 
        [199]   float   -5.52660131 0x0000AC82@Data 
        [200]   float   -5.51651907 0x0000AC84@Data 
        [201]   float   -5.50623178 0x0000AC86@Data 
        [202]   float   -5.49624109 0x0000AC88@Data 
        [203]   float   -5.485147   0x0000AC8A@Data 
        [204]   float   -5.47501183 0x0000AC8C@Data 
        [205]   float   -5.46328545 0x0000AC8E@Data 
        [206]   float   -5.45254183 0x0000AC90@Data 
        [207]   float   -5.44477701 0x0000AC92@Data 
        [208]   float   -5.4340167  0x0000AC94@Data 
        [209]   float   -5.42170048 0x0000AC96@Data 
        [210]   float   -5.41080379 0x0000AC98@Data 
        [211]   float   -5.39967155 0x0000AC9A@Data 
        [212]   float   -5.3899231  0x0000AC9C@Data 
        [213]   float   -5.37808514 0x0000AC9E@Data 
        [214]   float   -5.36787987 0x0000ACA0@Data 
        [215]   float   -5.35850477 0x0000ACA2@Data 
        [216]   float   -5.34721613 0x0000ACA4@Data 
        [217]   float   -5.33521509 0x0000ACA6@Data 
        [218]   float   -5.32282257 0x0000ACA8@Data 
        [219]   float   -5.31297684 0x0000ACAA@Data 
        [220]   float   -5.30264711 0x0000ACAC@Data 
        [221]   float   -5.29186058 0x0000ACAE@Data 
        [222]   float   -5.28142786 0x0000ACB0@Data 
        [223]   float   -5.26961184 0x0000ACB2@Data 
        [224]   float   -5.26108456 0x0000ACB4@Data 
        [225]   float   -5.24903965 0x0000ACB6@Data 
        [226]   float   -5.23651075 0x0000ACB8@Data 
        [227]   float   -5.22406387 0x0000ACBA@Data 
        [228]   float   -5.20979643 0x0000ACBC@Data 
        [229]   float   -5.19997168 0x0000ACBE@Data 
        [230]   float   -5.1882329  0x0000ACC0@Data 
        [231]   float   -5.17625809 0x0000ACC2@Data 
        [232]   float   -5.16158962 0x0000ACC4@Data 
        [233]   float   -5.14840126 0x0000ACC6@Data 
        [234]   float   -5.13927889 0x0000ACC8@Data 
        [235]   float   -5.13136959 0x0000ACCA@Data 
        [236]   float   -5.11481094 0x0000ACCC@Data 
        [237]   float   -5.10613918 0x0000ACCE@Data 
        [238]   float   -5.09396029 0x0000ACD0@Data 
        [239]   float   -5.07759237 0x0000ACD2@Data 
        [240]   float   -5.06652117 0x0000ACD4@Data 
        [241]   float   -5.05575037 0x0000ACD6@Data 
        [242]   float   -5.03821468 0x0000ACD8@Data 
        [243]   float   -5.02769613 0x0000ACDA@Data 
        [244]   float   -5.01593161 0x0000ACDC@Data 
        [245]   float   -5.00187397 0x0000ACDE@Data 
        [246]   float   -4.9867239  0x0000ACE0@Data 
        [247]   float   -4.9731946  0x0000ACE2@Data 
        [248]   float   -4.96112251 0x0000ACE4@Data 
        [249]   float   -4.94452286 0x0000ACE6@Data 
        [250]   float   -4.93108988 0x0000ACE8@Data 
        [251]   float   -4.91571093 0x0000ACEA@Data 
        [252]   float   -4.89764166 0x0000ACEC@Data 
        [253]   float   -4.88364983 0x0000ACEE@Data 
        [254]   float   -4.86943626 0x0000ACF0@Data 
        [255]   float   -4.85259581 0x0000ACF2@Data 
        [256]   float   -4.83773279 0x0000ACF4@Data 
        [257]   float   -4.82245827 0x0000ACF6@Data 
        [258]   float   -4.80447149 0x0000ACF8@Data 
        [259]   float   -4.78616667 0x0000ACFA@Data 
        [260]   float   -4.77194595 0x0000ACFC@Data 
        [261]   float   -4.75696182 0x0000ACFE@Data 
        [262]   float   -4.74021482 0x0000AD00@Data 
        [263]   float   -4.725667   0x0000AD02@Data 
        [264]   float   -4.70963478 0x0000AD04@Data 
        [265]   float   -4.69183779 0x0000AD06@Data 
        [266]   float   -4.67109823 0x0000AD08@Data 
        [267]   float   -4.6520977  0x0000AD0A@Data 
        [268]   float   -4.63173342 0x0000AD0C@Data 
        [269]   float   -4.60824251 0x0000AD0E@Data 
        [270]   float   -4.58578348 0x0000AD10@Data 
        [271]   float   -4.56532001 0x0000AD12@Data 
        [272]   float   -4.53728199 0x0000AD14@Data 
        [273]   float   -4.51299191 0x0000AD16@Data 
        [274]   float   -4.48875237 0x0000AD18@Data 
        [275]   float   -4.45950317 0x0000AD1A@Data 
        [276]   float   -4.43132257 0x0000AD1C@Data 
        [277]   float   -4.40324116 0x0000AD1E@Data 
        [278]   float   -4.36883783 0x0000AD20@Data 
        [279]   float   -4.33383942 0x0000AD22@Data 
        [280]   float   -4.29820776 0x0000AD24@Data 
        [281]   float   -4.25666571 0x0000AD26@Data 
        [282]   float   -4.21294165 0x0000AD28@Data 
        [283]   float   -4.16904402 0x0000AD2A@Data 
        [284]   float   -4.11754942 0x0000AD2C@Data 
        [285]   float   -4.05849981 0x0000AD2E@Data 
        [286]   float   -3.99171638 0x0000AD30@Data 
        [287]   float   -3.92622542 0x0000AD32@Data 
        [288]   float   -3.83736086 0x0000AD34@Data 
        [289]   float   -3.7439847  0x0000AD36@Data 
        [290]   float   -3.64928699 0x0000AD38@Data 
        [291]   float   -3.54741406 0x0000AD3A@Data 
        [292]   float   -3.40504026 0x0000AD3C@Data 
        [293]   float   -3.17164207 0x0000AD3E@Data 
    '''

    tag = 'Mini6PhaseIPMInverter-528-0927-phaseB-80V[294-Points]-1A-[ADC offset-compensated]'
    ccs_expressions[tag] = '''
        [0] float   0.86600697  0x0000A89C@Data 
        [1] float   0.860197544 0x0000A89E@Data 
        [2] float   0.854231298 0x0000A8A0@Data 
        [3] float   0.848360002 0x0000A8A2@Data 
        [4] float   0.842451751 0x0000A8A4@Data 
        [5] float   0.836556792 0x0000A8A6@Data 
        [6] float   0.830727041 0x0000A8A8@Data 
        [7] float   0.824801445 0x0000A8AA@Data 
        [8] float   0.818903387 0x0000A8AC@Data 
        [9] float   0.813013494 0x0000A8AE@Data 
        [10]    float   0.807167947 0x0000A8B0@Data 
        [11]    float   0.801200807 0x0000A8B2@Data 
        [12]    float   0.795315385 0x0000A8B4@Data 
        [13]    float   0.789418697 0x0000A8B6@Data 
        [14]    float   0.783558547 0x0000A8B8@Data 
        [15]    float   0.777629197 0x0000A8BA@Data 
        [16]    float   0.77172941  0x0000A8BC@Data 
        [17]    float   0.765884936 0x0000A8BE@Data 
        [18]    float   0.760014534 0x0000A8C0@Data 
        [19]    float   0.754084527 0x0000A8C2@Data 
        [20]    float   0.748221457 0x0000A8C4@Data 
        [21]    float   0.742308438 0x0000A8C6@Data 
        [22]    float   0.736452758 0x0000A8C8@Data 
        [23]    float   0.730553687 0x0000A8CA@Data 
        [24]    float   0.7246539   0x0000A8CC@Data 
        [25]    float   0.718754768 0x0000A8CE@Data 
        [26]    float   0.712851048 0x0000A8D0@Data 
        [27]    float   0.70698911  0x0000A8D2@Data 
        [28]    float   0.701073527 0x0000A8D4@Data 
        [29]    float   0.695175588 0x0000A8D6@Data 
        [30]    float   0.689302623 0x0000A8D8@Data 
        [31]    float   0.683419645 0x0000A8DA@Data 
        [32]    float   0.677476883 0x0000A8DC@Data 
        [33]    float   0.671612918 0x0000A8DE@Data 
        [34]    float   0.665699661 0x0000A8E0@Data 
        [35]    float   0.659845114 0x0000A8E2@Data 
        [36]    float   0.653944731 0x0000A8E4@Data 
        [37]    float   0.648046851 0x0000A8E6@Data 
        [38]    float   0.642163336 0x0000A8E8@Data 
        [39]    float   0.636274993 0x0000A8EA@Data 
        [40]    float   0.630371034 0x0000A8EC@Data 
        [41]    float   0.624517083 0x0000A8EE@Data 
        [42]    float   0.618621409 0x0000A8F0@Data 
        [43]    float   0.612675726 0x0000A8F2@Data 
        [44]    float   0.606782913 0x0000A8F4@Data 
        [45]    float   0.600878596 0x0000A8F6@Data 
        [46]    float   0.595063806 0x0000A8F8@Data 
        [47]    float   0.589144409 0x0000A8FA@Data 
        [48]    float   0.583245575 0x0000A8FC@Data 
        [49]    float   0.577322185 0x0000A8FE@Data 
        [50]    float   0.571449816 0x0000A900@Data 
        [51]    float   0.565598428 0x0000A902@Data 
        [52]    float   0.559666514 0x0000A904@Data 
        [53]    float   0.553792179 0x0000A906@Data 
        [54]    float   0.547919989 0x0000A908@Data 
        [55]    float   0.542019129 0x0000A90A@Data 
        [56]    float   0.536109447 0x0000A90C@Data 
        [57]    float   0.530223191 0x0000A90E@Data 
        [58]    float   0.524289787 0x0000A910@Data 
        [59]    float   0.518462896 0x0000A912@Data 
        [60]    float   0.512558401 0x0000A914@Data 
        [61]    float   0.506663859 0x0000A916@Data 
        [62]    float   0.500809073 0x0000A918@Data 
        [63]    float   0.494880289 0x0000A91A@Data 
        [64]    float   0.489000767 0x0000A91C@Data 
        [65]    float   0.483099163 0x0000A91E@Data 
        [66]    float   0.477211326 0x0000A920@Data 
        [67]    float   0.471311241 0x0000A922@Data 
        [68]    float   0.46538645  0x0000A924@Data 
        [69]    float   0.459516436 0x0000A926@Data 
        [70]    float   0.453632981 0x0000A928@Data 
        [71]    float   0.447743446 0x0000A92A@Data 
        [72]    float   0.441851795 0x0000A92C@Data 
        [73]    float   0.435962051 0x0000A92E@Data 
        [74]    float   0.430069417 0x0000A930@Data 
        [75]    float   0.424164146 0x0000A932@Data 
        [76]    float   0.418282717 0x0000A934@Data 
        [77]    float   0.412412107 0x0000A936@Data 
        [78]    float   0.40654102  0x0000A938@Data 
        [79]    float   0.40060702  0x0000A93A@Data 
        [80]    float   0.394710302 0x0000A93C@Data 
        [81]    float   0.388824075 0x0000A93E@Data 
        [82]    float   0.382949829 0x0000A940@Data 
        [83]    float   0.37706089  0x0000A942@Data 
        [84]    float   0.371149093 0x0000A944@Data 
        [85]    float   0.365253061 0x0000A946@Data 
        [86]    float   0.359360695 0x0000A948@Data 
        [87]    float   0.353486717 0x0000A94A@Data 
        [88]    float   0.347574741 0x0000A94C@Data 
        [89]    float   0.341671497 0x0000A94E@Data 
        [90]    float   0.335793793 0x0000A950@Data 
        [91]    float   0.329915076 0x0000A952@Data 
        [92]    float   0.324048966 0x0000A954@Data 
        [93]    float   0.31814304  0x0000A956@Data 
        [94]    float   0.312208712 0x0000A958@Data 
        [95]    float   0.306390375 0x0000A95A@Data 
        [96]    float   0.30045718  0x0000A95C@Data 
        [97]    float   0.294562727 0x0000A95E@Data 
        [98]    float   0.288656801 0x0000A960@Data 
        [99]    float   0.282776684 0x0000A962@Data 
        [100]   float   0.276923835 0x0000A964@Data 
        [101]   float   0.271027386 0x0000A966@Data 
        [102]   float   0.265150338 0x0000A968@Data 
        [103]   float   0.259218663 0x0000A96A@Data 
        [104]   float   0.253314078 0x0000A96C@Data 
        [105]   float   0.247413516 0x0000A96E@Data 
        [106]   float   0.241553813 0x0000A970@Data 
        [107]   float   0.235636741 0x0000A972@Data 
        [108]   float   0.229754791 0x0000A974@Data 
        [109]   float   0.223856553 0x0000A976@Data 
        [110]   float   0.217992365 0x0000A978@Data 
        [111]   float   0.212050587 0x0000A97A@Data 
        [112]   float   0.206167161 0x0000A97C@Data 
        [113]   float   0.200307727 0x0000A97E@Data 
        [114]   float   0.194442675 0x0000A980@Data 
        [115]   float   0.188541308 0x0000A982@Data 
        [116]   float   0.182645917 0x0000A984@Data 
        [117]   float   0.176746562 0x0000A986@Data 
        [118]   float   0.170858234 0x0000A988@Data 
        [119]   float   0.164936662 0x0000A98A@Data 
        [120]   float   0.159061998 0x0000A98C@Data 
        [121]   float   0.153167218 0x0000A98E@Data 
        [122]   float   0.147299901 0x0000A990@Data 
        [123]   float   0.141395569 0x0000A992@Data 
        [124]   float   0.135500759 0x0000A994@Data 
        [125]   float   0.129664779 0x0000A996@Data 
        [126]   float   0.123686455 0x0000A998@Data 
        [127]   float   0.117811725 0x0000A99A@Data 
        [128]   float   0.111945078 0x0000A99C@Data 
        [129]   float   0.105981827 0x0000A99E@Data 
        [130]   float   0.100143343 0x0000A9A0@Data 
        [131]   float   0.094244808 0x0000A9A2@Data 
        [132]   float   0.0883650705    0x0000A9A4@Data 
        [133]   float   0.0825411752    0x0000A9A6@Data 
        [134]   float   0.076566495 0x0000A9A8@Data 
        [135]   float   0.0707654878    0x0000A9AA@Data 
        [136]   float   0.0647584274    0x0000A9AC@Data 
        [137]   float   0.0589883141    0x0000A9AE@Data 
        [138]   float   0.053028062 0x0000A9B0@Data 
        [139]   float   0.0472641177    0x0000A9B2@Data 
        [140]   float   0.0413398258    0x0000A9B4@Data 
        [141]   float   0.0356914662    0x0000A9B6@Data 
        [142]   float   0.0298973061    0x0000A9B8@Data 
        [143]   float   0.0238785371    0x0000A9BA@Data 
        [144]   float   0.0178308953    0x0000A9BC@Data 
        [145]   float   0.0118945874    0x0000A9BE@Data 
        [146]   float   0.00604146719   0x0000A9C0@Data 
        [147]   float   -0.866025805    0x0000A9C2@Data 
        [148]   float   -0.860146463    0x0000A9C4@Data 
        [149]   float   -0.854252756    0x0000A9C6@Data 
        [150]   float   -0.848372102    0x0000A9C8@Data 
        [151]   float   -0.842422366    0x0000A9CA@Data 
        [152]   float   -0.836532414    0x0000A9CC@Data 
        [153]   float   -0.830651164    0x0000A9CE@Data 
        [154]   float   -0.824804902    0x0000A9D0@Data 
        [155]   float   -0.818862379    0x0000A9D2@Data 
        [156]   float   -0.813012481    0x0000A9D4@Data 
        [157]   float   -0.807098806    0x0000A9D6@Data 
        [158]   float   -0.801217258    0x0000A9D8@Data 
        [159]   float   -0.795300782    0x0000A9DA@Data 
        [160]   float   -0.78942287 0x0000A9DC@Data 
        [161]   float   -0.783519089    0x0000A9DE@Data 
        [162]   float   -0.777681291    0x0000A9E0@Data 
        [163]   float   -0.771733463    0x0000A9E2@Data 
        [164]   float   -0.765917242    0x0000A9E4@Data 
        [165]   float   -0.759959757    0x0000A9E6@Data 
        [166]   float   -0.754081905    0x0000A9E8@Data 
        [167]   float   -0.74819988 0x0000A9EA@Data 
        [168]   float   -0.742320359    0x0000A9EC@Data 
        [169]   float   -0.736393869    0x0000A9EE@Data 
        [170]   float   -0.730540454    0x0000A9F0@Data 
        [171]   float   -0.724613309    0x0000A9F2@Data 
        [172]   float   -0.718766391    0x0000A9F4@Data 
        [173]   float   -0.712851822    0x0000A9F6@Data 
        [174]   float   -0.70696497 0x0000A9F8@Data 
        [175]   float   -0.701045752    0x0000A9FA@Data 
        [176]   float   -0.695153892    0x0000A9FC@Data 
        [177]   float   -0.6893242  0x0000A9FE@Data 
        [178]   float   -0.683337033    0x0000AA00@Data 
        [179]   float   -0.67751044 0x0000AA02@Data 
        [180]   float   -0.671573997    0x0000AA04@Data 
        [181]   float   -0.665718734    0x0000AA06@Data 
        [182]   float   -0.659826338    0x0000AA08@Data 
        [183]   float   -0.653955936    0x0000AA0A@Data 
        [184]   float   -0.648063302    0x0000AA0C@Data 
        [185]   float   -0.642120183    0x0000AA0E@Data 
        [186]   float   -0.636262357    0x0000AA10@Data 
        [187]   float   -0.630370796    0x0000AA12@Data 
        [188]   float   -0.624466598    0x0000AA14@Data 
        [189]   float   -0.618578494    0x0000AA16@Data 
        [190]   float   -0.612736106    0x0000AA18@Data 
        [191]   float   -0.606793344    0x0000AA1A@Data 
        [192]   float   -0.600890577    0x0000AA1C@Data 
        [193]   float   -0.595032692    0x0000AA1E@Data 
        [194]   float   -0.58912164 0x0000AA20@Data 
        [195]   float   -0.583250463    0x0000AA22@Data 
        [196]   float   -0.577315092    0x0000AA24@Data 
        [197]   float   -0.571417511    0x0000AA26@Data 
        [198]   float   -0.565543234    0x0000AA28@Data 
        [199]   float   -0.559683859    0x0000AA2A@Data 
        [200]   float   -0.553759634    0x0000AA2C@Data 
        [201]   float   -0.547907412    0x0000AA2E@Data 
        [202]   float   -0.542013824    0x0000AA30@Data 
        [203]   float   -0.536075234    0x0000AA32@Data 
        [204]   float   -0.530237377    0x0000AA34@Data 
        [205]   float   -0.524331152    0x0000AA36@Data 
        [206]   float   -0.518415272    0x0000AA38@Data 
        [207]   float   -0.51250875 0x0000AA3A@Data 
        [208]   float   -0.506633818    0x0000AA3C@Data 
        [209]   float   -0.500779212    0x0000AA3E@Data 
        [210]   float   -0.494909137    0x0000AA40@Data 
        [211]   float   -0.488972694    0x0000AA42@Data 
        [212]   float   -0.483123422    0x0000AA44@Data 
        [213]   float   -0.477206379    0x0000AA46@Data 
        [214]   float   -0.471329719    0x0000AA48@Data 
        [215]   float   -0.46542874 0x0000AA4A@Data 
        [216]   float   -0.459519744    0x0000AA4C@Data 
        [217]   float   -0.453638405    0x0000AA4E@Data 
        [218]   float   -0.447747111    0x0000AA50@Data 
        [219]   float   -0.441863716    0x0000AA52@Data 
        [220]   float   -0.435927838    0x0000AA54@Data 
        [221]   float   -0.430050194    0x0000AA56@Data 
        [222]   float   -0.424152851    0x0000AA58@Data 
        [223]   float   -0.418320447    0x0000AA5A@Data 
        [224]   float   -0.412322998    0x0000AA5C@Data 
        [225]   float   -0.40646705 0x0000AA5E@Data 
        [226]   float   -0.400580466    0x0000AA60@Data 
        [227]   float   -0.394747227    0x0000AA62@Data 
        [228]   float   -0.388823837    0x0000AA64@Data 
        [229]   float   -0.382930607    0x0000AA66@Data 
        [230]   float   -0.377038956    0x0000AA68@Data 
        [231]   float   -0.371166945    0x0000AA6A@Data 
        [232]   float   -0.365302831    0x0000AA6C@Data 
        [233]   float   -0.359397501    0x0000AA6E@Data 
        [234]   float   -0.353496641    0x0000AA70@Data 
        [235]   float   -0.347564399    0x0000AA72@Data 
        [236]   float   -0.341719717    0x0000AA74@Data 
        [237]   float   -0.335776091    0x0000AA76@Data 
        [238]   float   -0.329871953    0x0000AA78@Data 
        [239]   float   -0.324028641    0x0000AA7A@Data 
        [240]   float   -0.318119735    0x0000AA7C@Data 
        [241]   float   -0.312205762    0x0000AA7E@Data 
        [242]   float   -0.30634734 0x0000AA80@Data 
        [243]   float   -0.300485939    0x0000AA82@Data 
        [244]   float   -0.294569463    0x0000AA84@Data 
        [245]   float   -0.288667142    0x0000AA86@Data 
        [246]   float   -0.282817423    0x0000AA88@Data 
        [247]   float   -0.276864409    0x0000AA8A@Data 
        [248]   float   -0.270992845    0x0000AA8C@Data 
        [249]   float   -0.265154809    0x0000AA8E@Data 
        [250]   float   -0.259191304    0x0000AA90@Data 
        [251]   float   -0.253358126    0x0000AA92@Data 
        [252]   float   -0.247455806    0x0000AA94@Data 
        [253]   float   -0.241571799    0x0000AA96@Data 
        [254]   float   -0.235672742    0x0000AA98@Data 
        [255]   float   -0.229751527    0x0000AA9A@Data 
        [256]   float   -0.223844528    0x0000AA9C@Data 
        [257]   float   -0.217971742    0x0000AA9E@Data 
        [258]   float   -0.212110996    0x0000AAA0@Data 
        [259]   float   -0.206192434    0x0000AAA2@Data 
        [260]   float   -0.200315416    0x0000AAA4@Data 
        [261]   float   -0.194414511    0x0000AAA6@Data 
        [262]   float   -0.188522264    0x0000AAA8@Data 
        [263]   float   -0.182624772    0x0000AAAA@Data 
        [264]   float   -0.176756084    0x0000AAAC@Data 
        [265]   float   -0.170833394    0x0000AAAE@Data 
        [266]   float   -0.164979443    0x0000AAB0@Data 
        [267]   float   -0.159066692    0x0000AAB2@Data 
        [268]   float   -0.153162345    0x0000AAB4@Data 
        [269]   float   -0.147283673    0x0000AAB6@Data 
        [270]   float   -0.141336769    0x0000AAB8@Data 
        [271]   float   -0.135496289    0x0000AABA@Data 
        [272]   float   -0.129614547    0x0000AABC@Data 
        [273]   float   -0.123702779    0x0000AABE@Data 
        [274]   float   -0.117813796    0x0000AAC0@Data 
        [275]   float   -0.111933798    0x0000AAC2@Data 
        [276]   float   -0.106044225    0x0000AAC4@Data 
        [277]   float   -0.100165963    0x0000AAC6@Data 
        [278]   float   -0.0942676589   0x0000AAC8@Data 
        [279]   float   -0.0883318037   0x0000AACA@Data 
        [280]   float   -0.0824574754   0x0000AACC@Data 
        [281]   float   -0.076660879    0x0000AACE@Data 
        [282]   float   -0.070723258    0x0000AAD0@Data 
        [283]   float   -0.0647760406   0x0000AAD2@Data 
        [284]   float   -0.0588856116   0x0000AAD4@Data 
        [285]   float   -0.0530399121   0x0000AAD6@Data 
        [286]   float   -0.047145471    0x0000AAD8@Data 
        [287]   float   -0.0412267074   0x0000AADA@Data 
        [288]   float   -0.0353087038   0x0000AADC@Data 
        [289]   float   -0.0295187682   0x0000AADE@Data 
        [290]   float   -0.0235772878   0x0000AAE0@Data 
        [291]   float   -0.0177018438   0x0000AAE2@Data 
        [292]   float   -0.0118004028   0x0000AAE4@Data 
        [293]   float   -0.00580472359  0x0000AAE6@Data 

        [0] float   5.92992067  0x0000AAF4@Data 
        [1] float   5.91866446  0x0000AAF6@Data 
        [2] float   5.91006184  0x0000AAF8@Data 
        [3] float   5.90019274  0x0000AAFA@Data 
        [4] float   5.89218664  0x0000AAFC@Data 
        [5] float   5.88362122  0x0000AAFE@Data 
        [6] float   5.87293053  0x0000AB00@Data 
        [7] float   5.8630724   0x0000AB02@Data 
        [8] float   5.85494614  0x0000AB04@Data 
        [9] float   5.84541845  0x0000AB06@Data 
        [10]    float   5.83665228  0x0000AB08@Data 
        [11]    float   5.8273654   0x0000AB0A@Data 
        [12]    float   5.81873178  0x0000AB0C@Data 
        [13]    float   5.80802965  0x0000AB0E@Data 
        [14]    float   5.79664373  0x0000AB10@Data 
        [15]    float   5.7884388   0x0000AB12@Data 
        [16]    float   5.77995777  0x0000AB14@Data 
        [17]    float   5.7697072   0x0000AB16@Data 
        [18]    float   5.75875235  0x0000AB18@Data 
        [19]    float   5.75014544  0x0000AB1A@Data 
        [20]    float   5.7393918   0x0000AB1C@Data 
        [21]    float   5.73293018  0x0000AB1E@Data 
        [22]    float   5.7225318   0x0000AB20@Data 
        [23]    float   5.7118392   0x0000AB22@Data 
        [24]    float   5.70227385  0x0000AB24@Data 
        [25]    float   5.69212627  0x0000AB26@Data 
        [26]    float   5.68220234  0x0000AB28@Data 
        [27]    float   5.67192554  0x0000AB2A@Data 
        [28]    float   5.66289282  0x0000AB2C@Data 
        [29]    float   5.65230083  0x0000AB2E@Data 
        [30]    float   5.64232111  0x0000AB30@Data 
        [31]    float   5.63330269  0x0000AB32@Data 
        [32]    float   5.6244936   0x0000AB34@Data 
        [33]    float   5.61259174  0x0000AB36@Data 
        [34]    float   5.6032896   0x0000AB38@Data 
        [35]    float   5.59213018  0x0000AB3A@Data 
        [36]    float   5.58163452  0x0000AB3C@Data 
        [37]    float   5.57239199  0x0000AB3E@Data 
        [38]    float   5.56303453  0x0000AB40@Data 
        [39]    float   5.55117083  0x0000AB42@Data 
        [40]    float   5.54258251  0x0000AB44@Data 
        [41]    float   5.53277397  0x0000AB46@Data 
        [42]    float   5.52136898  0x0000AB48@Data 
        [43]    float   5.51138449  0x0000AB4A@Data 
        [44]    float   5.50295591  0x0000AB4C@Data 
        [45]    float   5.49322796  0x0000AB4E@Data 
        [46]    float   5.47904491  0x0000AB50@Data 
        [47]    float   5.47322559  0x0000AB52@Data 
        [48]    float   5.4646306   0x0000AB54@Data 
        [49]    float   5.45636749  0x0000AB56@Data 
        [50]    float   5.44469166  0x0000AB58@Data 
        [51]    float   5.43232727  0x0000AB5A@Data 
        [52]    float   5.42131853  0x0000AB5C@Data 
        [53]    float   5.4113884   0x0000AB5E@Data 
        [54]    float   5.40052509  0x0000AB60@Data 
        [55]    float   5.39011908  0x0000AB62@Data 
        [56]    float   5.37748575  0x0000AB64@Data 
        [57]    float   5.36809683  0x0000AB66@Data 
        [58]    float   5.35781479  0x0000AB68@Data 
        [59]    float   5.34487391  0x0000AB6A@Data 
        [60]    float   5.33454418  0x0000AB6C@Data 
        [61]    float   5.32813597  0x0000AB6E@Data 
        [62]    float   5.31772041  0x0000AB70@Data 
        [63]    float   5.3054285   0x0000AB72@Data 
        [64]    float   5.29412699  0x0000AB74@Data 
        [65]    float   5.28332424  0x0000AB76@Data 
        [66]    float   5.2718873   0x0000AB78@Data 
        [67]    float   5.26046991  0x0000AB7A@Data 
        [68]    float   5.24987364  0x0000AB7C@Data 
        [69]    float   5.23766518  0x0000AB7E@Data 
        [70]    float   5.22540951  0x0000AB80@Data 
        [71]    float   5.21502829  0x0000AB82@Data 
        [72]    float   5.20206642  0x0000AB84@Data 
        [73]    float   5.18970633  0x0000AB86@Data 
        [74]    float   5.17948675  0x0000AB88@Data 
        [75]    float   5.16906643  0x0000AB8A@Data 
        [76]    float   5.15451384  0x0000AB8C@Data 
        [77]    float   5.14369202  0x0000AB8E@Data 
        [78]    float   5.13217688  0x0000AB90@Data 
        [79]    float   5.12138224  0x0000AB92@Data 
        [80]    float   5.10864258  0x0000AB94@Data 
        [81]    float   5.09755421  0x0000AB96@Data 
        [82]    float   5.08670139  0x0000AB98@Data 
        [83]    float   5.07533932  0x0000AB9A@Data 
        [84]    float   5.06220055  0x0000AB9C@Data 
        [85]    float   5.05051184  0x0000AB9E@Data 
        [86]    float   5.0323925   0x0000ABA0@Data 
        [87]    float   5.02009535  0x0000ABA2@Data 
        [88]    float   5.00589037  0x0000ABA4@Data 
        [89]    float   4.99266052  0x0000ABA6@Data 
        [90]    float   4.98074961  0x0000ABA8@Data 
        [91]    float   4.97208595  0x0000ABAA@Data 
        [92]    float   4.95418835  0x0000ABAC@Data 
        [93]    float   4.94484711  0x0000ABAE@Data 
        [94]    float   4.93286276  0x0000ABB0@Data 
        [95]    float   4.91407394  0x0000ABB2@Data 
        [96]    float   4.89981461  0x0000ABB4@Data 
        [97]    float   4.88066959  0x0000ABB6@Data 
        [98]    float   4.86627817  0x0000ABB8@Data 
        [99]    float   4.85396481  0x0000ABBA@Data 
        [100]   float   4.8445859   0x0000ABBC@Data 
        [101]   float   4.83590174  0x0000ABBE@Data 
        [102]   float   4.81760406  0x0000ABC0@Data 
        [103]   float   4.80109262  0x0000ABC2@Data 
        [104]   float   4.7834034   0x0000ABC4@Data 
        [105]   float   4.76695776  0x0000ABC6@Data 
        [106]   float   4.74921989  0x0000ABC8@Data 
        [107]   float   4.73093987  0x0000ABCA@Data 
        [108]   float   4.71105242  0x0000ABCC@Data 
        [109]   float   4.69296217  0x0000ABCE@Data 
        [110]   float   4.67336798  0x0000ABD0@Data 
        [111]   float   4.65337896  0x0000ABD2@Data 
        [112]   float   4.63305998  0x0000ABD4@Data 
        [113]   float   4.61081314  0x0000ABD6@Data 
        [114]   float   4.58835125  0x0000ABD8@Data 
        [115]   float   4.56612396  0x0000ABDA@Data 
        [116]   float   4.54176378  0x0000ABDC@Data 
        [117]   float   4.5160799   0x0000ABDE@Data 
        [118]   float   4.49006844  0x0000ABE0@Data 
        [119]   float   4.46408892  0x0000ABE2@Data 
        [120]   float   4.43635988  0x0000ABE4@Data 
        [121]   float   4.40816641  0x0000ABE6@Data 
        [122]   float   4.3743577   0x0000ABE8@Data 
        [123]   float   4.34195042  0x0000ABEA@Data 
        [124]   float   4.30485106  0x0000ABEC@Data 
        [125]   float   4.26854467  0x0000ABEE@Data 
        [126]   float   4.22855997  0x0000ABF0@Data 
        [127]   float   4.18507242  0x0000ABF2@Data 
        [128]   float   4.13825798  0x0000ABF4@Data 
        [129]   float   4.08585882  0x0000ABF6@Data 
        [130]   float   4.01747036  0x0000ABF8@Data 
        [131]   float   3.9518342   0x0000ABFA@Data 
        [132]   float   3.87490988  0x0000ABFC@Data 
        [133]   float   3.78743052  0x0000ABFE@Data 
        [134]   float   3.6795032   0x0000AC00@Data 
        [135]   float   3.56468153  0x0000AC02@Data 
        [136]   float   3.441401    0x0000AC04@Data 
        [137]   float   3.28855085  0x0000AC06@Data 
        [138]   float   3.05977392  0x0000AC08@Data 
        [139]   float   2.70512319  0x0000AC0A@Data 
        [140]   float   2.10457587  0x0000AC0C@Data 
        [141]   float   1.25320137  0x0000AC0E@Data 
        [142]   float   0.563560903 0x0000AC10@Data 
        [143]   float   -0.232684121    0x0000AC12@Data 
        [144]   float   -0.877381504    0x0000AC14@Data 
        [145]   float   -1.6001364  0x0000AC16@Data 
        [146]   float   -2.3848052  0x0000AC18@Data 
        [147]   float   -6.02172184 0x0000AC1A@Data 
        [148]   float   -6.01136446 0x0000AC1C@Data 
        [149]   float   -6.00309134 0x0000AC1E@Data 
        [150]   float   -5.99089432 0x0000AC20@Data 
        [151]   float   -5.98306513 0x0000AC22@Data 
        [152]   float   -5.97450113 0x0000AC24@Data 
        [153]   float   -5.96361303 0x0000AC26@Data 
        [154]   float   -5.9555769  0x0000AC28@Data 
        [155]   float   -5.94554901 0x0000AC2A@Data 
        [156]   float   -5.93653679 0x0000AC2C@Data 
        [157]   float   -5.92829037 0x0000AC2E@Data 
        [158]   float   -5.91899204 0x0000AC30@Data 
        [159]   float   -5.90928125 0x0000AC32@Data 
        [160]   float   -5.89950085 0x0000AC34@Data 
        [161]   float   -5.89001036 0x0000AC36@Data 
        [162]   float   -5.8812871  0x0000AC38@Data 
        [163]   float   -5.87093401 0x0000AC3A@Data 
        [164]   float   -5.85992479 0x0000AC3C@Data 
        [165]   float   -5.85257244 0x0000AC3E@Data 
        [166]   float   -5.84332848 0x0000AC40@Data 
        [167]   float   -5.83493328 0x0000AC42@Data 
        [168]   float   -5.82537794 0x0000AC44@Data 
        [169]   float   -5.81838274 0x0000AC46@Data 
        [170]   float   -5.80952168 0x0000AC48@Data 
        [171]   float   -5.79733324 0x0000AC4A@Data 
        [172]   float   -5.78962231 0x0000AC4C@Data 
        [173]   float   -5.77854156 0x0000AC4E@Data 
        [174]   float   -5.77110958 0x0000AC50@Data 
        [175]   float   -5.76089001 0x0000AC52@Data 
        [176]   float   -5.7509408  0x0000AC54@Data 
        [177]   float   -5.74085236 0x0000AC56@Data 
        [178]   float   -5.73092604 0x0000AC58@Data 
        [179]   float   -5.72010756 0x0000AC5A@Data 
        [180]   float   -5.7136178  0x0000AC5C@Data 
        [181]   float   -5.70110607 0x0000AC5E@Data 
        [182]   float   -5.69292974 0x0000AC60@Data 
        [183]   float   -5.68302107 0x0000AC62@Data 
        [184]   float   -5.67344904 0x0000AC64@Data 
        [185]   float   -5.66431522 0x0000AC66@Data 
        [186]   float   -5.65729523 0x0000AC68@Data 
        [187]   float   -5.64803219 0x0000AC6A@Data 
        [188]   float   -5.63753128 0x0000AC6C@Data 
        [189]   float   -5.6275053  0x0000AC6E@Data 
        [190]   float   -5.61847305 0x0000AC70@Data 
        [191]   float   -5.60687971 0x0000AC72@Data 
        [192]   float   -5.59741831 0x0000AC74@Data 
        [193]   float   -5.58612919 0x0000AC76@Data 
        [194]   float   -5.57549858 0x0000AC78@Data 
        [195]   float   -5.56789732 0x0000AC7A@Data 
        [196]   float   -5.55788374 0x0000AC7C@Data 
        [197]   float   -5.54605627 0x0000AC7E@Data 
        [198]   float   -5.53692245 0x0000AC80@Data 
        [199]   float   -5.52660131 0x0000AC82@Data 
        [200]   float   -5.51651907 0x0000AC84@Data 
        [201]   float   -5.50623178 0x0000AC86@Data 
        [202]   float   -5.49624109 0x0000AC88@Data 
        [203]   float   -5.485147   0x0000AC8A@Data 
        [204]   float   -5.47501183 0x0000AC8C@Data 
        [205]   float   -5.46328545 0x0000AC8E@Data 
        [206]   float   -5.45254183 0x0000AC90@Data 
        [207]   float   -5.44477701 0x0000AC92@Data 
        [208]   float   -5.4340167  0x0000AC94@Data 
        [209]   float   -5.42170048 0x0000AC96@Data 
        [210]   float   -5.41080379 0x0000AC98@Data 
        [211]   float   -5.39967155 0x0000AC9A@Data 
        [212]   float   -5.3899231  0x0000AC9C@Data 
        [213]   float   -5.37808514 0x0000AC9E@Data 
        [214]   float   -5.36787987 0x0000ACA0@Data 
        [215]   float   -5.35850477 0x0000ACA2@Data 
        [216]   float   -5.34721613 0x0000ACA4@Data 
        [217]   float   -5.33521509 0x0000ACA6@Data 
        [218]   float   -5.32282257 0x0000ACA8@Data 
        [219]   float   -5.31297684 0x0000ACAA@Data 
        [220]   float   -5.30264711 0x0000ACAC@Data 
        [221]   float   -5.29186058 0x0000ACAE@Data 
        [222]   float   -5.28142786 0x0000ACB0@Data 
        [223]   float   -5.26961184 0x0000ACB2@Data 
        [224]   float   -5.26108456 0x0000ACB4@Data 
        [225]   float   -5.24903965 0x0000ACB6@Data 
        [226]   float   -5.23651075 0x0000ACB8@Data 
        [227]   float   -5.22406387 0x0000ACBA@Data 
        [228]   float   -5.20979643 0x0000ACBC@Data 
        [229]   float   -5.19997168 0x0000ACBE@Data 
        [230]   float   -5.1882329  0x0000ACC0@Data 
        [231]   float   -5.17625809 0x0000ACC2@Data 
        [232]   float   -5.16158962 0x0000ACC4@Data 
        [233]   float   -5.14840126 0x0000ACC6@Data 
        [234]   float   -5.13927889 0x0000ACC8@Data 
        [235]   float   -5.13136959 0x0000ACCA@Data 
        [236]   float   -5.11481094 0x0000ACCC@Data 
        [237]   float   -5.10613918 0x0000ACCE@Data 
        [238]   float   -5.09396029 0x0000ACD0@Data 
        [239]   float   -5.07759237 0x0000ACD2@Data 
        [240]   float   -5.06652117 0x0000ACD4@Data 
        [241]   float   -5.05575037 0x0000ACD6@Data 
        [242]   float   -5.03821468 0x0000ACD8@Data 
        [243]   float   -5.02769613 0x0000ACDA@Data 
        [244]   float   -5.01593161 0x0000ACDC@Data 
        [245]   float   -5.00187397 0x0000ACDE@Data 
        [246]   float   -4.9867239  0x0000ACE0@Data 
        [247]   float   -4.9731946  0x0000ACE2@Data 
        [248]   float   -4.96112251 0x0000ACE4@Data 
        [249]   float   -4.94452286 0x0000ACE6@Data 
        [250]   float   -4.93108988 0x0000ACE8@Data 
        [251]   float   -4.91571093 0x0000ACEA@Data 
        [252]   float   -4.89764166 0x0000ACEC@Data 
        [253]   float   -4.88364983 0x0000ACEE@Data 
        [254]   float   -4.86943626 0x0000ACF0@Data 
        [255]   float   -4.85259581 0x0000ACF2@Data 
        [256]   float   -4.83773279 0x0000ACF4@Data 
        [257]   float   -4.82245827 0x0000ACF6@Data 
        [258]   float   -4.80447149 0x0000ACF8@Data 
        [259]   float   -4.78616667 0x0000ACFA@Data 
        [260]   float   -4.77194595 0x0000ACFC@Data 
        [261]   float   -4.75696182 0x0000ACFE@Data 
        [262]   float   -4.74021482 0x0000AD00@Data 
        [263]   float   -4.725667   0x0000AD02@Data 
        [264]   float   -4.70963478 0x0000AD04@Data 
        [265]   float   -4.69183779 0x0000AD06@Data 
        [266]   float   -4.67109823 0x0000AD08@Data 
        [267]   float   -4.6520977  0x0000AD0A@Data 
        [268]   float   -4.63173342 0x0000AD0C@Data 
        [269]   float   -4.60824251 0x0000AD0E@Data 
        [270]   float   -4.58578348 0x0000AD10@Data 
        [271]   float   -4.56532001 0x0000AD12@Data 
        [272]   float   -4.53728199 0x0000AD14@Data 
        [273]   float   -4.51299191 0x0000AD16@Data 
        [274]   float   -4.48875237 0x0000AD18@Data 
        [275]   float   -4.45950317 0x0000AD1A@Data 
        [276]   float   -4.43132257 0x0000AD1C@Data 
        [277]   float   -4.40324116 0x0000AD1E@Data 
        [278]   float   -4.36883783 0x0000AD20@Data 
        [279]   float   -4.33383942 0x0000AD22@Data 
        [280]   float   -4.29820776 0x0000AD24@Data 
        [281]   float   -4.25666571 0x0000AD26@Data 
        [282]   float   -4.21294165 0x0000AD28@Data 
        [283]   float   -4.16904402 0x0000AD2A@Data 
        [284]   float   -4.11754942 0x0000AD2C@Data 
        [285]   float   -4.05849981 0x0000AD2E@Data 
        [286]   float   -3.99171638 0x0000AD30@Data 
        [287]   float   -3.92622542 0x0000AD32@Data 
        [288]   float   -3.83736086 0x0000AD34@Data 
        [289]   float   -3.7439847  0x0000AD36@Data 
        [290]   float   -3.64928699 0x0000AD38@Data 
        [291]   float   -3.54741406 0x0000AD3A@Data 
        [292]   float   -3.40504026 0x0000AD3C@Data 
        [293]   float   -3.17164207 0x0000AD3E@Data 
    '''

    tag = 'SiC-529-0957-phase-B-80V-[ADC-gain-Tuned]-1A too small'
    ccs_expressions[tag] = '''
        [0] float   0.866030574 0x0000A89C@Data 
        [1] float   0.847599566 0x0000A89E@Data 
        [2] float   0.82918942  0x0000A8A0@Data 
        [3] float   0.81073308  0x0000A8A2@Data 
        [4] float   0.792302489 0x0000A8A4@Data 
        [5] float   0.773884714 0x0000A8A6@Data 
        [6] float   0.755476117 0x0000A8A8@Data 
        [7] float   0.737052202 0x0000A8AA@Data 
        [8] float   0.718609273 0x0000A8AC@Data 
        [9] float   0.700181127 0x0000A8AE@Data 
        [10]    float   0.681759715 0x0000A8B0@Data 
        [11]    float   0.663332105 0x0000A8B2@Data 
        [12]    float   0.644897044 0x0000A8B4@Data 
        [13]    float   0.626470447 0x0000A8B6@Data 
        [14]    float   0.608071208 0x0000A8B8@Data 
        [15]    float   0.589636743 0x0000A8BA@Data 
        [16]    float   0.571185529 0x0000A8BC@Data 
        [17]    float   0.552772522 0x0000A8BE@Data 
        [18]    float   0.534353256 0x0000A8C0@Data 
        [19]    float   0.515941262 0x0000A8C2@Data 
        [20]    float   0.497505635 0x0000A8C4@Data 
        [21]    float   0.479097277 0x0000A8C6@Data 
        [22]    float   0.460647523 0x0000A8C8@Data 
        [23]    float   0.442202508 0x0000A8CA@Data 
        [24]    float   0.423816293 0x0000A8CC@Data 
        [25]    float   0.405390084 0x0000A8CE@Data 
        [26]    float   0.386923403 0x0000A8D0@Data 
        [27]    float   0.36850509  0x0000A8D2@Data 
        [28]    float   0.350108862 0x0000A8D4@Data 
        [29]    float   0.331665754 0x0000A8D6@Data 
        [30]    float   0.31323415  0x0000A8D8@Data 
        [31]    float   0.294812471 0x0000A8DA@Data 
        [32]    float   0.276364475 0x0000A8DC@Data 
        [33]    float   0.257962525 0x0000A8DE@Data 
        [34]    float   0.23953414  0x0000A8E0@Data 
        [35]    float   0.221116379 0x0000A8E2@Data 
        [36]    float   0.202695683 0x0000A8E4@Data 
        [37]    float   0.184211433 0x0000A8E6@Data 
        [38]    float   0.1658898   0x0000A8E8@Data 
        [39]    float   0.147394136 0x0000A8EA@Data 
        [40]    float   0.128912956 0x0000A8EC@Data 
        [41]    float   0.110546395 0x0000A8EE@Data 
        [42]    float   0.0921181366    0x0000A8F0@Data 
        [43]    float   0.0737087131    0x0000A8F2@Data 
        [44]    float   0.0552865602    0x0000A8F4@Data 
        [45]    float   0.036850974 0x0000A8F6@Data 
        [46]    float   0.0184165034    0x0000A8F8@Data 
        [47]    float   -0.866039753    0x0000A8FA@Data 
        [48]    float   -0.847616673    0x0000A8FC@Data 
        [49]    float   -0.82915926 0x0000A8FE@Data 
        [50]    float   -0.810743034    0x0000A900@Data 
        [51]    float   -0.792318523    0x0000A902@Data 
        [52]    float   -0.773894012    0x0000A904@Data 
        [53]    float   -0.755460858    0x0000A906@Data 
        [54]    float   -0.737043142    0x0000A908@Data 
        [55]    float   -0.718611002    0x0000A90A@Data 
        [56]    float   -0.700198293    0x0000A90C@Data 
        [57]    float   -0.681771636    0x0000A90E@Data 
        [58]    float   -0.663331449    0x0000A910@Data 
        [59]    float   -0.644906461    0x0000A912@Data 
        [60]    float   -0.626485765    0x0000A914@Data 
        [61]    float   -0.608068347    0x0000A916@Data 
        [62]    float   -0.589633644    0x0000A918@Data 
        [63]    float   -0.571221888    0x0000A91A@Data 
        [64]    float   -0.552799344    0x0000A91C@Data 
        [65]    float   -0.534351766    0x0000A91E@Data 
        [66]    float   -0.515924215    0x0000A920@Data 
        [67]    float   -0.497484267    0x0000A922@Data 
        [68]    float   -0.47908783 0x0000A924@Data 
        [69]    float   -0.460637867    0x0000A926@Data 
        [70]    float   -0.442205817    0x0000A928@Data 
        [71]    float   -0.423783541    0x0000A92A@Data 
        [72]    float   -0.405385226    0x0000A92C@Data 
        [73]    float   -0.386912733    0x0000A92E@Data 
        [74]    float   -0.36850521 0x0000A930@Data 
        [75]    float   -0.350108206    0x0000A932@Data 
        [76]    float   -0.331656516    0x0000A934@Data 
        [77]    float   -0.313253015    0x0000A936@Data 
        [78]    float   -0.294824243    0x0000A938@Data 
        [79]    float   -0.276371032    0x0000A93A@Data 
        [80]    float   -0.257957667    0x0000A93C@Data 
        [81]    float   -0.239507183    0x0000A93E@Data 
        [82]    float   -0.221103758    0x0000A940@Data 
        [83]    float   -0.202661291    0x0000A942@Data 
        [84]    float   -0.184260681    0x0000A944@Data 
        [85]    float   -0.16585204 0x0000A946@Data 
        [86]    float   -0.147445798    0x0000A948@Data 
        [87]    float   -0.128958687    0x0000A94A@Data 
        [88]    float   -0.110545732    0x0000A94C@Data 
        [89]    float   -0.0921209231   0x0000A94E@Data 
        [90]    float   -0.0737150386   0x0000A950@Data 
        [91]    float   -0.0552910045   0x0000A952@Data 
        [92]    float   -0.0368487649   0x0000A954@Data 
        [93]    float   -0.0184173305   0x0000A956@Data 

        [0] float   5.29960012  0x0000A964@Data 
        [1] float   5.26355648  0x0000A966@Data 
        [2] float   5.22537804  0x0000A968@Data 
        [3] float   5.18560028  0x0000A96A@Data 
        [4] float   5.14695358  0x0000A96C@Data 
        [5] float   5.10533905  0x0000A96E@Data 
        [6] float   5.06375551  0x0000A970@Data 
        [7] float   5.02423096  0x0000A972@Data 
        [8] float   4.98234081  0x0000A974@Data 
        [9] float   4.93927908  0x0000A976@Data 
        [10]    float   4.89598274  0x0000A978@Data 
        [11]    float   4.85272694  0x0000A97A@Data 
        [12]    float   4.80757189  0x0000A97C@Data 
        [13]    float   4.7631588   0x0000A97E@Data 
        [14]    float   4.71587658  0x0000A980@Data 
        [15]    float   4.66751432  0x0000A982@Data 
        [16]    float   4.61977243  0x0000A984@Data 
        [17]    float   4.57252359  0x0000A986@Data 
        [18]    float   4.52002144  0x0000A988@Data 
        [19]    float   4.46552515  0x0000A98A@Data 
        [20]    float   4.40926218  0x0000A98C@Data 
        [21]    float   4.35200262  0x0000A98E@Data 
        [22]    float   4.29228497  0x0000A990@Data 
        [23]    float   4.22966623  0x0000A992@Data 
        [24]    float   4.16210604  0x0000A994@Data 
        [25]    float   4.0928278   0x0000A996@Data 
        [26]    float   4.01896858  0x0000A998@Data 
        [27]    float   3.94044614  0x0000A99A@Data 
        [28]    float   3.85693669  0x0000A99C@Data 
        [29]    float   3.766325    0x0000A99E@Data 
        [30]    float   3.68593669  0x0000A9A0@Data 
        [31]    float   3.58009315  0x0000A9A2@Data 
        [32]    float   3.46724916  0x0000A9A4@Data 
        [33]    float   3.33849645  0x0000A9A6@Data 
        [34]    float   3.19714928  0x0000A9A8@Data 
        [35]    float   3.04905152  0x0000A9AA@Data 
        [36]    float   2.86288071  0x0000A9AC@Data 
        [37]    float   2.64139366  0x0000A9AE@Data 
        [38]    float   2.37475395  0x0000A9B0@Data 
        [39]    float   2.04847097  0x0000A9B2@Data 
        [40]    float   1.63256955  0x0000A9B4@Data 
        [41]    float   1.22680163  0x0000A9B6@Data 
        [42]    float   0.895828962 0x0000A9B8@Data 
        [43]    float   0.655625939 0x0000A9BA@Data 
        [44]    float   0.509033263 0x0000A9BC@Data 
        [45]    float   0.415855706 0x0000A9BE@Data 
        [46]    float   0.247680798 0x0000A9C0@Data 
        [47]    float   -5.33538389 0x0000A9C2@Data 
        [48]    float   -5.29685116 0x0000A9C4@Data 
        [49]    float   -5.2595377  0x0000A9C6@Data 
        [50]    float   -5.22158098 0x0000A9C8@Data 
        [51]    float   -5.1830554  0x0000A9CA@Data 
        [52]    float   -5.14358854 0x0000A9CC@Data 
        [53]    float   -5.10297155 0x0000A9CE@Data 
        [54]    float   -5.06064129 0x0000A9D0@Data 
        [55]    float   -5.01896858 0x0000A9D2@Data 
        [56]    float   -4.97791052 0x0000A9D4@Data 
        [57]    float   -4.93481731 0x0000A9D6@Data 
        [58]    float   -4.8921833  0x0000A9D8@Data 
        [59]    float   -4.8479104  0x0000A9DA@Data 
        [60]    float   -4.80344248 0x0000A9DC@Data 
        [61]    float   -4.75673437 0x0000A9DE@Data 
        [62]    float   -4.71031904 0x0000A9E0@Data 
        [63]    float   -4.66127682 0x0000A9E2@Data 
        [64]    float   -4.61284494 0x0000A9E4@Data 
        [65]    float   -4.56656933 0x0000A9E6@Data 
        [66]    float   -4.51594114 0x0000A9E8@Data 
        [67]    float   -4.46221066 0x0000A9EA@Data 
        [68]    float   -4.40783072 0x0000A9EC@Data 
        [69]    float   -4.34962797 0x0000A9EE@Data 
        [70]    float   -4.29057026 0x0000A9F0@Data 
        [71]    float   -4.22814465 0x0000A9F2@Data 
        [72]    float   -4.16174173 0x0000A9F4@Data 
        [73]    float   -4.09322023 0x0000A9F6@Data 
        [74]    float   -4.01984739 0x0000A9F8@Data 
        [75]    float   -3.94110727 0x0000A9FA@Data 
        [76]    float   -3.85721111 0x0000A9FC@Data 
        [77]    float   -3.77545857 0x0000A9FE@Data 
        [78]    float   -3.68497539 0x0000AA00@Data 
        [79]    float   -3.5784688  0x0000AA02@Data 
        [80]    float   -3.46598411 0x0000AA04@Data 
        [81]    float   -3.33772945 0x0000AA06@Data 
        [82]    float   -3.20002413 0x0000AA08@Data 
        [83]    float   -3.05843306 0x0000AA0A@Data 
        [84]    float   -2.8776021  0x0000AA0C@Data 
        [85]    float   -2.66463566 0x0000AA0E@Data 
        [86]    float   -2.41172242 0x0000AA10@Data 
        [87]    float   -2.09841394 0x0000AA12@Data 
        [88]    float   -1.71704733 0x0000AA14@Data 
        [89]    float   -1.32776868 0x0000AA16@Data 
        [90]    float   -0.997559905    0x0000AA18@Data 
        [91]    float   -0.739297926    0x0000AA1A@Data 
        [92]    float   -0.579165876    0x0000AA1C@Data 
        [93]    float   -0.456074327    0x0000AA1E@Data 
    '''

    tag = 'SiC-529-0957-phase-B-80V-[ADC-gain-Tuned]-3A'
    ccs_expressions[tag] = '''
        [0] float   2.59805846  0x0000A89C@Data 
        [1] float   2.54280305  0x0000A89E@Data 
        [2] float   2.48753476  0x0000A8A0@Data 
        [3] float   2.43223143  0x0000A8A2@Data 
        [4] float   2.37696171  0x0000A8A4@Data 
        [5] float   2.32168531  0x0000A8A6@Data 
        [6] float   2.26641011  0x0000A8A8@Data 
        [7] float   2.21110868  0x0000A8AA@Data 
        [8] float   2.15581727  0x0000A8AC@Data 
        [9] float   2.10062027  0x0000A8AE@Data 
        [10]    float   2.04530478  0x0000A8B0@Data 
        [11]    float   1.99001491  0x0000A8B2@Data 
        [12]    float   1.93471014  0x0000A8B4@Data 
        [13]    float   1.87946141  0x0000A8B6@Data 
        [14]    float   1.82416713  0x0000A8B8@Data 
        [15]    float   1.76890457  0x0000A8BA@Data 
        [16]    float   1.71363568  0x0000A8BC@Data 
        [17]    float   1.65835309  0x0000A8BE@Data 
        [18]    float   1.60310102  0x0000A8C0@Data 
        [19]    float   1.54779136  0x0000A8C2@Data 
        [20]    float   1.49252319  0x0000A8C4@Data 
        [21]    float   1.43724847  0x0000A8C6@Data 
        [22]    float   1.38197458  0x0000A8C8@Data 
        [23]    float   1.32670796  0x0000A8CA@Data 
        [24]    float   1.27137792  0x0000A8CC@Data 
        [25]    float   1.21612954  0x0000A8CE@Data 
        [26]    float   1.16083336  0x0000A8D0@Data 
        [27]    float   1.10557353  0x0000A8D2@Data 
        [28]    float   1.05028069  0x0000A8D4@Data 
        [29]    float   0.994998574 0x0000A8D6@Data 
        [30]    float   0.939729035 0x0000A8D8@Data 
        [31]    float   0.884459198 0x0000A8DA@Data 
        [32]    float   0.829162359 0x0000A8DC@Data 
        [33]    float   0.773884535 0x0000A8DE@Data 
        [34]    float   0.718618095 0x0000A8E0@Data 
        [35]    float   0.663363934 0x0000A8E2@Data 
        [36]    float   0.608053267 0x0000A8E4@Data 
        [37]    float   0.552779853 0x0000A8E6@Data 
        [38]    float   0.49750182  0x0000A8E8@Data 
        [39]    float   0.442222327 0x0000A8EA@Data 
        [40]    float   0.386930317 0x0000A8EC@Data 
        [41]    float   0.331659943 0x0000A8EE@Data 
        [42]    float   0.276393086 0x0000A8F0@Data 
        [43]    float   0.221120864 0x0000A8F2@Data 
        [44]    float   0.16582182  0x0000A8F4@Data 
        [45]    float   0.110596165 0x0000A8F6@Data 
        [46]    float   0.0552883446    0x0000A8F8@Data 
        [47]    float   -2.59807873 0x0000A8FA@Data 
        [48]    float   -2.54277563 0x0000A8FC@Data 
        [49]    float   -2.48750353 0x0000A8FE@Data 
        [50]    float   -2.43225455 0x0000A900@Data 
        [51]    float   -2.3769753  0x0000A902@Data 
        [52]    float   -2.32169461 0x0000A904@Data 
        [53]    float   -2.26642084 0x0000A906@Data 
        [54]    float   -2.21110868 0x0000A908@Data 
        [55]    float   -2.15583682 0x0000A90A@Data 
        [56]    float   -2.10060096 0x0000A90C@Data 
        [57]    float   -2.04531288 0x0000A90E@Data 
        [58]    float   -1.99001205 0x0000A910@Data 
        [59]    float   -1.93472815 0x0000A912@Data 
        [60]    float   -1.87949014 0x0000A914@Data 
        [61]    float   -1.82418108 0x0000A916@Data 
        [62]    float   -1.76889956 0x0000A918@Data 
        [63]    float   -1.71363986 0x0000A91A@Data 
        [64]    float   -1.65837109 0x0000A91C@Data 
        [65]    float   -1.60307872 0x0000A91E@Data 
        [66]    float   -1.54777884 0x0000A920@Data 
        [67]    float   -1.49246967 0x0000A922@Data 
        [68]    float   -1.43722463 0x0000A924@Data 
        [69]    float   -1.38195455 0x0000A926@Data 
        [70]    float   -1.32668948 0x0000A928@Data 
        [71]    float   -1.27138841 0x0000A92A@Data 
        [72]    float   -1.21611142 0x0000A92C@Data 
        [73]    float   -1.16084325 0x0000A92E@Data 
        [74]    float   -1.10556281 0x0000A930@Data 
        [75]    float   -1.0502789  0x0000A932@Data 
        [76]    float   -0.995001674    0x0000A934@Data 
        [77]    float   -0.93971324 0x0000A936@Data 
        [78]    float   -0.884436488    0x0000A938@Data 
        [79]    float   -0.829175651    0x0000A93A@Data 
        [80]    float   -0.773864329    0x0000A93C@Data 
        [81]    float   -0.71862191 0x0000A93E@Data 
        [82]    float   -0.663338184    0x0000A940@Data 
        [83]    float   -0.60804534 0x0000A942@Data 
        [84]    float   -0.552771747    0x0000A944@Data 
        [85]    float   -0.49748072 0x0000A946@Data 
        [86]    float   -0.442236453    0x0000A948@Data 
        [87]    float   -0.386944056    0x0000A94A@Data 
        [88]    float   -0.3316679  0x0000A94C@Data 
        [89]    float   -0.276391029    0x0000A94E@Data 
        [90]    float   -0.221100315    0x0000A950@Data 
        [91]    float   -0.165858999    0x0000A952@Data 
        [92]    float   -0.110550329    0x0000A954@Data 
        [93]    float   -0.0552803725   0x0000A956@Data 

        [0] float   8.1953373   0x0000A964@Data 
        [1] float   8.10455704  0x0000A966@Data 
        [2] float   8.01686096  0x0000A968@Data 
        [3] float   7.93063688  0x0000A96A@Data 
        [4] float   7.85211039  0x0000A96C@Data 
        [5] float   7.76353025  0x0000A96E@Data 
        [6] float   7.67756605  0x0000A970@Data 
        [7] float   7.59230852  0x0000A972@Data 
        [8] float   7.51024389  0x0000A974@Data 
        [9] float   7.4076252   0x0000A976@Data 
        [10]    float   7.3174715   0x0000A978@Data 
        [11]    float   7.22633886  0x0000A97A@Data 
        [12]    float   7.13549232  0x0000A97C@Data 
        [13]    float   7.04421568  0x0000A97E@Data 
        [14]    float   6.95446777  0x0000A980@Data 
        [15]    float   6.86407042  0x0000A982@Data 
        [16]    float   6.77300167  0x0000A984@Data 
        [17]    float   6.68270063  0x0000A986@Data 
        [18]    float   6.5886035   0x0000A988@Data 
        [19]    float   6.50304699  0x0000A98A@Data 
        [20]    float   6.40898037  0x0000A98C@Data 
        [21]    float   6.31664991  0x0000A98E@Data 
        [22]    float   6.22213984  0x0000A990@Data 
        [23]    float   6.12641811  0x0000A992@Data 
        [24]    float   6.02993059  0x0000A994@Data 
        [25]    float   5.93260717  0x0000A996@Data 
        [26]    float   5.8346386   0x0000A998@Data 
        [27]    float   5.73401594  0x0000A99A@Data 
        [28]    float   5.6310215   0x0000A99C@Data 
        [29]    float   5.52691269  0x0000A99E@Data 
        [30]    float   5.42489958  0x0000A9A0@Data 
        [31]    float   5.31394863  0x0000A9A2@Data 
        [32]    float   5.20203352  0x0000A9A4@Data 
        [33]    float   5.08434868  0x0000A9A6@Data 
        [34]    float   4.96206903  0x0000A9A8@Data 
        [35]    float   4.83198738  0x0000A9AA@Data 
        [36]    float   4.70008087  0x0000A9AC@Data 
        [37]    float   4.55892181  0x0000A9AE@Data 
        [38]    float   4.3958087   0x0000A9B0@Data 
        [39]    float   4.21749401  0x0000A9B2@Data 
        [40]    float   4.00987005  0x0000A9B4@Data 
        [41]    float   3.75894547  0x0000A9B6@Data 
        [42]    float   3.46091819  0x0000A9B8@Data 
        [43]    float   3.04869437  0x0000A9BA@Data 
        [44]    float   2.38282633  0x0000A9BC@Data 
        [45]    float   1.2396481   0x0000A9BE@Data 
        [46]    float   0.513116121 0x0000A9C0@Data 
        [47]    float   -8.21723175 0x0000A9C2@Data 
        [48]    float   -8.13222694 0x0000A9C4@Data 
        [49]    float   -8.05079746 0x0000A9C6@Data 
        [50]    float   -7.96500683 0x0000A9C8@Data 
        [51]    float   -7.87996769 0x0000A9CA@Data 
        [52]    float   -7.79305172 0x0000A9CC@Data 
        [53]    float   -7.70666075 0x0000A9CE@Data 
        [54]    float   -7.61965752 0x0000A9D0@Data 
        [55]    float   -7.53716755 0x0000A9D2@Data 
        [56]    float   -7.44602156 0x0000A9D4@Data 
        [57]    float   -7.35914278 0x0000A9D6@Data 
        [58]    float   -7.27010679 0x0000A9D8@Data 
        [59]    float   -7.17926121 0x0000A9DA@Data 
        [60]    float   -7.08862734 0x0000A9DC@Data 
        [61]    float   -6.99922848 0x0000A9DE@Data 
        [62]    float   -6.90802574 0x0000A9E0@Data 
        [63]    float   -6.81647444 0x0000A9E2@Data 
        [64]    float   -6.72372198 0x0000A9E4@Data 
        [65]    float   -6.63322639 0x0000A9E6@Data 
        [66]    float   -6.54663754 0x0000A9E8@Data 
        [67]    float   -6.45377302 0x0000A9EA@Data 
        [68]    float   -6.35797167 0x0000A9EC@Data 
        [69]    float   -6.2630477  0x0000A9EE@Data 
        [70]    float   -6.1673584  0x0000A9F0@Data 
        [71]    float   -6.07148314 0x0000A9F2@Data 
        [72]    float   -5.9732728  0x0000A9F4@Data 
        [73]    float   -5.8757844  0x0000A9F6@Data 
        [74]    float   -5.77360344 0x0000A9F8@Data 
        [75]    float   -5.67199659 0x0000A9FA@Data 
        [76]    float   -5.56714439 0x0000A9FC@Data 
        [77]    float   -5.46498632 0x0000A9FE@Data 
        [78]    float   -5.3567605  0x0000AA00@Data 
        [79]    float   -5.24218845 0x0000AA02@Data 
        [80]    float   -5.12665987 0x0000AA04@Data 
        [81]    float   -5.00434494 0x0000AA06@Data 
        [82]    float   -4.87649822 0x0000AA08@Data 
        [83]    float   -4.74341106 0x0000AA0A@Data 
        [84]    float   -4.60018539 0x0000AA0C@Data 
        [85]    float   -4.44711637 0x0000AA0E@Data 
        [86]    float   -4.27415133 0x0000AA10@Data 
        [87]    float   -4.07555294 0x0000AA12@Data 
        [88]    float   -3.8399086  0x0000AA14@Data 
        [89]    float   -3.56012058 0x0000AA16@Data 
        [90]    float   -3.18063021 0x0000AA18@Data 
        [91]    float   -2.63663483 0x0000AA1A@Data 
        [92]    float   -1.67963481 0x0000AA1C@Data 
        [93]    float   -0.726204515    0x0000AA1E@Data 
    '''

    tag = 'SiC-602-1647-phase-B-180V-[ADC-gain-Tuned]-3A'
    ccs_expressions[tag] = '''
        [0] float   2.5980885   0x0000A89C@Data 
        [1] float   2.54278207  0x0000A89E@Data 
        [2] float   2.48753476  0x0000A8A0@Data 
        [3] float   2.43222594  0x0000A8A2@Data 
        [4] float   2.37695599  0x0000A8A4@Data 
        [5] float   2.32168674  0x0000A8A6@Data 
        [6] float   2.26640224  0x0000A8A8@Data 
        [7] float   2.21113539  0x0000A8AA@Data 
        [8] float   2.15586615  0x0000A8AC@Data 
        [9] float   2.10057068  0x0000A8AE@Data 
        [10]    float   2.04528069  0x0000A8B0@Data 
        [11]    float   1.99002528  0x0000A8B2@Data 
        [12]    float   1.93473625  0x0000A8B4@Data 
        [13]    float   1.87945211  0x0000A8B6@Data 
        [14]    float   1.8241787   0x0000A8B8@Data 
        [15]    float   1.76888454  0x0000A8BA@Data 
        [16]    float   1.7136184   0x0000A8BC@Data 
        [17]    float   1.65833461  0x0000A8BE@Data 
        [18]    float   1.60304666  0x0000A8C0@Data 
        [19]    float   1.54781771  0x0000A8C2@Data 
        [20]    float   1.49254107  0x0000A8C4@Data 
        [21]    float   1.43721771  0x0000A8C6@Data 
        [22]    float   1.38196576  0x0000A8C8@Data 
        [23]    float   1.32666302  0x0000A8CA@Data 
        [24]    float   1.27138293  0x0000A8CC@Data 
        [25]    float   1.21611094  0x0000A8CE@Data 
        [26]    float   1.16083896  0x0000A8D0@Data 
        [27]    float   1.10556233  0x0000A8D2@Data 
        [28]    float   1.05027783  0x0000A8D4@Data 
        [29]    float   0.995013893 0x0000A8D6@Data 
        [30]    float   0.939735889 0x0000A8D8@Data 
        [31]    float   0.88444382  0x0000A8DA@Data 
        [32]    float   0.829172015 0x0000A8DC@Data 
        [33]    float   0.773881435 0x0000A8DE@Data 
        [34]    float   0.718625009 0x0000A8E0@Data 
        [35]    float   0.663355887 0x0000A8E2@Data 
        [36]    float   0.608050525 0x0000A8E4@Data 
        [37]    float   0.552775204 0x0000A8E6@Data 
        [38]    float   0.497509241 0x0000A8E8@Data 
        [39]    float   0.442205697 0x0000A8EA@Data 
        [40]    float   0.386955261 0x0000A8EC@Data 
        [41]    float   0.331704229 0x0000A8EE@Data 
        [42]    float   0.276381701 0x0000A8F0@Data 
        [43]    float   0.221024051 0x0000A8F2@Data 
        [44]    float   0.165830493 0x0000A8F4@Data 
        [45]    float   0.110543929 0x0000A8F6@Data 
        [46]    float   0.0552896485    0x0000A8F8@Data 
        [47]    float   -2.59806228 0x0000A8FA@Data 
        [48]    float   -2.54276752 0x0000A8FC@Data 
        [49]    float   -2.4875145  0x0000A8FE@Data 
        [50]    float   -2.4322114  0x0000A900@Data 
        [51]    float   -2.37694836 0x0000A902@Data 
        [52]    float   -2.32167888 0x0000A904@Data 
        [53]    float   -2.26640081 0x0000A906@Data 
        [54]    float   -2.21112204 0x0000A908@Data 
        [55]    float   -2.15581322 0x0000A90A@Data 
        [56]    float   -2.1005671  0x0000A90C@Data 
        [57]    float   -2.04529643 0x0000A90E@Data 
        [58]    float   -1.99000585 0x0000A910@Data 
        [59]    float   -1.93475008 0x0000A912@Data 
        [60]    float   -1.87945867 0x0000A914@Data 
        [61]    float   -1.8241781  0x0000A916@Data 
        [62]    float   -1.76892805 0x0000A918@Data 
        [63]    float   -1.71361089 0x0000A91A@Data 
        [64]    float   -1.65834892 0x0000A91C@Data 
        [65]    float   -1.6030798  0x0000A91E@Data 
        [66]    float   -1.54781282 0x0000A920@Data 
        [67]    float   -1.49254358 0x0000A922@Data 
        [68]    float   -1.43724978 0x0000A924@Data 
        [69]    float   -1.38196635 0x0000A926@Data 
        [70]    float   -1.32667673 0x0000A928@Data 
        [71]    float   -1.27139091 0x0000A92A@Data 
        [72]    float   -1.2161262  0x0000A92C@Data 
        [73]    float   -1.16085315 0x0000A92E@Data 
        [74]    float   -1.10555589 0x0000A930@Data 
        [75]    float   -1.0502944  0x0000A932@Data 
        [76]    float   -0.995004356    0x0000A934@Data 
        [77]    float   -0.939715326    0x0000A936@Data 
        [78]    float   -0.884458184    0x0000A938@Data 
        [79]    float   -0.829173684    0x0000A93A@Data 
        [80]    float   -0.77388674 0x0000A93C@Data 
        [81]    float   -0.718627691    0x0000A93E@Data 
        [82]    float   -0.663349688    0x0000A940@Data 
        [83]    float   -0.608077109    0x0000A942@Data 
        [84]    float   -0.552777946    0x0000A944@Data 
        [85]    float   -0.497495264    0x0000A946@Data 
        [86]    float   -0.442224652    0x0000A948@Data 
        [87]    float   -0.386865109    0x0000A94A@Data 
        [88]    float   -0.331698895    0x0000A94C@Data 
        [89]    float   -0.276414722    0x0000A94E@Data 
        [90]    float   -0.221121743    0x0000A950@Data 
        [91]    float   -0.165866747    0x0000A952@Data 
        [92]    float   -0.110545345    0x0000A954@Data 
        [93]    float   -0.0552563109   0x0000A956@Data 

        [0] float   12.4034624  0x0000A964@Data 
        [1] float   12.313405   0x0000A966@Data 
        [2] float   12.2277403  0x0000A968@Data 
        [3] float   12.1300383  0x0000A96A@Data 
        [4] float   12.0388803  0x0000A96C@Data 
        [5] float   11.9449377  0x0000A96E@Data 
        [6] float   11.8568678  0x0000A970@Data 
        [7] float   11.7607269  0x0000A972@Data 
        [8] float   11.6694469  0x0000A974@Data 
        [9] float   11.5823126  0x0000A976@Data 
        [10]    float   11.4833899  0x0000A978@Data 
        [11]    float   11.3822889  0x0000A97A@Data 
        [12]    float   11.2835817  0x0000A97C@Data 
        [13]    float   11.1833811  0x0000A97E@Data 
        [14]    float   11.0891237  0x0000A980@Data 
        [15]    float   10.9866285  0x0000A982@Data 
        [16]    float   10.8850965  0x0000A984@Data 
        [17]    float   10.7869015  0x0000A986@Data 
        [18]    float   10.6857815  0x0000A988@Data 
        [19]    float   10.5972843  0x0000A98A@Data 
        [20]    float   10.4852467  0x0000A98C@Data 
        [21]    float   10.365387   0x0000A98E@Data 
        [22]    float   10.2569075  0x0000A990@Data 
        [23]    float   10.1504927  0x0000A992@Data 
        [24]    float   10.021347   0x0000A994@Data 
        [25]    float   9.90989494  0x0000A996@Data 
        [26]    float   9.77521133  0x0000A998@Data 
        [27]    float   9.64620686  0x0000A99A@Data 
        [28]    float   9.51123238  0x0000A99C@Data 
        [29]    float   9.36225891  0x0000A99E@Data 
        [30]    float   9.22058678  0x0000A9A0@Data 
        [31]    float   9.06615448  0x0000A9A2@Data 
        [32]    float   8.90116024  0x0000A9A4@Data 
        [33]    float   8.7139082   0x0000A9A6@Data 
        [34]    float   8.51770401  0x0000A9A8@Data 
        [35]    float   8.30315876  0x0000A9AA@Data 
        [36]    float   8.05904484  0x0000A9AC@Data 
        [37]    float   7.77789116  0x0000A9AE@Data 
        [38]    float   7.47486782  0x0000A9B0@Data 
        [39]    float   7.09943485  0x0000A9B2@Data 
        [40]    float   6.70494604  0x0000A9B4@Data 
        [41]    float   6.13136196  0x0000A9B6@Data 
        [42]    float   5.40683651  0x0000A9B8@Data 
        [43]    float   4.25867844  0x0000A9BA@Data 
        [44]    float   2.55136704  0x0000A9BC@Data 
        [45]    float   1.17127824  0x0000A9BE@Data 
        [46]    float   0.485746443 0x0000A9C0@Data 
        [47]    float   -12.43717   0x0000A9C2@Data 
        [48]    float   -12.3467617 0x0000A9C4@Data 
        [49]    float   -12.2532711 0x0000A9C6@Data 
        [50]    float   -12.162919  0x0000A9C8@Data 
        [51]    float   -12.0683336 0x0000A9CA@Data 
        [52]    float   -11.9776602 0x0000A9CC@Data 
        [53]    float   -11.8846931 0x0000A9CE@Data 
        [54]    float   -11.7901306 0x0000A9D0@Data 
        [55]    float   -11.6999416 0x0000A9D2@Data 
        [56]    float   -11.6055021 0x0000A9D4@Data 
        [57]    float   -11.5079584 0x0000A9D6@Data 
        [58]    float   -11.414155  0x0000A9D8@Data 
        [59]    float   -11.3154058 0x0000A9DA@Data 
        [60]    float   -11.2166443 0x0000A9DC@Data 
        [61]    float   -11.1151695 0x0000A9DE@Data 
        [62]    float   -11.0123882 0x0000A9E0@Data 
        [63]    float   -10.9098005 0x0000A9E2@Data 
        [64]    float   -10.8091011 0x0000A9E4@Data 
        [65]    float   -10.7056608 0x0000A9E6@Data 
        [66]    float   -10.6053677 0x0000A9E8@Data 
        [67]    float   -10.4989262 0x0000A9EA@Data 
        [68]    float   -10.3934803 0x0000A9EC@Data 
        [69]    float   -10.2887907 0x0000A9EE@Data 
        [70]    float   -10.1724911 0x0000A9F0@Data 
        [71]    float   -10.0519409 0x0000A9F2@Data 
        [72]    float   -9.93203163 0x0000A9F4@Data 
        [73]    float   -9.8078804  0x0000A9F6@Data 
        [74]    float   -9.67338562 0x0000A9F8@Data 
        [75]    float   -9.53700733 0x0000A9FA@Data 
        [76]    float   -9.39493942 0x0000A9FC@Data 
        [77]    float   -9.25238609 0x0000A9FE@Data 
        [78]    float   -9.09961796 0x0000AA00@Data 
        [79]    float   -8.92718697 0x0000AA02@Data 
        [80]    float   -8.75035763 0x0000AA04@Data 
        [81]    float   -8.55232716 0x0000AA06@Data 
        [82]    float   -8.34014893 0x0000AA08@Data 
        [83]    float   -8.10224628 0x0000AA0A@Data 
        [84]    float   -7.83410263 0x0000AA0C@Data 
        [85]    float   -7.53796959 0x0000AA0E@Data 
        [86]    float   -7.19063234 0x0000AA10@Data 
        [87]    float   -6.80311584 0x0000AA12@Data 
        [88]    float   -6.26976204 0x0000AA14@Data 
        [89]    float   -5.63396883 0x0000AA16@Data 
        [90]    float   -4.68489504 0x0000AA18@Data 
        [91]    float   -3.27892733 0x0000AA1A@Data 
        [92]    float   -1.80067527 0x0000AA1C@Data 
        [93]    float   -0.846980214    0x0000AA1E@Data 
    '''

    ''' Select a tag
    '''
    tag = None
    # tag_selected = 'Mini6PhaseIPMInverter-528-0927-phaseB-80V[294-Points]-1A'
    # tag_selected ='Mini6PhaseIPMInverter-528-0927-phaseB-80V[294-Points]-1A-[ADC offset-compensated]'
    tag_selected = 'SiC-529-0957-phase-B-80V-[ADC-gain-Tuned]-3A'
    tag_selected = 'SiC-602-1647-phase-B-180V-[ADC-gain-Tuned]-3A'

    phase_current_data, phase_voltage_data = dict(), dict()
    phase_current_data[tag_selected], \
    phase_voltage_data[tag_selected] = synthesize_ccs_expression_phaseCurrent(ccs_expressions[tag_selected])

    ''' Remove offset so that zero current maps to zero voltage
    '''
    if tag_selected=='Mini6PhaseIPMInverter-528-0927-phaseB-80V[294-Points]-1A-[ADC offset-compensated]':
        phase_current_data[tag_selected] += -0.02325 + 0.0012 - 0.0001526

        # phase_current_data[tag_selected] = phase_current_data[tag_selected][-100:]
        # phase_voltage_data[tag_selected] = phase_voltage_data[tag_selected][-100:]

        # for el in phase_current_data[tag_selected]:
        #     print('%g' % (el), end=', ')
        # print()
        # print()
        # for el in phase_voltage_data[tag_selected]:
        #     print('%g' % (el), end=', ')
        # quit()

    print(len(phase_current_data[tag_selected]))
    print(len(phase_voltage_data[tag_selected]))

    ''' 描点、拟合、画图
    '''
    a1, a2, a3 = analyze_ui_curve(tag_selected)
    print('End value for distorted voltage is:', wt_sigmoid(100, 0, a2, a3))

    print('-------------phase quantities output ')
    # print(phase_current_data[tag_selected])
    # print(phase_voltage_data[tag_selected])

    plt.show()






    ''' 月飞：逆变器非线性的标幺化的可行性验证需要三个点。
    '''
    if False:
        # end value is 0.5*a2
        DistortedVoltage_Udc20V  =  20, 1.1525295223674838
        DistortedVoltage_Udc80V  =  80, 3.8942857833854116 # from ui_curve_v2.py
        DistortedVoltage_Udc180V = 180, 6.742338018176723

        plt.figure()
        plt.plot( DistortedVoltage_Udc20V[0],  DistortedVoltage_Udc20V[1], 'o')
        plt.plot( DistortedVoltage_Udc80V[0],  DistortedVoltage_Udc80V[1], 'o')
        plt.plot(DistortedVoltage_Udc180V[0], DistortedVoltage_Udc180V[1], 'o')
        plt.show()

        deadtime_voltage_per_dc_bus_voltage = (6.742338018176723 - 3.8942857833854116) / (180 - 80); print(deadtime_voltage_per_dc_bus_voltage)
        deadtime_voltage_per_dc_bus_voltage = (3.8942857833854116 - 1.1525295223674838) / (80 - 20); print(deadtime_voltage_per_dc_bus_voltage)
        deadtime_voltage_per_dc_bus_voltage = (6.742338018176723 - 1.1525295223674838) / (180 - 20); print(deadtime_voltage_per_dc_bus_voltage)

