"""
Defines function import_idf, which imports IDF data to a Building
object.
"""

import datetime as dt

import numpy as np
from scipy.sparse import spdiags
from scipy.sparse import coo_matrix

from building_plus.config.building import IDF_FIELDS


def import_idf(filepath):
    """Import IDF data from given file. Returns Building instance with
    properties filled from IDF file.

    Positional arguments:
    filepath - (pathlib.Path) Path to IDF file.
    """

    # Get object data.
    objects, ground_temps, convection = read_objects(filepath)

    # Instantiate objects to be passed to Building constructor.
    name = objects['Building'][0]['name']  # Assumes one building.
    site = load_object(['Building'], objects,0,'') 
    site = site[name]
    site['ground_reflect'] = 0
    rp = load_object(['RunPeriod'], objects,0,'')
    sim_date = import_date(rp[objects['RunPeriod'][0]['name']])
    location = load_object(['Site:Location'], objects,0,'array') 
    schedule = import_schedules(objects)
    holidays = load_object(['RunPeriodControl:SpecialDays'],objects,0,'')
    material = load_object(['Material','Material:NoMass'], objects,0,'')  

    window_material = load_object(['WindowMaterial:SimpleGlazingSystem','WindowMaterial:Glazing','WindowMaterial:Gas'], objects,0,'') 

    construction, window_construction = read_construction(objects['Construction'],material,window_material,4) 
    surfaces = import_idf_surfaces(objects,construction)
    windows, doors= import_windows_doors(objects,window_construction)
    window_frames = load_object(['WindowProperty:FrameAndDivider'],objects,0,'')
    zones = load_object(['Zone'],objects,0,'array')

    zones, surfaces, windows, ctf = zone_geometry(zones,surfaces,windows)
    infiltration = import_infiltration(objects,zones)
    mixing = import_mixing(objects,zones,schedule)
    occupancy, zones = import_occupancy(objects,zones)
    lighting_internal = import_lighting(objects,zones)
    plug_load = import_equipment(objects,zones,'ElectricEquipment')
    gas_load = import_equipment(objects,zones,'GasEquipment')
    exterior = load_object(['Exterior:Lights','Exterior:FuelEquipment'], objects,0,'') 
    cases = load_object(['Refrigeration:Case'], objects,0,'') 
    walk_ins = {}
    racks = load_object(['Refrigeration:CompressorRack'], objects,0,'') 
    racks = rack_cases(racks,cases,objects)
    water_use = load_object(['WaterUse:Equipment'], objects,0,'') 
    water_use_con = load_object(['WaterUse:Connections'], objects,0,'') 
    for i in water_use_con:
        for j in water_use_con[i]:
            if j!='type':
                water_use[i][j] = water_use_con[i][j]

    hvac,e_list,zones['air_loop'],zones['air_plenum'] = import_hvac(objects,zones['name'],schedule)
    air_demand_nodes, air_demand_equip = setup_nodes(hvac['components'],hvac['loop'],'d')
    air_supply_nodes,air_supply_equip = setup_nodes(hvac['components'],hvac['loop'],'s')
    air_supply_equip['branch_order'] = [[] for i in range(len(air_supply_equip['name']))]
    for j in range(len(hvac['loop']['name'])):
        components = []
        components.extend(*[hvac['branches']['component_name'][i] for i, x in enumerate(hvac['branches']['loop']) if x==j])
        for j in range(len(components)):
            k = air_supply_equip['name'].index(components[j])
            air_supply_equip['branch_order'][k] = j
    plant_loop, components = import_plant(objects)
    plant_demand_nodes, plant_demand_equip = setup_nodes(components,plant_loop,'d')
    plant_supply_nodes,plant_supply_equip = setup_nodes(components,plant_loop,'s')


    pump = load_object(['Pump:VariableSpeed','Pump:ConstantSpeed'], objects,0,'') 
    chiller = load_object(['Chiller:Electric:EIR','Chiller:Electric:ReformulatedEIR'], objects,0,'') 
    boiler = load_object(['Boiler:HotWater'], objects,0,'') 
    humidifiers = load_object(['Humidifier:Steam:Electric'], objects,0,'') 
    unitary_heat_cool = load_object(['AirLoopHVAC:UnitaryHeatCool'], objects,0,'') 
    for i in unitary_heat_cool:
        unitary_heat_cool[i]['loop'] = hvac['loop']['supply_outlet'].index(unitary_heat_cool[i]['outlet']) 
    cooling_tower = load_object(['CoolingTower:SingleSpeed','CoolingTower:TwoSpeed','CoolingTower:VariableSpeed:Merkel'], objects,0,'') 
    water_heater = load_object(['WaterHeater:Mixed'], objects,0,'') 
    controller = load_object(['Controller:WaterCoil'], objects,0,'') 
    manager = load_object(['SetpointManager:Scheduled','SetpointManager:MixedAir','SetpointManager:SingleZone:Reheat','SetpointManager:SingleZone:Humidity:Minimum','SetpointManager:SingleZone:Humidity:Maximum','SetpointManager:FollowOutdoorAirTemperature','SetpointManager:OutdoorAirReset'], objects,0,'array') 
    n_list = load_object(['NodeList'],objects,0,'')
    for i in range(len(manager['name'])):
        try:
            manager['node'][i] = n_list['node'][n_list['name'].index(manager['node'][i])]
        except:
            # manager is not a list.
            pass
    zone_controls = load_object(['ZoneControl:Thermostat','ZoneControl:Humidistat'], objects,2,'')
    thermostat = load_object(['ThermostatSetpoint:SingleHeating','ThermostatSetpoint:SingleCooling','ThermostatSetpoint:SingleHeatingOrCooling','ThermostatSetpoint:DualSetpoint'], objects,0,'')
    outdoor_air = import_outdoor_air(objects)
    setpoints = load_object(['Sizing:Zone'],objects,0,'array')
    setpoints['zone'] = [zones['name'].index(setpoints['name'][i]) for i in range(len(setpoints['name']))]    
    setpoints['outdoor_flow_method'] = [outdoor_air['method'][outdoor_air['name'].index(setpoints['outdoor_air_object'][i])] for i in range(len(setpoints['name']))]
    setpoints['outdoor_flow_value'] = [outdoor_air['value'][outdoor_air['name'].index(setpoints['outdoor_air_object'][i])]  for i in range(len(setpoints['name']))]
    unitary_sys = load_object(['ZoneHVAC:UnitHeater','ZoneHVAC:PackagedTerminalAirConditioner','ZoneHVAC:FourPipeFanCoil'],objects,0,'')
    if len(unitary_sys)>0:
        for i in unitary_sys:
            k = e_list['e_name'].index(i)
            unitary_sys[i]['zone'] = e_list['zone'][k]
            for j in range(len(e_list['name'])):
                if (e_list['name'][j] == e_list['name'][k] and j!=k and e_list['e_type'][j]=='airterminal:singleduct:uncontrolled'):
                    unitary_sys[i]['terminal'] = hvac['terminals']['name'].index(e_list['e_name'][j])
    fans = load_object(['Fan:ConstantVolume','Fan:ZoneExhaust','Fan:VariableVolume','Fan:OnOff'],objects,0,'')
    for x in fans:
        try:
            k = e_list['e_name'].index(x)
            fans[x]['exhaust'] = True
            fans[x]['exhaust_zone'] = e_list['zone'][k]
        except ValueError:
            fans[x]['exhaust'] = False
            fans[x]['exhaust_zone'] = []

    curves = load_object(['Curve:Quadratic','Curve:Cubic','Curve:Biquadratic','Curve:Bicubic','Curve:ChillerPartLoadWithLift'],objects,0,'')
    coils_cooling = load_object(['Coil:Cooling:DX:TwoSpeed','Coil:Cooling:DX:SingleSpeed','Coil:Cooling:Water','Coil:Cooling:Water:DetailedGeometry'],objects,0,'')
    coils_heating = load_object(['Coil:Heating:Fuel','Coil:Heating:Water','Coil:Heating:Electric'],objects,0,'')
    for x in coils_heating:
        coils_heating[x]['rated_air_flow']=0
    water_main_temperature = load_object(['Site:WaterMainsTemperature'],objects,0,'array')
    if len(water_main_temperature['name'])>0:
        water_main_temperature['method'] = water_main_temperature['name']
    impact_factor = load_object(['EnvironmentalImpactFactors'],objects,0,'array')
    if len(impact_factor['name'])>0:
        impact_factor['district_heat_efficiency'] = impact_factor['name']
    coil_system = load_object(['CoilSystem:Cooling:DX'],objects,0,'')
    if len(coil_system)>0:
        for x in coil_system:
            try:
                i = hvac['components']['name'].index(x)
                hvac['components']['name'][i] = coil_system[x]['coil_name']
            except ValueError:
                pass
            try:
                i = air_supply_equip['name'].index(x)
                air_supply_equip['name'][i] = coil_system[x]['coil_name']
            except ValueError:
                pass

    # Return dictionary of Building data.
    return dict(
        name=name,
        site=site,
        location = location,
        sim_date = sim_date,
        holidays = holidays,
        convection=convection,
        schedule=schedule,
        material=material,
        surfaces = surfaces,
        windows=windows,
        doors=doors,
        window_frames=window_frames,
        zones = zones,
        ctf = ctf,
        infiltration = infiltration,
        mixing = mixing,
        occupancy = occupancy,
        lighting_internal = lighting_internal,
        plug_load = plug_load,
        gas_load = gas_load,
        exterior = exterior,
        cases = cases,
        racks = racks,
        walk_ins = walk_ins,
        water_use= water_use,
        hvac = hvac,
        air_demand_nodes = air_demand_nodes,
        air_demand_equip = air_demand_equip,
        air_supply_nodes = air_supply_nodes,
        air_supply_equip = air_supply_equip,
        plant_loop = plant_loop,
        plant_demand_nodes = plant_demand_nodes, 
        plant_demand_equip = plant_demand_equip,
        plant_supply_nodes = plant_supply_nodes,
        plant_supply_equip = plant_supply_equip,
        pump = pump,
        chiller = chiller,
        boiler = boiler,
        humidifiers = humidifiers,
        unitary_heat_cool= unitary_heat_cool,
        cooling_tower=cooling_tower,
        water_heater=water_heater,
        controller=controller,
        manager = manager,
        zone_controls=zone_controls,
        thermostat=thermostat,
        setpoints=setpoints,
        unitary_sys=unitary_sys,
        fans=fans,
        curves=curves,
        coils_cooling=coils_cooling,
        coils_heating = coils_heating,
        water_main_temperature=water_main_temperature,
        impact_factor=impact_factor,
        ground_temperatures = ground_temps,
    )


def load_object(keys,all_obj,repeat,meth):
    #load objects in list of keys into a single dictionary, s
    s = {}
    if meth=='array' or meth=='extend':
        s['name'] = []
        s['type']= []
    for key in keys:
        try:
            k_obj = all_obj[key]            
            f = IDF_FIELDS[key] 
            col = key.find(':')
            if meth=='array' or meth=='extend':
                for i in f:
                    if not i in s:
                        s[i] = [None for x in range(len(s['name']))]
                for x in range(len(k_obj)): 
                    value = k_obj[x]['value']
                    for i in range(len(f)):
                        if i>=(len(f)-repeat):
                            nv=[read_num(value[x]) for x in range(i,len(value),repeat)]
                        elif i<len(value):
                            nv=read_num(value[i])
                        if meth=='array':
                            s[f[i]].append(nv)
                        else:
                            s[f[i]].extend(nv)
                    if meth=='array':
                        s['name'].append(k_obj[x]['name'])
                        s['type'].append(key[col+1:])
                    else:
                        s['name'].extend([k_obj[x]['name'] for i in range(len(nv))])
                        s['type'].extend([key[col+1:] for i in range(len(nv))])
            else:
                for x in range(len(k_obj)):  
                    value = k_obj[x]['value']
                    s[k_obj[x]['name']] ={}
                    s[k_obj[x]['name']]['type']= key[col+1:]
                    for i in range(len(f)):
                        if i>=(len(f)-repeat):
                            s[k_obj[x]['name']][f[i]] = [read_num(value[x]) for x in range(i,len(value),repeat)]
                        elif i<len(value):
                            s[k_obj[x]['name']][f[i]] = read_num(value[i])
        except KeyError:
            pass
    return s


