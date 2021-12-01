from eagers.setup.load_network import load_network
from eagers.setup.update_qpform_all import update_qpform_all
from eagers.setup.add_buildings import add_buildings
from eagers.basic.build_time_vector import build_time_vector
from eagers.basic.check_ac_dc import check_ac_dc
from eagers.setup.load_matrices import load_matrices

def preload(plant,test_data,options,online=None):
    preload= {}
    time = build_time_vector(options['start_date'], options, to_timedelta=True)
    dt = [(time[i+1] - time[i]).total_seconds()/3600 for i in range(len(time)-1)]
    subnet = load_network(plant['network'], plant['generator'], plant['building'])
    gen_qp_form =  update_qpform_all(plant['generator'], subnet, test_data, 1)
    building_qp_form = add_buildings(plant['building'], subnet, gen_qp_form)
    gen_qp_form = check_ac_dc(gen_qp_form, building_qp_form, test_data)
    b_names = [plant['building'][i]['name'] for i in range(len(plant['building']))]
    if 'fluid_loop' not in plant:
        plant['fluid_loop'] = []
    if 'market' not in plant:
        plant['market'] = []
    op_mat_a = load_matrices(gen_qp_form, b_names, plant['fluid_loop'], plant['market'], subnet, options, 'a', dt)
    op_mat_b = load_matrices(gen_qp_form, b_names, plant['fluid_loop'], plant['market'], subnet, options, 'b', dt)
    one_step = load_matrices(gen_qp_form, b_names, plant['fluid_loop'], plant['market'], subnet, options, 'b', None)
    if online is None and options['method'] == 'Control':
        a = {}
        a['horizon'] = options['resolution'] #the horizon is the resolution
        a['resolution'] = options['t_opt']/3600 #the resolution is the frequency of Topt
        a['tspacing'] = 'constant'
        
        online_time = build_time_vector(options['start_date'], a, to_timedelta=True), ## set up dt vector of time interval length
        ns = len(online_time)
        pre_time = [0]
        pre_time.extend([online_time[i+1] for i in range(ns-1)])
        dt2 = [online_time[i] - pre_time[i] for i in range(ns)]
        online = [[] for i in range(ns)]
        for t in range(ns):
            online[t] = load_matrices(gen_qp_form, b_names, plant['fluid_loop'], plant['market'], subnet, options, 'b', [dt2[i] for i in range(t, ns)]) #build the matrix for the onlineOptimLoop using FitB:
    else:
        online = []

    preload['building_qp_form'] = building_qp_form
    preload['gen_qp_form'] = gen_qp_form
    preload['num_steps'] = 0
    preload['one_step'] = one_step
    preload['online'] = online
    preload['op_mat_a'] = op_mat_a
    preload['op_mat_b'] = op_mat_b
    preload['subnet'] = subnet
    return preload