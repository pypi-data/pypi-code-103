import datetime

from eagers.basic.build_time_vector import build_time_vector
from eagers.config.simulation import DEFAULT_INITIAL_SOC
from eagers.setup.load_matrices import load_matrices
from eagers.setup.automatic_ic import automatic_ic
from eagers.update.update_data import update_data
from eagers.setup.initialize_observer import initialize_observer, observer_component_ic
from eagers.solver.dispatch_loop import dispatch_loop


def water_year_forecast(gen,buildings,fluid_loop,observer,all_data_nodes,names,zones,pl,subnet,options,date,test_data):
    hydroforecast = False
    for i in range(len(gen)):
        if gen[i]['type']=='HydroStorage':
            hydroforecast = True
    if 'hydro_wy_timestamp' in observer and observer['hydro_wy_timestamp'] !=None:
        if observer['hydro_wy_timestamp'][-1]>=date[-1]:
            hydroforecast = False

    if hydroforecast:
        #first create the yearly dispatch data 
        # i.e. run Dispatch loop with updated information
        #these will be used for set points in the actual dispatch
        date_now = date[0]
        options['horizon'] = 364*24 #Yearly Horizon
        options['resolution'] = 7*24 #Week Resolution
        if date_now.month()<10 and date[-1].month()>=10:
            year = date_now.year()-1
            dy1 = datetime.datetime(date_now.year(),10,1,0,0,0)
            options['horizon'] = (53+round((date[-1]-dy1).days()/7+.5))*7*24 #ensure that water year forecast goes a week beyond the final date
        elif date_now.month()<10:
            year = date_now.year()-1
        else:
            year = date_now.year()
        d1 = datetime.datetime(year, 10, 1, 1, 0, 0) 
        date = build_time_vector(d1,options, to_timedelta=True)
        dt = [(date[t+1] - date[t]).seconds/3600 for t in range(len(date)-1)]
        b_names = [buildings[i]['name'] for i in range(len(buildings))]
        op_mat_a = load_matrices(gen,b_names,fluid_loop,observer['market'],subnet,options,'A',dt) #build quadratic programming matrices for FitA
        op_mat_b = load_matrices(gen,b_names,fluid_loop,observer['market'],subnet,options,'B',dt) #build quadratic programming matrices for FitB
        one_step = load_matrices(gen,b_names,fluid_loop,observer['market'],subnet,options,'B',[]) #build quadratic programming matrices for single time step

        if observer['hydro_wy_timestamp'] == None:
            wy_observer = initialize_observer(gen,subnet,fluid_loop,observer['market'],all_data_nodes, names, zones, pl,test_data,observer,date_now)
            data_t0 = update_data(gen,buildings,subnet, date[0],options,test_data,wy_observer,'perfect')
            ic, _ = automatic_ic(gen,fluid_loop,observer['market'],subnet,one_step,options,data_t0) # set the initial conditions 
            wy_observer = observer_component_ic(gen,ic,DEFAULT_INITIAL_SOC,names,wy_observer)
        else:
            wy_observer = observer
        
        if date[-1]<=test_data['hydro']['timestamp'][-1]:
            forecast = update_data(gen,buildings,subnet, date, options, test_data, observer,options['forecast'])
            solution,_ = dispatch_loop(gen,wy_observer,subnet,names,op_mat_a,op_mat_b,one_step,options,date,forecast,[])
            hydro_soc_init = [0 for n in range(len(subnet['hydro']['nodes']))]
            for n in range(len(subnet['hydro']['nodes'])):
                i = subnet['hydro']['equipment'][n]
                if gen[i]['type']=='HydroStorage':
                    hydro_soc_init[n] = observer.stor_state[i]
            solution['hydro_soc'] = [solution['hydro_soc'][n].insert(0,hydro_soc_init) for n in range(len(solution['hydro_soc']))]
            print('Water Year Forecast Completed for ' + str(year)+':',str(year+1))
            if observer.hydro_wy_timestamp==None:
                t = 0
                while solution['timestamp'][t+1]<date_now:
                    t+=1
                r = (solution['timestamp'][t+1]-date_now)/(solution['timestamp'][t+1]-solution['timestamp'][t])
                for i in range(len(gen)):
                    if gen[i]['type'] =='HydroStorage':
                        n = gen[i]['hydro']['subnet_node'] #dam #
                        observer['stor_state'][i] = r*solution['hydro_soc'][t][n] + (1-r)*solution['hydro_soc'][t+1][n]
            observer['hydro_wy_timestamp'] = solution['timestamp'] 
            observer['hydro_wy_soc'] = solution['hydro_soc']
    return observer