def read_objects(filepath):
    """Parses the given text file into a dictionary with the relevant
    data.

    Note: Only exception to parsing pattern is ground temperatures
    and convection algorithm (single line objects).
    """
    # Start with blank dict constructed from expected IDF object types.
    # Each new object will be appended to a list of distinct object
    # types.
    objects = {}
    convection ={}
    ground_temps = []

    # Read lines of file.
    with open(filepath, 'r') as f:
        # line = next(f)
        while True:
            try:
                line = next(f).lstrip()
                com = line.find(',')
                if com>=0 and line.find('!')<0:
                #start of a new object
                    obj_type = line[0:com]
                    name = (next(f).lstrip()).lower()
                    com = name.find(',')
                    if com<0:
                        com = name.find(';')
                    if com<0: #could be ground temps or surface convection
                        if obj_type.find('Site:GroundTemperature')>=0:
                            val = line[line.find(',')+1:-2].split(',' or ';')
                            ground_temps = [float(val[x]) for x in range(len(val))]
                        elif obj_type=='SurfaceConvectionAlgorithm:Inside':
                                com = [pos for pos, char in enumerate(line) if (char == ',' or char == ';')]
                                convection['interior'] = line[com[0]+1:com[1]]
                        elif obj_type=='SurfaceConvectionAlgorithm:Outside':
                                com = [pos for pos, char in enumerate(line) if (char == ',' or char == ';')]
                                convection['exterior'] = line[com[0]+1:com[1]]
                    else:
                        name = name[0:com]
                        line = next(f).lstrip()
                        exc = line.find('!')
                        value = []
                        parameter = []
                        while exc>0:
                            com = [pos for pos, char in enumerate(line[0:exc]) if (char == ',' or char == ';')]
                            value.append(line[0:com[-1]])
                            parameter.append(line[exc+1:-1])
                            line = next(f).lstrip()
                            exc = line.find('!')
                        # Create new object dict.
                        new_obj = dict(name=name,value=value,parameter=parameter,)
                        try:
                            objects[obj_type].append(new_obj)# Append the new object to the list of its type.
                        except KeyError:
                            # Tried appending to nonexistent dict entry, which raised an
                            # Exception (specifically, a KeyError).
                            # Instead of appending, make a new list.
                            objects[obj_type] = [new_obj]
            except StopIteration:
                break

    return objects, ground_temps, convection

def read_num(n):
    """Convert to an integer or float if possible."""
    try:
        n = int(n)
    except ValueError:
        try:
            n = float(n)
        except ValueError:
            if isinstance(n, str):
                if n:
                    return n.lower()
                else:
                    return None
    return n

def import_date(rp):
    '''convert simulation period (month/day) and start day of week into a date vector'''
    if rp['day']=='monday':
        y = 2018
    elif rp['day']=='sunday':
        y = 2017
    elif rp['day']=='saturday':
        y = 2011
    elif rp['day']=='friday':
        y = 2010
    elif rp['day']=='thursday':
        y = 2015
    elif rp['day']=='wednesday':
        y = 2014
    elif rp['day']=='tuesday':
        y = 2013
    d1 = dt.datetime(y,rp['m1'],rp['d1'])
    d2 = dt.datetime(y,rp['m2'],rp['d2'])
    hours = ((d2-d1).days+1)*24+1
    date = [d1 + dt.timedelta(hours=i) for i in range(hours)]
    return date


