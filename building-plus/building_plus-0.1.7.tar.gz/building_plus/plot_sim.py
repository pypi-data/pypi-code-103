'''
Plot as validation against energy plus run
'''
import csv
import matplotlib.pyplot as plt 
from multiprocessing import Process

def plot_sim(facility,T_zone,Q_transfer,building,date,filename):
    dr=csv.DictReader(open(filename,'r'))
    e_plus = {}
    for row in dr:
        if len(list(e_plus.keys())) == 0:
            e_plus={k.rstrip():[] for k in row}
        for k, v in row.items():
            if k != 'Date/Time':
                e_plus[k.rstrip()].append(float(v))
    e_plus['Date/Time'] = building['sim_date'][1:]
    EP = ['Electricity:Facility [J](Hourly)','Heating:Gas [J](Hourly)','Heating:Electricity [J](Hourly)','WaterSystems:Gas [J](Hourly)','Cooling:Electricity [J](Hourly)','HeatRejection:Electricity [J](Hourly)','Fans:Electricity [J](Hourly)','Pumps:Electricity [J](Hourly)']
    EAG = ['net_elec','heat_gas','heat_elec','water_gas','cool_elec','tower_elec','fan_elec','pumps']
    label_x = ['electric ---total (kw)','heating --- gas (kW)','heating --- electric (kW)','water system --- gas (kW)','cooling (kW)','cooling tower fans (kW)','HVAC fans (kW)','water pumps --- (kW)']

    i1 = 0
    while building['sim_date'][i1+1]<date[0]:
        i1+=1
    i2 = i1+0
    while building['sim_date'][i2+1]<=date[-1]:
        i2+=1
    model_fit = {}
    for j in range(len(EP)):
        if EP[j] in e_plus and any([e_plus[EP[j]][i]>0 for i in range(i1,i2)]):
            x = [e_plus[EP[j]][i]/3600/1000 for i in range(i1,i2)]
            y = [i/1000 for i in facility[EAG[j]]]
            m_x = sum(x)/len(x)
            m_y = sum(y)/len(y)
            if sum([(x[i]-m_x)**2 for i in range(len(x))]) == 0:
                COD = 0
            else:
                COD = 1 - sum([(y[i] - x[i])**2 for i in range(len(x))])/sum([(x[i]-m_x)**2 for i in range(len(x))]) #Coefficient of determination
            if sum([(y[i]-m_y)**2 for i in range(len(x))]) == 0:
                COD_B = 0
            else: 
                COD_B = 1 - sum([(y[i] - x[i])**2 for i in range(len(x))])/sum([(y[i]-m_y)**2 for i in range(len(x))])
            if (sum([(x[i]-m_x)**2 for i in range(len(x))])*sum([(y[i]-m_y)**2 for i in range(len(x))])) == 0:
                pearson = 0
            else:
                pearson = sum([(x[i]-m_x)*(y[i] - m_y) for i in range(len(x))])**2/(sum([(x[i]-m_x)**2 for i in range(len(x))])*sum([(y[i]-m_y)**2 for i in range(len(x))])) #Pearson product moment correlation coefficient
            model_fit[EAG[j]] = {}
            model_fit[EAG[j]]['Pearson'] = pearson
            model_fit[EAG[j]]['COD'] = max(COD,COD_B)
            model_fit[EAG[j]]['total_energy_percent'] = sum(y)/sum(x)
            p = Process(target=plot_fig, args=(j,date,x,y,label_x[j]))
            p.start()

    p_n = len(EP)+2
    plot_z = [i for i in range(len(building['zones']['name']))]
    for p in range(len(plot_z)):
        name = building['zones']['name'][plot_z[p]].upper()
        field = 'Cooling:EnergyTransfer:Zone:' + name +' [J](Hourly)'
        if len(field)>63:
            field = field[:63]
        if field in e_plus:
            x = [e_plus[field][i]/3600/1000 for i in range(i1,i2)]
            y = [max(0,-i[plot_z[p]]/1000) for i in Q_transfer]
            y_lab = building['zones']['name'][plot_z[p]] + ' zone cooling (kW)'
            p = Process(target=plot_fig, args=(p_n+p,date,x,y,y_lab))
            p.start()
        else: 
            print('Need to add   Output:Meter,Cooling:EnergyTransfer:Zone:DINING,hourly; for all zone names to the .idf file and re-generate the result file then save in building_plus_user folder.')

    p_n = p_n + len(plot_z)
    for p in range(len(plot_z)):
        name = building['zones']['name'][plot_z[p]].upper()
        field = 'Heating:EnergyTransfer:Zone:'+ name + ' [J](Hourly)'
        if len(field)>63:
            field = field[:63]
        if field in e_plus:
            x = [e_plus[field][i]/3600/1000 for i in range(i1,i2)]
            y = [max(0,i[plot_z[p]]/1000) for i in Q_transfer]
            y_lab = building['zones']['name'][plot_z[p]] + ' zone heating (kW)'
            p = Process(target=plot_fig, args=(p_n+p,date,x,y,y_lab))
            p.start()
        else: 
            print('Need to add   Output:Meter,Heating:EnergyTransfer:Zone:DINING,hourly; for all zone names  to the .idf file and re-generate the result file then save in building_plus_user folder.')

    p_n = p_n + len(plot_z)
    for p in range(len(plot_z)):
        name = building['zones']['name'][plot_z[p]].upper()
        field = name + ':Zone Air Temperature [C](Hourly)'
        if len(field)>63:
            field = field[:63]
        if field in e_plus:
            x = [e_plus[field][i] for i in range(i1,i2)]
            y = [T_zone[i+1][plot_z[p]] for i in range(len(date))]
            y_lab = building['zones']['name'][plot_z[p]] + ' zone temperature (C)'
            p = Process(target=plot_fig, args=(p_n+p,date,x,y,y_lab))
            p.start()
        else: 
            print('Need to add   Output:Variable,*,Zone Air Temperature,hourly;  to the .idf file and re-generate the result file then save in building_plus_user folder.')

def plot_fig(p,d,x,y,y_lab):
    m_x = sum(x)/len(x)
    m_y = sum(y)/len(y)
    if sum([(x[i]-m_x)**2 for i in range(len(x))]) == 0:
        COD_A = 0
    else:
        COD_A = 1 - sum([(y[i] - x[i])**2 for i in range(len(x))])/sum([(x[i]-m_x)**2 for i in range(len(x))]) #Coefficient of determination
    if sum([(y[i]-m_y)**2 for i in range(len(x))]) == 0:
        COD_B = 0
    else: 
        COD_B = 1 - sum([(y[i] - x[i])**2 for i in range(len(x))])/sum([(y[i]-m_y)**2 for i in range(len(x))])
    COD = max(COD_A,COD_B)
    plt.figure(p)
    plt.plot(d,y, label = 'WSU')
    plt.plot(d,x,label = 'EnergyPlus')
    plt.xlabel('Day of year')
    plt.ylabel(y_lab)
    plt.annotate('r^2 value :'+str(COD),xy = (x[0],y[0]),xytext = [.05, .95],xycoords= 'figure fraction')
    plt.annotate('NF value :'+str(sum(y)/sum(x)),xy = (x[0],y[0]),xytext = [.55, .95],xycoords= 'figure fraction')
    plt.ioff()
    plt.draw()
    plt.show()