def import_schedules(objects):
    sched = {}
    for x in objects['Schedule:Compact']:
        name = x['name'].lstrip()
        values = x['value']
        type = values[0]
        seasons = []
        interpolate = []
        season = -1
        ramp = 1e-4
        profile ={}
        i = 1
        while i <len(values):
            if values[i][:7]=='Through':
                bksls = values[i].find('/')
                month = int(values[i][bksls-2:bksls])
                day = int(values[i][bksls+1:])
                dy = [31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
                seasons.append(sum(dy[0:(month-1)])*24 + 24*day)
                season+=1
                interpolate.append(False)
                i+=1
            elif values[i][:3]=='For':
                day = values[i][4:].split()
                i+=1
                if values[i]=='Interpolate:No':
                    i+=1
                elif values[i]=='Interpolate:Yes':
                    interpolate[season] = True
                    i+=1
                time = [0.0]
                val = [0.0] 
                while i<len(values) and values[i][:5]=='Until':
                    sep = [pos for pos, char in enumerate(values[i]) if (char == ':' or char == ',')]
                    time.append(float(values[i][sep[0]+1:sep[1]])+float(values[i][sep[1]+1:sep[2]])/60)
                    val.append(float(values[i][sep[2]+1:]))
                    i+=1
                val[0]=val[1]
                new_day = dict(time=time,val=val,season=season)
                for x in day:
                    try:
                        profile[x].append(new_day)
                    except KeyError:
                        profile[x] = [new_day]

        sched[name] = dict(type=type,seasons=seasons,interpolate=interpolate,ramp=ramp,profile=profile)
    return sched


def read_construction(objects,materials,window_materials,i_nodes):
    def material_conductivity(materials,value,i_nodes):
        c_tot = 0
        r_tot = 0
        for mat in value:
            if 'thickness' in materials[mat]:
                try:
                    c_tot+= materials[mat]['density']*materials[mat]['specheat']*materials[mat]['thickness']
                    r_tot+= materials[mat]['thickness']/materials[mat]['conductivity']
                except TypeError:
                    pass
        c = [0.0]
        r = []
        dx = []
        for mat in value:
            if 'thickness' in materials[mat]:
                try:
                    c_l= materials[mat]['density']*materials[mat]['specheat']*materials[mat]['thickness']
                    r_l = materials[mat]['thickness']/materials[mat]['conductivity']
                    if r_l/r_tot<0.02 and len(r)>0: #don't create more nodes, lump in with portion of surface with greater resistance
                        c[-1] += c_l
                        r[-1] += r_l # K*m^2/W 
                    elif c_l/c_tot>0.04 and r_l/r_tot>=0.02:
                        if len(r) == len(c):
                            r[-1] += r_l/i_nodes
                            r.extend([r_l/i_nodes for x in range(1,i_nodes)])
                        else:
                            r.extend([r_l/i_nodes for x in range(i_nodes)])
                        dx.extend([materials[mat]['thickness']/i_nodes for x in range(i_nodes)])
                        c[-1] += 0.5*c_l/i_nodes
                        c.extend([c_l/i_nodes for x in range(i_nodes)])
                        c[-1] -= 0.5*c_l/i_nodes
                    else: #create a single node
                        c[-1] += 0.5*c_l
                        c.append(0.5*c_l)
                        r.append(r_l)
                        dx.append(materials[mat]['thickness'])
                except TypeError:
                    pass
            elif 'thermal_resistance' in materials[mat]:
                try:
                    if c_tot ==0:#air wall, find thickness that matches R and use that for capacitance
                        k_air = 0.0262 #W/m*K
                        rho_air = 1.204 #kg/m^3
                        cp_air = 1006 #Specific Heat {J/kg-K}
                        t = materials[mat]['thermal_resistance']*k_air #thickness in m
                        air_cap = t*rho_air*cp_air #capacitance in J/K*m^2
                        dx.append(materials[mat]['thermal_resistance']/k_air) #air equivelant, air = 0.0262 W/m*K
                        r.append(materials[mat]['thermal_resistance']) # K*m^2/W 
                        c[-1] += air_cap/2
                        c.append(air_cap/2)
                    else:  #no-mass layer lumped into previous node
                        if len(c)==1:
                            r = [materials[mat]['thermal_resistance']]
                        else:
                            r[-1] += materials[mat]['thermal_resistance']
                except TypeError:
                    print('error in material conductivity')
        k = [dx[x]/r[x] for x in range(len(dx))]
        return k,dx,c,r
    
    def absorptance(materials,value):
        #interior surface absoprtance
        sol = [materials[value[0]]['solar_absorptance']]
        therm = [materials[value[0]]['thermal_absorptance']]
        try:
            vis = [materials[value[0]]['visible_absorptance']]
        except KeyError:
            vis = sol
        #exterior surface absoprtance
        sol.append(materials[value[-1]]['solar_absorptance'])
        therm.append(materials[value[-1]]['thermal_absorptance'])
        try:
            vis.append(materials[value[-1]]['visible_absorptance'])
        except KeyError:
            vis = sol
        return  sol, therm, vis

    def glazing(mat,value):
        normal_transmittance = []
        emittance=[]
        normal_reflectance=[]
        thermal_conductivity=[]
        thickness=[]
        transmittance = []
        reflectance=[]
        gap_thickness=0
        for x in value:
            if mat[x]['type']=='Glazing':
                normal_transmittance.append(mat[x]['solar_transmittance'])
                emittance.extend([mat[x]['emittance_front'],mat[x]['emittance_back']])
                normal_reflectance.extend([mat[x]['reflectance_front'],mat[x]['reflectance_back']])
                thermal_conductivity.append(mat[x]['thermal_conductivity'])
                thickness.append(mat[x]['thickness'])
                if normal_transmittance[-1]>0.645:
                    transmittance = [0.0288, 1.460, -3.840, 3.355, -0.0015]
                    reflectance = [1.054, -2.532, 2.043, -0.563, 0.999]
                else:
                    transmittance = [0.599, -0.05725, -2.341, 2.813, -0.002]
                    reflectance = [3.225, -7.862, 6.513, -1.868, 0.997]
            elif mat[x]['type'].find('gas')>=0:
                gap_thickness = mat[x]['gap_thickness']
        window = dict(normal_transmittance=normal_transmittance,emittance=emittance,normal_reflectance=normal_reflectance,
                    thermal_conductivity=thermal_conductivity,thickness=thickness,transmittance=transmittance,
                    reflectance=reflectance,gap_thickness=gap_thickness)
        return window

    def simple_glazing(mat):
        #convert basic parameters to a single pane, see section 7.7, page 285 of reference manual
        solar_heat_gain = mat['solar_heat_gain']
        u_factor = mat['u_factor']
        visible_transmittance = mat['visible_transmittance']
        
        def transmit_reflect_coef(shgc,U):
            #Details in engineering reference pg 287 and http://gaia.lbl.gov/btech/papers/2804.pdf
            T = [[1.470E-02,1.486E+00,-3.852E+00,3.355E+00,-1.474E-03],
                [5.546E-01,3.563E-02,-2.416E+00,2.831E+00,-2.037E-03],
                [7.709E-01,-6.383E-01,-1.576E+00,2.448E+00,-2.042E-03],
                [3.462E-01,3.963E-01,-2.582E+00,2.845E+00,-2.804E-04],
                [2.883E+00,-5.873E+00,2.489E+00,1.510E+00,-2.577E-03],
                [3.025E+00,-6.366E+00,3.137E+00,1.213E+00,-1.367E-03],
                [3.229E+00,-6.844E+00,3.535E+00,1.088E+00,-2.891E-03],
                [3.334E+00,-7.131E+00,3.829E+00,9.766E-01,-2.952E-03],
                [3.146E+00,-6.855E+00,3.931E+00,7.860E-01,-2.934E-03],
                [3.744E+00,-8.836E+00,6.018E+00,8.407E-02,4.825E-04]]

            R = [[1.632E+01,-5.782E+01,7.924E+01,-5.008E+01,1.334E+01],
                [4.048E+01,-1.193E+02,1.348E+02,-7.097E+01,1.611E+01],
                [5.749E+01,-1.645E+02,1.780E+02,-8.875E+01,1.884E+01],
                [5.714E+00,-1.667E+01,1.863E+01,-9.756E+00,3.074E+00],
                [-5.488E-01,-6.498E+00,2.120E+01,-2.097E+01,7.814E+00],
                [4.290E+00,-1.267E+01,1.466E+01,-8.153E+00,2.871E+00],
                [2.174E+01,-6.444E+01,7.489E+01,-4.179E+01,1.062E+01],
                [4.341E+00,-1.280E+01,1.478E+01,-8.203E+00,2.879E+00],
                [4.136E+01,-1.178E+02,1.276E+02,-6.437E+01,1.426E+01],
                [4.490E+00,-1.266E+01,1.397E+01,-7.501E+00,2.693E+00]] 

            
            T_fghi = [.25*T[5][i] + .25*T[6][i] + .25*T[7][i] + .25*T[8][i] for i in range(5)]
            R_fghi = [.25*R[5][i] + .25*R[6][i] + .25*R[7][i] + .25*R[8][i] for i in range(5)]
            T_bdcd = [.25*T[1][i] + .25*T[2][i] + .5*T[3][i] for i in range(5)]
            R_bdcd = [.25*R[1][i] + .25*R[2][i] + .5*R[3][i] for i in range(5)]
            T_fh = [0.5*T[5][i] + 0.5*T[7][i] for i in range(5)]
            R_fh = [0.5*R[5][i] + 0.5*R[7][i] for i in range(5)]
            if shgc>.65: 
                if U>4.54:
                    transmittance = T[0]
                    reflectance = R[0]
                elif U>3.41:
                    a = (U-3.41)/1.13
                    transmittance = [a*T[0][i] + (1-a)*T[4][i] for i in range(5)]    
                    reflectance = [a*R[0][i] + (1-a)*R[4][i] for i in range(5)]
                else:
                    transmittance = T[4]
                    reflectance = R[4]       
            elif shgc>.6:
                b = (shgc-.6)/.05
                if U>4.54:
                    transmittance = [b*T[0][i] + (1-b)*T_bdcd[i] for i in range(5)]
                    reflectance = [b*R[0][i] + (1-b)*R_bdcd[i] for i in range(5)] 
                elif U>3.41:
                    a = (U-3.41)/1.13
                    transmittance = [a*(b*T[0][i] + (1-b)*T_bdcd[i]) + (1-a)*T[4][i] for i in range(5)]
                    reflectance = [a*(R[0][i] + (1-b)*R_bdcd[i]) + (1-a)*R[4][i] for i in range(5)]
                else:
                    transmittance = T[4]
                    reflectance = R[4]
            elif shgc>.55:
                if U>4.54:
                    transmittance = T_bdcd  
                    reflectance = R_bdcd 
                elif U>3.41:
                    a = (U-3.41)/1.13
                    transmittance = [a*T_bdcd[i] + (1-a)*T[4][i] for i in range(5)]    
                    reflectance = [a*R_bdcd[i] + (1-a)*R[4][i] for i in range(5)]
                else:
                    transmittance = T[4]
                    reflectance = R[4]
            elif shgc>.5:
                b = (shgc-.5)/.05
                if U>4.54:
                    transmittance = T_bdcd  
                    reflectance = R_bdcd 
                elif U>3.41:
                    a = (U-3.41)/1.13
                    transmittance = [a*T_bdcd[i] + (1-a)*(b*T[4][i] + (1-b)*T_fghi[i]) for i in range(5)]    
                    reflectance = [a*R_bdcd[i] + (1-a)*(b*R[4][i] + (1-b)*R_fghi[i]) for i in range(5)]    
                elif U>1.7:
                    transmittance = [b*T[4][i] + (1-b)*T_fghi[i] for i in range(5)]
                    reflectance = [b*R[4][i] + (1-b)*R_fghi[i] for i in range(5)]
                elif U>1.42:
                    a = (U-1.42)/0.28
                    transmittance = [a*(b*T[4][i] + (1-b)*T_fghi[i]) + (1-a)*T[4][i] for i in range(5)]
                    reflectance = [a*(b*R[4][i] + (1-b)*R_fghi[i]) + (1-a)*R[4][i] for i in range(5)]
                else:
                    transmittance = T[4]
                    reflectance = R[4]
            elif shgc>.45: 
                if U>4.54:
                    transmittance = T_bdcd  
                    reflectance = R_bdcd 
                elif U>3.41:
                    a = (U-3.41)/1.13
                    transmittance = [a*T_bdcd[i] + (1-a)*T_fghi[i] for i in range(5)]    
                    reflectance = [a*R_bdcd[i] + (1-a)*R_fghi[i] for i in range(5)]
                elif U>1.7:
                    transmittance = T_fghi
                    reflectance = R_fghi
                elif U>1.42:
                    a = (U-1.42)/0.28
                    transmittance = [a*T_fghi[i] + (1-a)*T[4][i] for i in range(5)]
                    reflectance = [a*R_fghi[i] + (1-a)*R[4][i] for i in range(5)]
                else:
                    transmittance = T[4]
                    reflectance = R[4]
            elif shgc>.35:
                if U>4.54:
                    b = (shgc-.3)/.15
                    transmittance = [b*T_bdcd[i] + (1-b)*T[3][i] for i in range(5)]
                    reflectance = [b*R_bdcd[i] + (1-b)*R[3][i] for i in range(5)]
                elif U>3.41:
                    a = (U-3.41)/1.13
                    b = (shgc-.3)/.15
                    transmittance = [a*(b*T_bdcd[i] + (1-b)*T[3][i]) + (1-a)*T_fghi[i] for i in range(5)]    
                    reflectance = [a*(b*R_bdcd[i] + (1-b)*R[3][i]) + (1-a)*R_fghi[i] for i in range(5)]    
                elif U>1.7:
                    transmittance = T_fghi
                    reflectance = R_fghi
                elif U>1.42:
                    b = (shgc-.35)/.1
                    a = (U-1.42)/0.28
                    transmittance = [a*T_fghi[i] + (1-a)*(b*T[4][i] + (1-b)*T[9][i]) for i in range(5)]
                    reflectance = [a*R_fghi[i] + (1-a)*(b*R[4][i] + (1-b)*R[9][i]) for i in range(5)]
                else:
                    b = (shgc-.35)/.1
                    transmittance = [b*T[4][i] + (1-b)*T[9][i] for i in range(5)]
                    reflectance = [b*R[4][i] + (1-b)*R[9][i] for i in range(5)]
            elif shgc>.3:
                if U>4.54:
                    b = (shgc-.3)/.15
                    transmittance = [b*T_bdcd[i] + (1-b)*T[3][i] for i in range(5)]
                    reflectance = [b*R_bdcd[i] + (1-b)*R[3][i] for i in range(5)]
                elif U>3.41:
                    a = (U-3.41)/1.13
                    b = (shgc-.3)/.15
                    transmittance = [a*(b*T_bdcd[i] + (1-b)*T[3][i]) + (1-a)*T_fghi[i] for i in range(5)]
                    reflectance = [a*(b*R_bdcd[i] + (1-b)*R[3][i]) + (1-a)*R_fghi[i] for i in range(5)] 
                elif U>1.7:
                    transmittance = T_fghi
                    reflectance = R_fghi
                elif U>1.42:
                    a = (U-1.42)/0.28
                    transmittance = [a*T_fghi[i] + (1-a)*T[9][i] for i in range(5)]
                    reflectance = [a*R_fghi[i] + (1-a)*R[9][i] for i in range(5)]
                else:
                    transmittance = T[9]
                    reflectance = R[9]
            elif shgc>.25:
                b = (shgc-.25)/.05
                if U>4.54:
                    transmittance = T[3]
                    reflectance = R[3]  
                elif U>3.41:
                    a = (U-3.41)/1.13
                    transmittance = [a*T[3][i] + (1-a)*(b*T_fghi[i] + (1-b)*T_fh[i]) for i in range(5)]    
                    reflectance = [a*R[3][i] + (1-a)*(b*R_fghi[i] + (1-b)*R_fh[i]) for i in range(5)]    
                elif U>1.7:
                    transmittance = [b*T_fghi[i] + (1-b)*T_fh[i] for i in range(5)]
                    reflectance = [b*R_fghi[i] + (1-b)*R_fh[i] for i in range(5)]
                elif U>1.42:
                    a = (U-1.42)/0.28
                    transmittance = [a*(T_fghi[i] + (1-b)*T_fh[i]) + (1-a)*T[9][i] for i in range(5)]
                    reflectance = [a*(b*R_fghi[i] + (1-b)*R_fh[i]) + (1-a)*R[9][i] for i in range(5)]
                else:
                    transmittance = T[9]
                    reflectance = R[9]
            else:
                if U>4.54:
                    transmittance = T[3]
                    reflectance = R[3]  
                elif U>3.41:
                    a = (U-3.41)/1.13
                    transmittance = [a*T[3][i] + (1-a)*T_fh[i] for i in range(5)]
                    reflectance = [a*R[3][i] + (1-a)*R_fh[i] for i in range(5)]
                elif U>1.7:
                    transmittance = T_fh
                    reflectance = R_fh
                elif U>1.42:
                    a = (U-1.42)/0.28
                    transmittance = [a*(T_fh[i]) + (1-a)*T[9][i] for i in range(5)]
                    reflectance = [a*(R_fh[i]) + (1-a)*R[9][i] for i in range(5)]
                else:
                    transmittance = T[9]
                    reflectance = R[9]

            return transmittance,reflectance

        if u_factor<5.85:
            interior_glazing_resistance_w = float(1/(0.359073*np.log(u_factor) + 6.949915))
        else:
            interior_glazing_resistance_w = 1/(1.788041*u_factor - 2.886625)
        exterior_glazing_resistance_w = 1/(0.025342*u_factor + 29.163853)
        bare_glass_resistance = 1/u_factor - interior_glazing_resistance_w - exterior_glazing_resistance_w
        if bare_glass_resistance>7:
            thickness = 0.002
        else:
            thickness = 0.05914 - 0.00714/bare_glass_resistance
        thermal_conductivity = thickness/bare_glass_resistance
        if solar_heat_gain<0.7206:
            a =  0.939998*solar_heat_gain**2 + 0.20332*solar_heat_gain
        elif solar_heat_gain>=0.7206:
            a = 1.30415*solar_heat_gain - 0.30515
        if solar_heat_gain<=0.15:
            b = 0.41040*solar_heat_gain
        elif solar_heat_gain>0.15:
            b = 0.085775*solar_heat_gain**2 + 0.963954*solar_heat_gain - 0.084958
        if u_factor>4.5:
            normal_transmittance = [a]
        elif u_factor<3.4: 
            normal_transmittance = [b]
        else:
            normal_transmittance = [(u_factor - 3.4)/1.1*(a-b)+b]
        if visible_transmittance==None:
            visible_transmittance = normal_transmittance[0]
        shgc_Tsol = solar_heat_gain - normal_transmittance[0]
        a = 1/(29.436546*(shgc_Tsol)**3 - 21.943415*(shgc_Tsol)**2 + 9.945872*(shgc_Tsol) + 7.426151)
        b = 1/(199.8208128*(shgc_Tsol)**3 - 90.639733*(shgc_Tsol)**2 + 19.737055*(shgc_Tsol) + 6.766575)
        c = 1/(2.225824*(shgc_Tsol) + 20.57708)
        d = 1/(5.763355*(shgc_Tsol) + 20.541528)
        if u_factor>4.5:
            interior_glazing_resistance_s = a
            exterior_glazing_resistance_s = c
        elif u_factor<3.4:
            interior_glazing_resistance_s = b
            exterior_glazing_resistance_s = d
        else:
            interior_glazing_resistance_s = (u_factor - 3.4)/1.1*(a-b)+b
            exterior_glazing_resistance_s = (u_factor - 3.4)/1.1*(c-d)+d
        inward_fraction = (exterior_glazing_resistance_s + 0.5*bare_glass_resistance)/(exterior_glazing_resistance_s + bare_glass_resistance + interior_glazing_resistance_s)
        nr = 1 - normal_transmittance[0] - shgc_Tsol/inward_fraction
        normal_reflectance = [nr,nr,0,0]
        emittance = [0.84,0.84,0,0] #front side, back side, 2nd pane front, 2nd pane back
        long_wave_transmittance = 0
        vr1= -0.0622*visible_transmittance**3 + 0.4277*visible_transmittance**2 - 0.4169*visible_transmittance + 0.2399 #front side
        vr2= -0.7409*visible_transmittance**3 + 1.6531*visible_transmittance**2 - 1.2299*visible_transmittance + 0.4547 #baack side
        visible_reflectance = [vr1,vr2,0,0]
        gap_thickness = 0
        normal_transmittance.append(0.0)#placeholder for 2nd pane
        [transmittance,reflectance] = transmit_reflect_coef(solar_heat_gain,u_factor)

        window = dict(solar_heat_gain=solar_heat_gain,visible_transmittance=visible_transmittance,
                    interior_glazing_resistance_w=interior_glazing_resistance_w,
                    exterior_glazing_resistance_w=exterior_glazing_resistance_w,
                    bare_glass_resistance=bare_glass_resistance,thickness=thickness,
                    thermal_conductivity=thermal_conductivity,normal_transmittance=normal_transmittance,
                    interior_glazing_resistance_s=interior_glazing_resistance_s,
                    exterior_glazing_resistance_s=exterior_glazing_resistance_s,inward_fraction=inward_fraction,
                    normal_reflectance=normal_reflectance,emittance=emittance,
                    long_wave_transmittance=long_wave_transmittance,visible_reflectance=visible_reflectance,
                    gap_thickness=gap_thickness,transmittance=transmittance,reflectance=reflectance)
        return window

    construct = {}
    window_construct = {}
    for k in range(len(objects)):
        nm = len(objects[k]['value'])
        value = [objects[k]['value'][nm-x-1].lower() for x in range(nm)]
        name = (objects[k]['name']).lower()#.replace('-','_')
        if value[0] in materials:
            rough = materials[value[-1]]['roughness']
            k,dx,c,r = material_conductivity(materials,value,i_nodes)
            sol,therm,vis = absorptance(materials,value)
            construct[name] = dict(roughness = rough,thermal_conductivity=k,node_length = dx,capacitance = c,resistance = r,solar = sol,thermal = therm,visible = vis)
        else:
            type = window_materials[value[0].lower()]['type']
            if type=='SimpleGlazingSystem':
                window_construct[name] = simple_glazing(window_materials[value[0]])
                window_construct[name]['type'] = 'SimpleGlazingSystem'
            elif type=='Glazing':
                window_construct[name] = glazing(window_materials,value)
                window_construct[name]['type'] = 'Glazing'
    return construct, window_construct


def import_idf_surfaces(objects,construct):
    surf = load_object(['BuildingSurface:Detailed','InternalMass'], objects,0,'array')
    ns=len(surf['name'])
    surf['adiabatic']=[True for x in range(ns)]
    
    surf['capacitance'] = []
    surf['roughness'] = []
    surf['resistance'] =[]    
    vf = ['vertices','normal','area','height','perimeter','absorptance_solar','thermal_conductivity','node_length',
         'absorptance_thermal','absorptance_visible','i_nodes','roughness_factor','cos_phi']
    for x in range(len(vf)):
        surf[vf[x]] = [[] for i in range(ns)]
    values = [objects['BuildingSurface:Detailed'][x]['value'] for x in range(len(objects['BuildingSurface:Detailed']))]
    values.extend([objects['InternalMass'][x]['value'] for x in range(len(objects['InternalMass']))])
    for x in range(ns):
        if surf['type'][x]=='Detailed':
            if surf['boundary'][x]!=surf['name'][x]:
                surf['adiabatic'][x]=False
            nv=read_num(values[x][8])
            surf['vertices'][x] = [[] for i in range(nv)]
            for y in range(nv):
                vs = values[x][9+y].split(',')
                for z in range(len(vs)):
                    surf['vertices'][x][y].append(read_num(vs[z]))
            surf['area'][x],surf['perimeter'][x],surf['normal'][x] = find_area(surf['vertices'][x],surf['surf_type'][x])
            h = sorted([surf['vertices'][x][i][2] for i in range(len(surf['vertices'][x]))])
            surf['height'][x]  = h[-1] - h[0]
        elif surf['type'][x]=='InternalMass':
            surf['surf_type'].append('internalmass')
            surf['area'][x] = read_num(values[x][2])
            surf['normal'][x] = [0, 0, 1]
            surf['boundary'].append('surface')
            surf['object'].append(surf['name'][x])
    orient = ['orient_horizontal','orient_vertical','orient_tilted','orient_ceiling','orient_floor']
    for x in range(len(orient)):
        surf[orient[x]] = [False for i in range(ns)]
    for x in range(ns):
        surf['capacitance'].append(construct[surf['construct'][x]]['capacitance'])
        surf['roughness'].append(construct[surf['construct'][x]]['roughness'])
        surf['resistance'].append(construct[surf['construct'][x]]['resistance'])
        surf['absorptance_solar'][x] = construct[surf['construct'][x]]['solar']
        surf['absorptance_thermal'][x] = construct[surf['construct'][x]]['thermal']
        surf['absorptance_visible'][x] = construct[surf['construct'][x]]['visible']
        surf['thermal_conductivity'][x] = construct[surf['construct'][x]]['thermal_conductivity']
        surf['node_length'][x] = construct[surf['construct'][x]]['node_length']
        surf['i_nodes'][x] = len(surf['capacitance'][x])#interior wall states per layer minimum is 3, both surfaces and center
        surf['cos_phi'][x] = surf['normal'][x][2]/(surf['normal'][x][0]**2 + surf['normal'][x][1]**2 + surf['normal'][x][2]**2)**.5 #portion of surface pointed upwards
        if surf['roughness'][x]=='veryrough':
            surf['roughness_factor'][x]=2.17
        elif surf['roughness'][x]=='mediumrough':
            surf['roughness_factor'][x]=1.52
        elif surf['roughness'][x]=='rough':
            surf['roughness_factor'][x]=1.67
        elif surf['roughness'][x]=='mediumsmooth':
            surf['roughness_factor'][x]=1.13
        elif surf['roughness'][x]=='smooth':
            surf['roughness_factor'][x]=1.11
        n = surf['normal'][x]
        if abs(n[0])<1e-3 and abs(n[1])<1e-3:
            surf['orient_horizontal'][x] = True
            if n[2]<0:
                surf['orient_ceiling'][x] = True
            elif n[2]>0:
                surf['orient_floor'][x] = True
        if abs(n[0])<1e-3:
            surf['orient_vertical'][x] = True
        if (not surf['orient_vertical'][x] and not surf['orient_horizontal'][x]):
            surf['orient_tilted'][x] = True
    return surf


def find_area(vertices,type):
    def norm(vec):
        mag = (vec[0]**2+vec[1]**2 + vec[2]**2)**.5 #magnitude of normal vector
        return mag

    def rotate_vertices(vertices,normal):
        a = normal[0]
        b = normal[1]
        vertices_rot = [[] for i in range(len(vertices))]
        if np.dot([a,b,0],[1,0,0]) == 0: #single rotation about x-axis
            theta_z = np.sign(normal[1])*np.arccos(np.dot(normal,[0,0,1])) #angle between normal and z-axis (rotate around y-axis)
            R_x = np.array([[1, 0, 0], [0, np.cos(theta_z), -np.sin(theta_z)], [0, np.sin(theta_z), np.cos(theta_z)]])
            for k in range(len(vertices)):
                rot = R_x.dot(vertices[k])
                vertices_rot[k] = [float(rot[i]) for i in range(3)]
        else:
            theta_x = -np.sign(normal[1])*np.arccos(np.dot([a,b,0],[1,0,0])/(a**2+b**2)**.5) #angle between shadow and x-axis (rotate around z-axis)
            R_z = np.array([[np.cos(theta_x), -np.sin(theta_x), 0], [np.sin(theta_x), np.cos(theta_x), 0], [0, 0, 1]])
            normal2 = (R_z.dot(normal))
            theta_z = -np.sign(normal[0])*np.arccos(np.dot(normal2,[0,0,1])) #angle between normal and z-axis (rotate around y-axis)
            R_y = np.array([[np.cos(theta_z), 0, np.sin(theta_z)], [0, 1, 0], [-np.sin(theta_z), 0, np.cos(theta_z)]])
            for k in range(len(vertices)):
                rot = R_y.dot(R_z.dot(vertices[k]))
                vertices_rot[k] = [float(rot[i]) for i in range(3)]
        return vertices_rot

    def p_dist(P1,P2):
        d = sum([(P2[i]-P1[i])**2 for i in range(3)])**.5
        return d

    P1 = vertices[0]
    P2 = vertices[1]
    P3 = vertices[2]
    A = p_dist(P1,P2) #length from P1 to P2
    B = p_dist(P2,P3) #length from P2 to P3
    C = p_dist(P3,P1) #length from P3 to P1
    j = 3
    while np.abs(A**2+B**2 + C**2 - (A+B+C)**2) < 0.0001*(A+B+C)**2: #change point 3 if vertices are on same line
        j +=1
        P3 = vertices[j]
        B = p_dist(P2,P3)  #length from P2 to P3
        C = p_dist(P3,P1) #length from P3 to P1
    normal_v = [0,0,0]
    for x in range(len(vertices)-2):
        c = np.cross([vertices[x+1][i]-vertices[x][i] for i in range(3)],[vertices[x+2][i]-vertices[x+1][i] for i in range(3)])
        normal_v = [normal_v[0] + float(c[0]),normal_v [1]+float(c[1]), normal_v [2] + float(c[2])]
    normal_v2 = np.cross([P2[i]-P1[i] for i in range(3)],[P3[i]-P2[i] for i in range(3)])
    
    normal = [normal_v[i]/norm(normal_v) for i in range(3)]
    normal2 = [float(normal_v2[i]/norm(normal_v2)) for i in range(3)]
    if any([abs(normal[i] - normal2[i])>1e-4 for i in range(3)]): #trouble getting correct normal vector direction with non-convex floor or ceiling shape
        if type=='floor':
            normal = [0,0,-1]
        else:
            normal = [0,0,1]
    if normal[0]!=0 or normal[1]!=0:
        vertices = rotate_vertices(vertices,normal)
    x = [vertices[i][0] for i in range(len(vertices))]
    y = [vertices[i][1] for i in range(len(vertices))]
    area = 0.5*abs(float(np.dot(x,np.roll(y,1))-np.dot(y,np.roll(x,1))))
    perimeter = abs(float(np.sum(((np.roll(x,-1) - x)**2 + (np.roll(y,-1) -y)**2)**.5)))
    return area,perimeter,normal


def import_windows_doors(objects,construct):
    def load_finest(fin,construct,vf):
        n=len(fin['name'])
        if n>0:
            orient = ['orient_horizontal','orient_vertical','orient_tilted','orient_ceiling','orient_floor']
            for x in range(len(orient)):
                fin[orient[x]] = [False for i in range(n)]
            for x in range(len(vf)):
                fin[vf[x]] = [[] for i in range(n)]
            for x in range(n):
                fin['area'][x],fin['perimeter'][x],fin['normal'][x] = find_area(fin['vertices'][x],'')
                fin['height'][x] = sum([fin['vertices'][x][i][2] for i in range(len(fin['vertices'][x]))])/len(fin['vertices'][x])
                for y in range(5,len(vf)):
                    if vf[y] in construct[fin['construct'][x]]:
                        fin[vf[y]][x] = construct[fin['construct'][x]][vf[y]]
                n = fin['normal'][x]
                if abs(n[0])<1e-3 and abs(n[1])<1e-3:
                    fin['orient_horizontal'][x] = True
                    if n[2]<0:
                        fin['orient_ceiling'][x] = True
                    elif n[2]>0:
                        fin['orient_floor'][x] = True
                if abs(n[0])<1e-3:
                    fin['orient_vertical'][x] = True
                if (not fin['orient_vertical'][x] and not fin['orient_horizontal'][x]):
                    fin['orient_tilted'][x] = True
                fin['cos_phi'][x] = fin['normal'][x][2]/(fin['normal'][x][0]**2 + fin['normal'][x][1]**2 + fin['normal'][x][2]**2)**.5 #portion of findow pointed upwards
        return fin
    
    finest = load_object(['FenestrationSurface:Detailed'], objects,0,'array')
    win = {}
    door = {}  
    wv = ['name','construct','surf_name','object','view_factor','shading','frame_name','multiplier']
    for y in wv:
        win[y] = [] 
        door[y] = []
    win['vertices']= []  
    door['vertices']= []  
    values = [objects['FenestrationSurface:Detailed'][x]['value'] for x in range(len(objects['FenestrationSurface:Detailed']))]
    for x in range(len(finest['name'])):
        nv=read_num(values[x][8])
        vert = [[0,0,0] for i in range(nv)]
        for y in range(nv):
            vs = values[x][9+y].split(',')
            for z in range(3):
                vert[y][z]=read_num(vs[z]) 
        if finest['surf_type'][x]=='window':
            win['vertices'].append(vert)
            for y in wv:
                win[y].append(finest[y][x]) 
        elif finest['surf_type'][x]=='door':
            door['vertices'].append(vert)
            for y in wv:
                door[y].append(finest[y][x])
    vf = ['normal','cos_phi','area','height','perimeter','normal_transmittance','normal_reflectance','emittance','thermal_conductivity','solar_heat_gain','gap_thickness','transmittance','reflectance','thickness']
    win =load_finest(win,construct,vf)
    win['type'] = [construct[win['construct'][x]]['type'] for x in range(len(win['name']))]
    vf = ['normal','cos_phi','area','height','perimeter']
    door =load_finest(door,construct,vf)
    return win, door


def zone_geometry(zone,surf,window):
    ctf = {}
    n_z = len(zone['name'])
    n_sur = len(surf['name'])
    nw = len(window['name'])
    ceil_area = [0 for i in range(n_z)]
    floor_height = [0 for i in range(n_z)]
    zone['floor_area'] = [0 for i in range(n_z)]
    zone['ceil_height'] = [0 for i in range(n_z)]
    surf['zone_index'] =[0 for i in range(n_sur)]
    zone['surfaces'] = []  
    zone['windows'] = []  
    for i in range(n_z):
        zone['surfaces'].append([])  
        zone['windows'].append([])  
    zone['exterior_area'] = [0 for i in range(n_z)]
    for i in range(n_sur):
        k=zone['name'].index(surf['zone'][i])
        surf['zone_index'][i] = k
        zone['surfaces'][k].append(i)
        if surf['surf_type'][i]=='floor':
            zone['floor_area'][k] += surf['area'][i]
        elif surf['surf_type'][i]=='roof' or surf['surf_type'][i]=='ceiling':
            ceil_area[k] += surf['area'][i]
        if  surf['boundary'][i]=='outdoors':
            zone['exterior_area'][k] += surf['area'][i]
        if surf['surf_type'][i]!='internalmass':
            for j in range(len(surf['vertices'][i])):
                surf['vertices'][i][j] = [surf['vertices'][i][j][0]+zone['x_origin'][k],
                                          surf['vertices'][i][j][1]+zone['y_origin'][k],
                                          surf['vertices'][i][j][2]+zone['z_origin'][k]] #change 3-d position of surface based on zone "origin"
    for i in range(n_sur):
        if surf['surf_type'][i]=='roof' or surf['surf_type'][i]=='ceiling':
            k=zone['name'].index(surf['zone'][i])
            l = len(surf['vertices'][i])
            zone['ceil_height'][k] += sum([surf['vertices'][i][j][2] for j in range(l)])/l*surf['area'][i]/ceil_area[k] #z-coordinate 
        elif surf['surf_type'][i]=='floor':
            k=zone['name'].index(surf['zone'][i])
            l = len(surf['vertices'][i])
            floor_height[k] += sum([surf['vertices'][i][j][2] for j in range(l)])/l*surf['area'][i]/zone['floor_area'][k] #%z-coordinate
    zone['ceil_height'] = [max(0,zone['ceil_height'][i]-floor_height[i]) for i in range(n_z)] 
    zone['volume'] = [zone['ceil_height'][i]*zone['floor_area'][i] for i in range(n_z)] 

    window['surface'] = [0 for i in range(nw)]
    window['zone'] = []
    window['ext_surf']=[]
    window['zone_index']= [0 for i in range(nw)]
    window['elevation']= [0 for i in range(nw)]
    for i in range(nw):
        s=surf['name'].index(window['surf_name'][i])
        window['surface'][i] = s
        window['zone'].append(surf['zone'][s])
        k=zone['name'].index(window['zone'][i])
        zone['windows'][k].append(i)
        window['zone_index'][i] = k
        for j in range(len(window['vertices'][i])):
                window['vertices'][i][j] = [window['vertices'][i][j][0]+zone['x_origin'][k],
                                            window['vertices'][i][j][1]+zone['y_origin'][k],
                                            window['vertices'][i][j][2]+zone['z_origin'][k]] #change 3-d position of surface based on zone "origin"
        surf['area'][window['surface'][i]] -= window['area'][i]
        l = len(window['vertices'][i])
        floor = min([surf['vertices'][s][j][2] for j in range(len(surf['vertices'][s]))])
        window['elevation'][i] =  sum([window['vertices'][i][j][2]-floor for j in range(l)])/l #height from floor
        if window['normal'][i][2]==1 or surf['surf_type'][window['surface'][i]]=='roof':  #skylight
            window['elevation'][i] += zone['ceil_height'][window['zone_index'][i]]

    def calc_view_factors(area_s,area_w,im_sur,s_norm):
        n = len(area_s)
        w = len(area_w)
        vf = np.zeros((n+w,n+w))
        area = area_s+area_w
        net_area = sum(area)
        for i in range(n+w):
            seen_area = net_area
            try:
                k = im_sur.index(i)
                seen_area -= area[i]
            except ValueError:
                for j in range(n+w):
                    try:
                        k = im_sur.index(j)
                    except ValueError:
                        if np.dot(s_norm[i],s_norm[j])>.985: #parallel surfaces (within 10 degrees) = zero view factor, pg 103 of manual
                            seen_area-= area[j]
            for j in range(n+w):
                if i!=j:
                    if np.dot(s_norm[i],s_norm[j])<=.985:
                        vf[i,j] = area[j]/seen_area #otherwise do nothing window/surfaces dont see each other
                    else:
                        try:
                            k = im_sur.index(i)
                            vf[i,j] = area[j]/seen_area
                        except ValueError:
                            try:
                                k = im_sur.index(j)
                                vf[i,j] = area[j]/seen_area
                            except ValueError:
                                pass
        #check reciprocity!: 
        area_i = np.tile(area,(n+w,1)).T
        vf_error = np.ones((n+w,n+w))
        while np.any(np.abs(vf_error)>1e-6):
            vf_scaled = vf*area_i
            vf_error = vf_scaled - vf_scaled.T
            with np.errstate(divide='ignore'):
                max_vf = np.maximum(vf_scaled,vf_scaled.T)
                perc_error = vf_error/max_vf
                perc_error[max_vf == 0] = 0
            vf = vf*(1-.5*perc_error)
            vf = vf*(np.tile((1/np.sum(vf,1)),(n+w,1)).T) #ensure all add up to 1
        return vf

    zone['view_factors'] = [[0 for i in range(n_sur+nw)] for j in range(n_sur+nw)]
    surf['area_rad'] = [surf['area'][i] for i in range(len(surf['area']))] #in case some internal mass objects surface area must be 'reduced' to enforce reciprocity (area of internal mass greater than area of surfaces in zone)
    for i in range(len(surf['surf_type'])):
        if surf['surf_type'][i]=='internalmass':
            surf['area_rad'][i] = surf['area_rad'][i]/2
    for k in range(n_z):
        #compute internal view factors in single zone
        sur_k = [i for i, e in enumerate(surf['zone_index']) if e==k]
        win_k = [i for i, e in enumerate(window['zone_index']) if e==k]
        im_sur = []
        for j in range(len(sur_k)):
            if surf['surf_type'][sur_k[j]]=='internalmass':
                im_sur.append(j)
        normal = []
        for i in range(len(sur_k)):
            normal.append(surf['normal'][sur_k[i]])
        for i in range(len(win_k)):
            normal.append(window['normal'][win_k[i]])
        a = [surf['area_rad'][i] for i in sur_k]
        b = [window['area'][i] for i in win_k]
        vf_zone = calc_view_factors(a,b,im_sur,normal)
        #combine all view factors into 1 matrix [surfaces;windows];
        sur_k.extend([win_k[x]+n_sur for x in range(len(win_k))])
        for i in range(len(sur_k)):
            for j in range(len(sur_k)):
                zone['view_factors'][sur_k[i]][sur_k[j]] = float(vf_zone[i,j])
                zone['view_factors'][sur_k[j]][sur_k[i]] = float(vf_zone[j,i])

    ext = [i for i, e in enumerate(surf['boundary']) if e=='outdoors' or e=='ground']
    surf['exterior']={}
    surf['exterior']['name'] = [surf['name'][x] for x in ext]
    surf['exterior']['normal'] = [surf['normal'][x] for x in ext]
    surf['exterior']['cos_phi'] = [surf['cos_phi'][x] for x in ext]
    surf['exterior']['thermal_absorptance'] = [surf['absorptance_thermal'][x][1] for x in ext]
    surf['exterior']['solar_absorptance'] = [surf['absorptance_solar'][x][1] for x in ext]
    surf['exterior']['boundary'] = [surf['boundary'][x] for x in ext]
    surf['exterior']['roughness_factor'] = [surf['roughness_factor'][x] for x in ext]
    surf['exterior']['perimeter'] = [surf['perimeter'][x] for x in ext]
    surf['exterior']['area'] = [surf['area'][x] for x in ext] #area without windows

    for i in range(len(window['name'])):
        window['ext_surf'].append(surf['exterior']['name'].index(window['surf_name'][i]))

    ctf,zone['interior_area'] = build_ctf(zone,surf,window)
    return zone, surf, window, ctf


def build_ctf(zones,surfaces,windows):
    '''
    organize surface and interior surface states for heat transfer calculations
    '''
    n_z = len(zones['name'])
    n_sur = len(surfaces['name'])
    ctf = {}
    ctf['z_height'] = [0 for i in range(n_z)]
    zone_surf_area = [0 for i in range(n_z)]
    s_states = 0 #number of temperature states associated with walls
    ctf['sur_state1'] = [0 for i in range(n_sur)]
    ctf['sur_state2'] = []
    for k in range(n_z):
        sur = [i for i, e in enumerate(surfaces['zone_index']) if e==k]
        win = [i for i, e in enumerate(windows['zone_index']) if e==k]
        zone_surf_area[k] = sum([surfaces['area'][i] for i in sur])
        if len(win)>0:
            zone_surf_area[k] += sum([windows['area'][i] for i in win])

    ctf['z_height'] = [i/2 for i in zones['ceil_height']]

    first_side=[True for x in range(n_sur)]
    for s in range(n_sur):
        if surfaces['boundary'][s]=='outdoors' or surfaces['boundary'][s]=='ground':
            s_states += len(surfaces['capacitance'][s])
        elif surfaces['boundary'][s]=='surface':
            b = surfaces['name'].index(surfaces['object'][s])
            if b<s:
                first_side[s] = False  #already counted the states, this avoids doing things twice, since calculations for surface A-->B and B-->A are the same
            else:
                s_states += len(surfaces['capacitance'][s])
        else:
            print(s)

    ctf['capacitance'] = [0 for i in range(s_states)]
    ctf['interior_surface'] = [[] for i in range(n_sur)]  #index of interior surface T state
    ctf['surf_area'] = [0 for i in range(s_states)]
    ctf['subsurf_names'] = []
    ctf['interior_absorb'] = [0 for i in range(n_sur)]

    n_ext = len(surfaces['exterior']['name'])
    ctf['exterior_surface'] = [[] for i in range(n_ext)] #index of exterior surface T state
    ctf['exterior_area'] = [0 for i in range(n_ext)]
    ctf['exterior_absorb'] = [0 for i in range(n_ext)]
    ctf['s_height'] = [0 for i in range(n_ext)]
    ctf['ground_cond'] = [0 for i in range(n_ext)]
    A_diag = [[] for i in range(3)] # matrix for implicit calculation of heat conduction through surfaces (net flux from both sides = change in stored energy)
    i = 0
    ext = 0
    for s in range(n_sur):
        j = zones['name'].index(surfaces['zone'][s])  #zone that it is touching
        C = [surfaces['capacitance'][s][x]*surfaces['area'][s] for x in range(len(surfaces['capacitance'][s]))]
        ctf['interior_absorb'][s] = surfaces['absorptance_thermal'][s][1]
        i_nodes = len(surfaces['capacitance'][s])
        K = surfaces['thermal_conductivity'][s]
        dx = surfaces['node_length'][s]
        if surfaces['boundary'][s]=='ground':
            K = [K[x]*6 for x in range(len(K))]
        if first_side[s]:
            ctf['interior_surface'][s]= i
            for j in range(i_nodes):
                ctf['subsurf_names'].append(surfaces['name'][s] +'_' + str(j))
            cond = [-K[m]/dx[m] for m in range(len(K))]
            A_diag[0].extend(cond)
            A_diag[0].append(0)
            A_diag[2].append(0)
            A_diag[2].extend(cond)
            A_diag[1].extend([-A_diag[0][i+j]-A_diag[2][i+j] for j in range(len(K)+1)])
            ctf['sur_state1'][s] = i
            ctf['capacitance'][i:i+i_nodes] = C
            ctf['surf_area'][i:i+i_nodes] = [surfaces['area'][s] for j in range(i_nodes)]
            i += i_nodes
        if surfaces['boundary'][s]=='outdoors' or surfaces['boundary'][s]=='ground':
            if surfaces['boundary'][s]=='ground':
                ctf['ground_cond'][ext] = K[i_nodes-2]
            ctf['sur_state2'].append(i-1)
            ctf['exterior_surface'][ext] = i-1
            ctf['exterior_area'][ext] = surfaces['area'][s]
            ctf['exterior_absorb'][ext] = surfaces['absorptance_solar'][s][1]
            l = len(surfaces['vertices'][s])
            ctf['s_height'][ext] = sum([surfaces['vertices'][s][j][2] for j in range(l)])/l
            ext +=1
        elif surfaces['boundary'][s]=='surface':
            b = surfaces['name'].index(surfaces['object'][s])
            if b>s:  #move second side up list to here so that A_diag matrice is collected together
                ctf['sur_state1'][b] = i-1
                ctf['subsurf_names'][i-1] = surfaces['name'][b]
                ctf['interior_surface'][b] = i-1
    ctf['A_diag'] = A_diag
    
    maxC = np.amax(ctf['capacitance'])
    if np.amin(ctf['capacitance'])/maxC<1e-4:
        ctf['capacitance'] = [max(5e-4*maxC,ctf['capacitance'][i]) for i in range(s_states)]  #increase capacitance of air wall and the like to help with numerical solving
    return ctf,zone_surf_area


def import_infiltration(objects,zones):
    infil = load_object(['ZoneInfiltration:DesignFlowRate'], objects,0,'array')
    n = len(infil['name'])
    infiltration = {}
    infiltration['nominal'] = [0 for i in range(n)]
    infiltration['zone'] = [zones['name'].index(infil['zone_name'][x]) for x in range(n)]
    infiltration['schedule'] = [infil['schedule'][x] for x in range(n)]
    for x in range(n):
        if infil['method'][x]=='flow/zone':
            infiltration['nominal'][x] = infil['nominal_set'][x]
        elif infil['method'][x]=='flow/area':
            infiltration['nominal'][x] = zones['floor_area'][infiltration['zone'][x]]*infil['per_area'][x]
        elif infil['method'][x]=='flow/exteriorarea':
            infiltration['nominal'][x] = zones['exterior_area'][infiltration['zone'][x]]*infil['per_ext_area'][x]
        elif infil['method'][x]=='airchanges/hour':
            infiltration['nominal'][x] = zones['volume'][infiltration['zone'][x]]*infil['changes_per_hr'][x]/3600
    return infiltration


def import_mixing(objects,zones,schedule):
    mix = load_object(['ZoneMixing'], objects,0,'array')
    n = len(mix['name'])
    mixing = {}
    mixing['nominal'] = [0 for i in range(n)]
    mixing['receiving_zone'] = [zones['name'].index(mix['receiving_zone'][x]) for x in range(n)]
    mixing['source_zone'] = [zones['name'].index(mix['source_zone'][x]) for x in range(n)]
    mixing['type'] = [mix['mix_type'][x] for x in range(n)]
    mixing['schedule'] = [mix['schedule'][x] for x in range(n)]
    for x in range(n):
        if mix['mix_type'][x]=='flow/zone':
            mixing['nominal'][x] = mix['nominal_set'][x]
        elif mix['mix_type'][x]=='flow/area':
            mixing['nominal'][x] = zones['floor_area'][mixing['zone'][x]]*mix['per_area'][x]
        elif mix['mix_type'][x]=='flow/exteriorarea':
            mixing['nominal'][x] = zones['exterior_area'][mixing['zone'][x]]*mix['per_ext_area'][x]
        elif mix['mix_type'][x]=='airchanges/hour':
            mixing['nominal'][x] = zones['volume'][mixing['zone'][x]]*mix['changes_per_hr'][x]/3600
    return mixing


def import_occupancy(objects,zones):
    occupancy = {}
    occ = load_object(['People'], objects,0,'array')
    n = len(occ['name'])
    occupancy = {}
    occupancy['name'] = [occ['name'][x] for x in range(n)]
    occupancy['nominal'] = [0 for i in range(n)]
    occupancy['zone'] = [zones['name'].index(occ['zone_name'][x]) for x in range(n)]
    occupancy['schedule'] = [occ['schedule'][x] for x in range(n)]
    occupancy['radiant'] = [occ['radiant'][x] for x in range(n)]
    occupancy['convected'] = [1-occupancy['radiant'][x] for x in range(n)]
    occupancy['activity'] = [occ['activity'][x] for x in range(n)]
    occupancy['work_eff'] = [occ['work_eff'][x] for x in range(n)]
    for x in range(n):
        if occ['method'][x]=='people':
            occupancy['nominal'][x] = occ['people'][x]/zones['floor_area'][occupancy['zone'][x]]
        elif occ['method'][x]=='people/area':
            occupancy['nominal'][x] = occ['people_per_area'][x]
        elif occ['method'][x]=='area/person':
            occupancy['nominal'][x] = 1/occ['area_per_person'][x]
    zones['max_occupancy'] = [0 for i in range(len(zones['name']))]
    for i in range(len(occupancy['zone'])):
        zones['max_occupancy'][occupancy['zone'][i]] += occupancy['nominal'][i]*zones['floor_area'][occupancy['zone'][i]] 
    return occupancy, zones


def import_lighting(objects,zones):
    lighting = {}
    lit = load_object(['Lights'], objects,0,'array')
    n = len(lit['name'])
    lighting = {}
    lighting['name'] = [lit['name'][x] for x in range(n)]
    lighting['nominal'] = [0 for i in range(n)]
    lighting['zone'] = [zones['name'].index(lit['zone_name'][x]) for x in range(n)]
    lighting['schedule'] = [lit['schedule'][x] for x in range(n)]
    lighting['radiant'] = [lit['radiant'][x] for x in range(n)]
    lighting['visible'] = [lit['visible'][x] for x in range(n)]
    lighting['convected'] = [1-lighting['radiant'][x] - lighting['visible'][x] for x in range(n)]
    for x in range(n):
        if lit['method'][x]=='lightinglevel':
            lighting['nominal'][x] = lit['light_level'][x]/zones['floor_area'][lighting['zone'][x]]
        elif lit['method'][x]=='watts/area':
            lighting['nominal'][x] = lit['watt_area'][x]
        elif lit['method'][x]=='watts/person':
            lighting['nominal'][x] = zones['max_occupancy'][lighting['zone'][x]]*lit['watt_person'][x]/zones['floor_area'][lighting['zone'][x]]
    return lighting


def import_equipment(objects,zones,type):
    equipment = {}
    equip = load_object([type], objects,0,'array')
    n = len(equip['name'])
    equipment = {}
    equipment['name'] = [equip['name'][x] for x in range(n)]
    equipment['nominal'] = [0 for i in range(n)]
    equipment['zone'] = [zones['name'].index(equip['zone_name'][x]) for x in range(n)]
    equipment['schedule'] = [equip['schedule'][x] for x in range(n)]
    equipment['latent'] = [equip['latent'][x] for x in range(n)]
    equipment['radiant'] = [equip['radiant'][x] for x in range(n)]
    equipment['lost'] = [equip['lost'][x] for x in range(n)]
    equipment['convected'] = [1-equipment['latent'][x] - equipment['radiant'][x]  - equipment['lost'][x] for x in range(n)]
    for x in range(n):
        if equip['method'][x]=='equipmentlevel':
            equipment['nominal'][x] = equip['equip_level'][x]/zones['floor_area'][equipment['zone'][x]]
        elif equip['method'][x]=='watts/area':
            equipment['nominal'][x] = equip['watt_area'][x]
        elif equip['method'][x]=='watts/person':
            equipment['nominal'][x] = zones['max_occupancy'][equipment['zone'][x]]*equip['watt_person'][x]/zones['floor_area'][equipment['zone'][x]]
    return equipment


def rack_cases(racks,cases,objects):
    list_rack = load_object(['Refrigeration:CaseAndWalkInList'], objects,1,'array') 
    n = len(list_rack['name']) 
    for x in racks:
        racks[x]['cases'] = []
    for i in range(n):
        for k in range(len(list_rack['case'][i])):
            try:
                racks[list_rack['name'][i]]['cases'].append(list_rack['case'][k])
            except ValueError:
                pass#do nothing
    for x in racks:
        try:
            racks[x]['cases'].append(racks[x]['case_name'])
        except ValueError:
            pass
    return racks


def import_outdoor_air(objects):
    out = load_object(['DesignSpecification:OutdoorAir'], objects,0,'array') 
    outdoor_air = {}
    if len(out)>0:
        n = len(out['name'])
        outdoor_air['name'] = [out['name'][k] for k in range(n)]
        outdoor_air['method'] = [out['method'][k] for k in range(n)]
        outdoor_air['value'] = []
        for x in range(n):
            if outdoor_air['method'][x]=='flow/person':
                outdoor_air['value'].append(out['flow_person'][x])
            elif outdoor_air['method'][x]=='flow/area':
                outdoor_air['value'].append(out['flow_area'][x])
            elif outdoor_air['method'][x]=='flow/zone':
                outdoor_air['value'].append(out['flow_zone'][x])
    return outdoor_air


def import_hvac(objects,zone_names,schedules):
    hvac = {}
    e_list = {}
    def load_design_size(objects,air_loop):
        design = load_object(['SizingPeriod:DesignDay'], objects,0,'array') 
        design['heat_sizing_factor'] = objects['Sizing:Parameters'][0]['name']
        design['cooling_sizing_factor'] = objects['Sizing:Parameters'][0]['value'][0]
        design['averaging_window'] = objects['Sizing:Parameters'][0]['value'][1]

        
        loop_size = load_object(['Sizing:System'],objects,0,'array')
        loops = len(loop_size['name'])
        design['all_outdoor_flow_cooling'] = [True for x in range(loops)]
        design['all_outdoor_flow_heating'] = [True for x in range(loops)]
        design['control_method']=[[] for x in range(loops)]
        vk = ['outdoor_flow','T_preheat','w_preheat','T_precool','w_precool','Tsupply_c','Tsupply_h','w_supply_c','w_supply_h']
        for j in range(len(vk)):
            design[vk[j]] = [0 for i in range(loops)]
        for i in range(loops):
            k = air_loop['name'].index(loop_size['name'][i])
            for j in range(len(vk)):
                try:
                    design[vk[j]][k] = loop_size[vk[j]][i]
                except ValueError:#leave as zero, was propbably a string (autosize)
                    pass
            if loop_size['cool_all_outdoor_air'][i]=='no':
                design['all_outdoor_flow_cooling'][k]= False
            if loop_size['heat_all_outdoor_air'][i]=='no':
                design['all_outdoor_flow_heating'][k] = False
            design['control_method'][k] = loop_size['control_method'][i]
        return design

    def load_terminals(objects,splitters,air_loop,e_list):
        #splitters connect to demand_inlet
        terminals = load_object(['AirTerminal:SingleDuct:Uncontrolled','AirTerminal:SingleDuct:VAV:Reheat'],objects,0,'array')
        air_distribution = load_object(['ZoneHVAC:AirDistributionUnit'],objects,0,'array')
        terminals['zone'] = []
        terminals['outlet'] = []
        terminals['return_'] = []
        terminals['loop'] = []
        for i in range(len(terminals['name'])):
            try: 
                k = e_list['e_name'].index(terminals['name'][i])
            except ValueError:
                ad = air_distribution['terminal'].index(terminals['name'][i])
                k = e_list['e_name'].index(air_distribution['name'][ad])
            terminals['zone'].append(e_list['zone'][k])
            terminals['outlet'].append(e_list['outlet'][k])
            terminals['return_'].append(e_list['return_'][k])
            for j in range(len(splitters['name'])):
                try:
                    k = splitters['outlets'][j].index(terminals['inlet'][i])
                    terminals['loop'].append(air_loop['demand_inlet'].index(splitters['inlet'][j]))
                    break
                except ValueError:
                    pass
        return terminals

    hvac['loop'] = load_object(['AirLoopHVAC'], objects,0,'array') 
    hvac['loop']['branches'] = []
    hvac['loop']['max_flow'] = [0 for i in range(len(hvac['loop']['name']))]
    branch_list = load_object(['BranchList'], objects,1,'array') 
    for i in range(len(hvac['loop']['name'])):
        bl = branch_list['name'].index(hvac['loop']['branch_list'][i])
        hvac['loop']['branches'].append(branch_list['branches'][bl])
    hvac['design'] = load_design_size(objects,hvac['loop'])

    hvac['branches'] = load_object(['Branch'],objects,4,'array')
    n = len(hvac['branches']['name'])
    hvac['branches']['loop'] = [-1 for i in range(n)]
    hvac['branches']['inlet'] = []
    hvac['branches']['outlet'] = []
    for j in range(n):
        for l in range(len(hvac['loop']['name'])):
            try:
                l_b = hvac['loop']['branches'][l].index(hvac['branches']['name'][j])
                hvac['branches']['loop'][j] = l
                break
            except ValueError:
                pass
        hvac['branches']['inlet'].append(hvac['branches']['component_inlet'][j][0])
        hvac['branches']['outlet'].append(hvac['branches']['component_outlet'][j][-1])
    hvac['supply_path'] = load_object(['AirLoopHVAC:SupplyPath'],objects,2,'array')
    n = len(hvac['supply_path']['name'])
    hvac['supply_path']['loop'] = [0 for i in range(n)]
    for k in range(n):
        hvac['supply_path']['loop'][k] = hvac['loop']['demand_inlet'].index(hvac['supply_path']['inlet'][k])
        hvac['branches']['inlet'].append([])
        hvac['branches']['outlet'].append(hvac['supply_path']['inlet'][k])
        hvac['branches']['name'].append(hvac['supply_path']['name'][k])
        hvac['branches']['loop'].append(-1)
    hvac['return_path'] = load_object(['AirLoopHVAC:ReturnPath'],objects,2,'array')
    n=len(hvac['return_path']['name'])
    hvac['return_path']['loop'] = [0 for i in range(n)]
    for k in range(n):
        hvac['return_path']['loop'][k] = hvac['loop']['demand_outlet'].index(hvac['return_path']['outlet'][k])
        hvac['branches']['inlet'].append(hvac['return_path']['outlet'][k])
        hvac['branches']['outlet'].append([])
        hvac['branches']['name'].append(hvac['return_path']['name'][k])
        hvac['branches']['loop'].append(-1)
    #Items with varying length (# of connections etc)
    hvac['splitters'] = load_object(['AirLoopHVAC:ZoneSplitter'],objects,1,'array')
    hvac['mixers'] = load_object(['AirLoopHVAC:ZoneMixer'],objects,1,'array')
    hvac['plenum'] = load_object(['AirLoopHVAC:ReturnPlenum'],objects,1,'array')
    
    zone_hvac = load_object(['ZoneHVAC:EquipmentConnections'],objects,0,'array')
    e_list = load_object(['ZoneHVAC:EquipmentList'],objects,4,'extend')

    n = len(e_list['name'])
    e_list['zone'] = [0 for i in range(n)]
    e_list['inlet'] = []
    e_list['outlet'] = []
    e_list['return_'] = []
    for x in range(n):
        ec = zone_hvac['hvac_equipment'].index(e_list['name'][x])
        ar = zone_hvac['return_'][ec]
        if len(hvac['plenum'])>0:
            for y in range(len(hvac['plenum']['name'])):
                try:
                    hvac['plenum']['inlets'][y].index(ar)
                    ar = hvac['plenum']['outlet'][y]
                    break
                except ValueError:
                    pass
        e_list['zone'][x] = int(zone_names.index(zone_hvac['name'][ec]))
        e_list['inlet'].append(zone_hvac['inlet'][ec])
        e_list['outlet'].append(zone_hvac['exhaust'][ec])
        e_list['return_'].append(ar)
    # Terminals
    hvac['terminals'] = load_terminals(objects,hvac['splitters'],hvac['loop'],e_list)
    #All HVAC components
    hvac['components'] = read_components(hvac['branches'],hvac['mixers'],hvac['splitters'])
    ##add terminals/distribution units/zones to connect demand equipment
    for i in range(len(hvac['terminals']['name'])):
        hvac['components']['name'].append(hvac['terminals']['name'][i])
        hvac['components']['type'].append('AirTerminal:SingleDuct:'+hvac['terminals']['type'][i])
        hvac['components']['inlet'].append(hvac['terminals']['inlet'][i])
        hvac['components']['outlet'].append(hvac['terminals']['return_'][i])
        hvac['components']['bypass'].append(False)
        hvac['components']['branch'].append(zone_names[hvac['terminals']['zone'][i]])
        hvac['components']['branch_number'].append(len(hvac['branches']['name'])+hvac['terminals']['zone'][i])
        hvac['components']['loop'].append(hvac['terminals']['loop'][i])

    ###Outdoor air
    oa_sys = load_object(['AirLoopHVAC:OutdoorAirSystem'],objects,0,'array')
    oa_list = load_object(['AirLoopHVAC:ControllerList'],objects,0,'array')
    hvac['outdoor_air'] = load_object(['Controller:OutdoorAir'],objects,0,'array')
    hvac['outdoor_air']['loop'] = []
    hvac['outdoor_air']['control'] = []
    for i in range(len(hvac['outdoor_air']['name'])):
        ln = oa_list['controller_name'].index(hvac['outdoor_air']['name'][i])
        sys = oa_sys['controller_list'].index(oa_list['name'][ln])
        l =hvac['components']['name'].index(oa_sys['name'][sys])
        hvac['outdoor_air']['loop'].append(hvac['components']['loop'][l])
        hvac['outdoor_air']['control'].append(oa_list['controller_name'][ln])
    ###Air routing
    zone_loop,zone_plenum,hvac['plenum'] = connect_zones_loops(zone_names,hvac['plenum'],hvac['mixers'],hvac['loop'],zone_hvac)
    ###Managers
    manager_list = load_object(['AvailabilityManagerAssignmentList'],objects,2,'array')
    hvac['managers'] = load_object(['AvailabilityManager:NightCycle','AvailabilityManager:Scheduled'],objects,0,'array')
    n = len(hvac['managers']['name'])
    hvac['managers']['loop'] = [-1 for i in range(n)]
    for i in range(n):
        for j in range(len(manager_list['name'])):
            try: 
                k = manager_list['manager_name'][j].index(hvac['managers']['name'][i])
                hvac['managers']['loop'][i] = hvac['loop']['manager'].index(manager_list['name'][j])
                break
            except ValueError:
                pass
    return hvac,e_list,zone_loop,zone_plenum


def read_components(branches,mixers,splitters):
    #putting components in an order so that they are simulated correctly
    components = {}
    components['name'] = []
    components['type'] = []
    components['branch'] = []
    components['branch_number'] = []
    components['loop'] = []
    components['inlet'] = []
    components['outlet'] = []
    components['bypass'] = []
    for i in range(len(mixers['name'])):
        m_in = mixers['inlets'][i]
        b = branches['inlet'].index(mixers['outlet'][i])
        for j in range(len(m_in)):
            components['name'].append(mixers['name'][i])
            components['type'].append('mixer')
            components['inlet'].append(m_in[j])
            components['outlet'].append(mixers['outlet'][i])
            components['bypass'].append(False)
            components['branch'].append(branches['name'][b])
            components['branch_number'].append(b)
            components['loop'].append(branches['loop'][b])
    j = len(components['name'])
    for i in range(len(branches['component_type'])):
        if branches['loop'][i]>=0:
            n = len(branches['component_type'][i])
            components['name'].extend(branches['component_name'][i])
            components['type'].extend(branches['component_type'][i])
            components['branch'].extend(branches['name'][i])
            components['branch_number'].extend([i for y in range(n)])
            components['loop'].extend([branches['loop'][i] for y in range(n)])
            components['inlet'].extend(branches['component_inlet'][i])
            components['outlet'].extend(branches['component_outlet'][i])
            mix_inlet = False
            for x in range(j):
                try: 
                    con = components['inlet'][x].index(components['outlet'][j])
                    if con>=0 and components['type'][x]=='mixer':
                        mix_inlet = True
                    break
                except ValueError:
                    pass
            if (n ==1 and components['type'][j]=='pipe:adiabatic' and mix_inlet): 
                components['bypass'].append(True)
            else:
                components['bypass'].extend([False for y in range(n)])
            j +=n
    for i in range(len(splitters['name'])):
        s_out = splitters['outlets'][i]
        b = branches['outlet'].index(splitters['inlet'][i])
        for j in range(len(s_out)):
            components['name'].append(splitters['name'][i])
            components['type'].append('splitter')
            components['inlet'].append(splitters['inlet'][i])
            components['outlet'].append(s_out[j])
            components['bypass'].append(False)
            components['branch'].append(branches['name'][b])
            components['branch_number'].append(b)
            components['loop'].append(branches['loop'][b])
    return components


def connect_zones_loops(z_names,plenum,mixers,loop,zone_hvac):
    n_p = len(plenum['name'])
    n_z = len(z_names)
    plenum['in_zones']=[[] for i in range(n_p)]
    plenum['zone_index']=[[] for i in range(n_p)]
    n_pi = 0
    for i in range(n_p):
        n_pi +=(len(plenum['inlets'][i])+1)  #plenum zone feeds itself (explains +1)
        
    n_np = n_z - n_pi
    zone_2_plenum = np.zeros((n_p+n_np,n_z),'int32')
    for i in range(n_p):
        for j in range(len(plenum['inlets'][i])):
            h = zone_hvac['return_'].index(plenum['inlets'][i][j])
            z = z_names.index(zone_hvac['name'][h])
            plenum['in_zones'][i].append(z)
            zone_2_plenum[i,z] = 1
        z = z_names.index(plenum['zone'][i])
        zone_2_plenum[i,z] = 1
        plenum['zone_index'][i] = z
    k = -1
    for i in range(n_z):
        if not np.any(zone_2_plenum[:,i]):
            k = k+1
            zone_2_plenum[n_p+k,i] = 1  #single zone plenum for those connecting directly to mixer
    n_m = len(mixers['name'])
    plenum_2_loop = np.zeros((n_m,n_p+n_np),'int32')
    for i in range(n_m):  #mixer inlets are connected to zone return air or plenum outlet. mixer outlet is connected to air_loop.demand_outlet & return_path.outlet
        k = loop['demand_outlet'].index(mixers['outlet'][i])
        for j in range(len(mixers['inlets'][i])):
            try:
                h = zone_hvac['return_'].index(mixers['inlets'][i][j])
                z = z_names.index(zone_hvac['name'][h])
                jj = np.nonzero(zone_2_plenum[:,z]>0)
                plenum_2_loop[k,jj] = 1
            except ValueError:
                p = plenum['outlet'].index(mixers['inlets'][i][j])
                plenum_2_loop[k,p] = 1
    zone_2_loop = plenum_2_loop@zone_2_plenum
    zone_loop = [None for i in range(n_z)]
    zone_plenum = [None for i in range(n_z)]
    for i in range(n_z):
        for j in range(n_m):
            if zone_2_loop[j,i]==1:
                zone_loop[i] = j
        for j in range(n_p):
            if zone_2_plenum[j,i]==1:
                zone_plenum[i] = j
    return zone_loop,zone_plenum,plenum


def setup_nodes(components,loop,d_or_s):
    '''create a list of nodes in the order they are connected
        Identify which branch/loop the node is on, and which # component on that branch it is'''
    nodes = {}
    equip = {}
    if len(loop['name'])>0:
        nf = ['name','branch','loop','bypass']
        for x in nf:
            nodes[x] = [] 
        n = len(loop['name'])
        nodes['inlet_node'] = [0 for i in range(n)]
        nodes['outlet_node'] = [0 for i in range(n)]
        ef = ['name','type','component_number','inlet','outlet_name','loop','bypass']
        for x in ef:
            equip[x] = []
        n = -1
        n2 = -1
        component_loaded = [False for x in range(len(components['name']))]
        for pl in range(len(loop['name'])):
            if d_or_s=='d':
                eob = [loop['demand_inlet'][pl]] #eob is end-of-branch
                outlet = loop['demand_outlet'][pl]
            else:
                eob = [loop['supply_inlet'][pl]]  #eob is end-of-branch
                outlet = loop['supply_outlet'][pl]
            nodes['inlet_node'][pl] = n+1
            while len(eob)>0:
                j =0
                while j<len(eob):  #identify if any branch starts at the current end-of-line
                    try:
                        c = [i for i, x in enumerate(components['inlet']) if x == eob[j]]
                        eob.pop(j)
                        if any([True for i in range(len(c)) if component_loaded[c[i]]==False]):
                            break
                    except ValueError:
                        j +=1
                        pass
                b = min([components['branch_number'][c[x]] for x in range(len(c))])
                b_components = [i for i, x in enumerate(components['branch_number']) if x == b]
                for i in b_components:
                    try:
                        prev_node =nodes['name'].index(components['inlet'][i])
                    except ValueError:
                        n +=1
                        nodes['name'].append(components['inlet'][i])
                        nodes['branch'].append(b)
                        nodes['loop'].append(pl)
                        nodes['bypass'].append(False)
                        prev_node = n
                    try:
                        prev_equip = equip['name'].index(components['name'][i])
                    except ValueError:
                        n2 +=1
                        equip['name'].append(components['name'][i])
                        equip['type'].append(components['type'][i])
                        equip['component_number'].append(i)
                        equip['inlet'].append(prev_node)
                        equip['outlet_name'].append(components['outlet'][i])
                        equip['loop'].append(pl)
                        equip['bypass'].append(False)
                        prev_equip = n2
                    if components['bypass'][i]:
                        nodes['bypass'][prev_node] = True
                        equip['bypass'][prev_equip] = True
                m = [i for i, x in enumerate(b_components) if components['type'][x] == 'mixer']
                if len(m)>0:
                    e = equip['name'].index(components['name'][b_components[m[0]]])
                    c_inlets = [i for i, x in enumerate(components['name']) if x == equip['name'][e]]
                    in_nodes = []
                    for j in range(len(c_inlets)):
                        in_nodes.append(nodes['name'].index(components['inlet'][c_inlets[j]]))
                    equip['inlet'][e] = in_nodes
                for i in b_components:
                    component_loaded[i] = True
                s = [i for i, x in enumerate(b_components) if components['type'][x] == 'splitter']
                if len(s)>0:
                    eob.extend([components['outlet'][b_components[i]] for i in s])
                else:
                    eob.append(components['outlet'][b_components[-1]])
                eob = [x for i, x in enumerate(eob) if i == eob.index(x)] #uniqe end of branches only (keep if index i is the first time it appears in eob list)
                try: #remove eob if it is outlet for supply.demand loop
                    i = eob.index(outlet)
                    eob.pop(i)
                except ValueError:
                    pass
                for i in range(len(eob)): #move mixer last. There can only be one mixer on a loop, so not a problem this way this ensures other equipment upstream of mixer is simulated first
                    try:
                        c = components['inlet'].index(eob[i])
                        if components['type'][c]=='mixer':
                            eob.append(eob.pop(i))
                    except ValueError:
                        pass
                if len(eob)==0:
                    try:
                        i = nodes['name'].index(outlet)
                    except ValueError: #exit node doesn't exist, create it
                        n +=1
                        nodes['name'].append(outlet)
                        nodes['branch'].append(b)
                        nodes['loop'].append(pl)
                        nodes['bypass'].append(False)
                        nodes['outlet_node'][pl] = n
        equip['outlet'] = [None for x in range(n2+1)]
        for k in range(len(nodes['name'])):
            upstream = [i for i, x in enumerate(equip['outlet_name']) if x ==nodes['name'][k]]
            for j in upstream:
                if equip['type'][j].find('splitter')>=0:
                    outlets = [components['outlet'][i] for i , x in enumerate(components['name']) if x == equip['name'][j]]
                    out_nodes = []
                    for l in outlets:
                        out_nodes.append(nodes['name'].index(l))
                    equip['outlet'][j] = out_nodes
                else:
                    equip['outlet'][j]= k
    return nodes,equip


def import_plant(objects):
    def branch_2_node(connect,branches,a,b,c):
        for i in range(len(connect['name'])):
            b_num = branches['name'].index(connect[a][i])
            connect[a][i] = branches[b][b_num]
            ports = connect[c][i]
            for j in range(len(ports)):
                b2 = branches['name'].index(ports[j])
                ports[j] = branches[a][b2]
            connect[c][i] = ports
        return connect
    components = {}
    loop = {}
    loop = load_object(['PlantLoop','CondenserLoop'],objects,0,'array')
    n = len(loop['name'])
    loop['loop_order'] = [i for i in range(n)]
    if n>0:
        loop['fluid_density'] = [0 for i in range(n)]
        loop['type'] = [[] for i in range(n)]
        loop['branches'] = [[] for i in range(n)]
        loop['exit_temperature'] = [0 for i in range(n)]
        loop['temperature_difference'] = [0 for i in range(n)]
        branch_list = load_object(['BranchList'],objects,1,'')
        for i in range(n):
            if loop['fluid'][i]=='water':
                loop['fluid_density'][i] = 997
            else:
                print('need density for plant loop fluid other than water')
            loop['branches'][i] = branch_list[loop['demand_branch_list'][i]]['branches']
            loop['branches'][i].extend(branch_list[loop['supply_branch_list'][i]]['branches'])
        k_obj = objects['Sizing:Plant']
        for k in range(len(k_obj)):
            try:
                i = loop['name'].index(k_obj[k]['name'])
                loop['type'][i] = k_obj[k]['value'][0]
                loop['exit_temperature'][i] = read_num(k_obj[k]['value'][1])
                loop['temperature_difference'][i] = read_num(k_obj[k]['value'][2])
            except ValueError:
                pass
        branches = load_object(['Branch'],objects,4,'array')
        n = len(branches['name'])
        branches['loop'] = [0 for i in range(n)]
        branches['inlet'] = []
        branches['outlet'] = []
        for j in range(n):
            for l in range(len(loop['branches'])):
                try:
                    l_b = loop['branches'][l].index(branches['name'][j])
                    branches['loop'][j] = l
                    break
                except ValueError:
                    pass
            branches['inlet'].append(branches['component_inlet'][j][0])
            branches['outlet'].append(branches['component_outlet'][j][-1])

        splitters = load_object(['Connector:Splitter'],objects,1,'array')
        splitters = branch_2_node(splitters,branches,'inlet','outlet','outlets')
        mixers = load_object(['Connector:Mixer'],objects,1,'array')
        mixers = branch_2_node(mixers,branches,'outlet','inlet','inlets')
        components = read_components(branches,mixers,splitters)
    return loop, components
