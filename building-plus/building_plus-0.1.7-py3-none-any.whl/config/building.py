"""
Defines Building-related constants.
"""
BUILD_NAMES = ['FullServiceRestaurant',    #1
                'Hospital',    #2
                'LargeHotel',    #3
                'LargeOffice',    #4
                'MediumOffice',    #5
                'MidriseApartment',    #6
                'OutPatient',    #7
                'PrimarySchool',    #8
                'QuickServiceRestaurant',    #9
                'SecondarySchool',    #10
                'SmallHotel',    #11
                'SmallOffice',    #12
                'Stand-aloneRetail',    #13
                'StripMall',    #14
                'SuperMarket',    #15
                'Warehouse']     #16

CLIMATE_NAMES = {'1A':'1A_USA_FL_MIAMI', '2A':'2A_USA_TX_HOUSTON', '2B': '2B_USA_AZ_PHOENIX', '3A': '3A_USA_GA_ATLANTA',
                    '3Bcoast': '3B_USA_CA_LOS_ANGELES', '3B': '3B_USA_NV_LAS_VEGAS', '3C': '3C_USA_CA_SAN_FRANCISCO',
                    '4A': '4A_USA_MD_BALTIMORE', '4B': '4B_USA_NM_ALBUQUERQUE', '4C': '4C_USA_WA_SEATTLE',
                    '5A': '5A_USA_IL_CHICAGO-OHARE', '5B': '5B_USA_CO_BOULDER', '6A': '6A_USA_MN_MINNEAPOLIS',
                    '6B': '6B_USA_MT_HELENA', '7A': '7A_USA_MN_DULUTH', '8A': '8A_USA_AK_FAIRBANKS'}

IDF_FIELDS = {
    'Building': ['north_axis','terrain','load_tol','temp_tol','solar_distribution','max_warm_up','min_warm_up',],
    'Site:Location': ['latitude','longitude','timezone','elevation'],
    'RunPeriod':['m1','d1','m2','d2','day','weather_special','weather_daylight','weekend_holiday','rain_inidcators','snow_indicators','repeat'],
    'RunPeriodControl:SpecialDays':['start','duration','type'],
    'Material': ['roughness','thickness','conductivity','density','specheat','thermal_absorptance','solar_absorptance','visible_absorptance',],
    'Material:NoMass': ['roughness','thermal_resistance','thermal_absorptance','solar_absorptance','visible_absorptance',],
    'WindowMaterial:SimpleGlazingSystem': ['u_factor','solar_heat_gain','visible_transmittance',],
    'WindowMaterial:Glazing': ['optical_data_type','spectral_data_set','thickness','solar_transmittance','reflectance_front','reflectance_back','transmittance_visible','reflectance_visible_front','reflectance_visible_back','transmittance_infrared','emittance_front','emittance_back','thermal_conductivity','dirt_correction','solar_diffusing',],
    'WindowMaterial:Gas': ['gas','gap_thickness',],
    'BuildingSurface:Detailed':['surf_type','construct','zone','boundary','object'],
    'InternalMass':['construct','zone'],
    'FenestrationSurface:Detailed':['surf_type','construct','surf_name','object','view_factor','shading','frame_name','multiplier'],
    'WindowProperty:FrameAndDivider':['width','projection_out','projection_in','conductance','conductance_ratio_edge_center','solar_absoprtance','visible_absorptance','emissivity','divider_type','divider_width','horizontal_dividers','vertical_dividers','divider_projection_out','divider_projection_in','divider_conductance','divider_conductance_ratio','divider_solar_absoprtnace','divider_visible_absorptance','divider_emissivity'],
    'Zone':['relative_north','x_origin','y_origin','z_origin','zone_type','multiplier','ceil_height','volume','floor_area','inside_convection','outside_convection','incl_in_total_area'],
    'Pump:VariableSpeed':['inlet','outlet','design_flow','design_head','design_power','motor_eff','fluid_ineff_frac','c1','c2','c3','c4','design_min_flow','control_type','schedule'],
    'Pump:ConstantSpeed':['inlet','outlet','design_flow','design_head','design_power','motor_eff','fluid_ineff_frac','control_type','schedule'],
    'Chiller:Electric:EIR':['capacity','COP_ref','chilled_water_temperature_ref','condenser_water_temperature_ref','chilled_water_flow_ref','condenser_water_flow_ref','capacity_temperature_curve','electric_in_out_temperature_curve','electric_in_out_part_load_curve','min_part_load','max_part_load','opt_part_load','min_unload_ratio','chilled_water_inlet','chilled_water_outlet','condenser_inlet','condenser_outlet','condenser_type','fan_power_ratio','frac_power_2_condenser','min_chilled_water_temperature','flow_mode','heat_recovery_flow','heat_recovery_inlet','heat_recovery_outlet','sizing_factor'],
    'Chiller:Electric:ReformulatedEIR':['capacity','COP_ref','chilled_water_temperature_ref','condenser_water_temperature_ref','chilled_water_flow_ref','condenser_water_flow_ref','capacity_temperature_curve','electric_in_out_temperature_curve','electric_in_out_curve_type','electric_in_out_part_load_curve','min_part_load','max_part_load','opt_part_load','min_unload_ratio','chilled_water_inlet','chilled_water_outlet','condenser_inlet','condenser_outlet','frac_power_2_condenser','min_chilled_water_temperature','flow_mode','heat_recovery_flow','heat_recovery_inlet','heat_recovery_outlet','sizing_factor'],
    'Boiler:HotWater':['fuel','capacity','efficiency','eff_temperature_curve','normalized_eff_curve','design_water_temperature','design_flow_rate','min_part_load','max_part_load','optimal_part_load','water_inlet','water_outlet','max_water_temperature','flow_mode','parasitic_electric_load','sizing_factor'],
    'Humidifier:Steam:Electric':['schedule','flow_capacity','max_power','fan_power','standby_power'],
    'AirLoopHVAC:UnitaryHeatCool':['schedule','inlet','outlet','fan_schedule','max_temperature','cooling_air_flow','heating_air_flow','no_load_air_flow','thermostat','fan_type','fan_name','fan_location','heat_coil_type','heat_coil','cool_coil_type','cool_coil','dehumid_control','reheat_type','reheat_name'],
    'CoolingTower:SingleSpeed':['water_inlet','water_outlet','water_flow','air_flow','fan_power','UA','free_convect_flow','free_convect_factor','free_convect_UA','free_convect_UA_factor','performance_method','heat_reject_capacity','nominal_capacity','free_convect_capacity','free_convect_size_factor','des_inlet_dry_bulb','des_inlet_wet_bulb','des_approach_temp','des_range_temp','basin_heater_capacity','basin_heater_setpoint','basin_heater_schedule','evap_loss_mode','evap_loss_factor','drift_loss','blowdown_mode','blowdown_ratio','blowdown_makeup_schedule','supply_water_tank','outdoor_air_inlet','capacity_control','number_of_cells','cell_control','cell_min_water_frac','cell_max_water_frac','sizing_factor'],
    'WaterHeater:Mixed':['tank_volume','temperature_schedule','deadband_temperature_dif','max_temperature','heater_control_type','heater_maximum_capacity','heater_minimum_capacity','heater_ignition_minimum_flow','heater_ignition_delay','heater_fuel','heater_efficiency','part_load_curve','off_cycle_fuel_use','off_cycle_fuel_type','off_cycle_frac2tank','on_cycle_fuel_use','on_cycle_fuel_type','on_cycle_frac2tank','ambient_temp_indicator','ambient_temp_schedule','ambient_temp_zone','ambient_temp_outdoor_node','off_cycle_loss2ambient','off_cycle_loss2zone','on_cycle_loss2ambient','on_cycle_loss2zone','peak_use_flow','use_flow_schedule','cold_water_supply_temp_schedule','use_side_inlet','use_side_outlet','use_side_effectiveness','source_side_inlet','source_side_outlet','source_side_effectiveness','use_side_design_flow','source_side_design_flow','indirect_water_heating_recovery_time'],
    'Controller:WaterCoil':['control_variable','action','actuator_variable','sensor_node','actuator_node','tolerance','max_actuated_flow','min_actuated_flow'],
    'SetpointManager:Scheduled':['control_variable','schedule','node'],
    'SetpointManager:MixedAir':['control_variable','reference_setpoint_node','fan_inlet_node','fan_outlet_node','node'],
    'SetpointManager:SingleZone:Reheat':['control_variable','min_temp','max_temp','zone','zone_node','zone_inlet_node','node'],
    'SetpointManager:SingleZone:Humidity:Minimum':['node','control_zone_node'],
    'SetpointManager:SingleZone:Humidity:Maximum':['node','control_zone_node'],
    'SetpointManager:FollowOutdoorAirTemperature':['control_variable','ref_temp_type','offset_temperature','max_temperature','min_temperature','node'],
    'SetpointManager:OutdoorAirReset':['control_variable','setpoint_at_low_temp','low_temp','setpoint_at_high_temp','high_temp','node'],
    'ZoneControl:Thermostat':['zone','control_type_schedule','control_type','control_name'],
    'ZoneControl:Humidistat':['zone','humidify_schedule','dehumidify_schedule'],
    'ThermostatSetpoint:SingleHeating':['heating'],
    'ThermostatSetpoint:SingleCooling':['cooling'],
    'ThermostatSetpoint:SingleHeatingOrCooling':['heating'],
    'ThermostatSetpoint:DualSetpoint':['heating','cooling'],
    'DesignSpecification:OutdoorAir':['method','flow_person','flow_area','flow_zone'],
    'Sizing:Zone':['cooling_T_method','cooling_T_des','cooling_dT_des','heating_T_method','heating_T_des','heating_dT_des','cooling_w_des','heating_w_des','outdoor_air_object','heating_sizing','cooling_sizing','cooling_flow_des_method','cooling_flow_des','cooling_min_flow_per_area','cooling_min_flow','cooling_min_frac','heating_flow_des_method','heating_flow_des','heating_min_flow_per_area','heating_min_flow','heating_min_frac'],
    'ZoneHVAC:UnitHeater':['schedule','inlet','outlet','fan_type','fan_name','max_air_flow','heat_coil_type','heat_coil','fan_schedule','fan_without_heating','max_hot_water','min_hot_water','tolerance','availability'],
    'ZoneHVAC:PackagedTerminalAirConditioner':['schedule','inlet','outlet','outdoor_air_type','outdoor_air','cooling_air_flow','heating_air_flow','no_load_air_flow','cooling_outdoor_air_flow','heating_outdoor_air_flow','no_load_outdoor_air_flow','fan_type','fan_name','heat_coil_type','heat_coil','cool_coil_type','cool_coil','fan_placement','fan_schedule'],
    'ZoneHVAC:FourPipeFanCoil':['schedule','capacity_control','max_air_flow','low_flow_ratio','medium_flow_ratio','outdoor_air_flow','outdoor_air_schedule','inlet','outlet','outdoor_air_mixer_type','outdoor_air_mixer','fan_type','fan_name','cool_coil_type','cool_coil','max_cold_water','min_cold_water','cooling_tolerance','heat_coil_type','heat_coil','max_hot_water','min_hot_water','heating_tolerance'],
    'Fan:ConstantVolume':['schedule','fan_efficiency','pressure_rise','flow_rate','motor_efficiency','motor_frac','inlet','outlet','end_use'],
    'Fan:ZoneExhaust':['schedule','fan_efficiency','pressure_rise','flow_rate','inlet','outlet','end_use'],
    'Fan:VariableVolume':['schedule','fan_efficiency','pressure_rise','flow_rate','method','min_flow_frac','min_flow_rate','motor_efficiency','motor_frac','a1','a2','a3','a4','a5','inlet','outlet','end_use'],
    'Fan:OnOff':['schedule','fan_efficiency','pressure_rise','flow_rate','motor_efficiency','motor_frac','inlet','outlet','power_speed_curve','efficiency_speed_curve','end_use'],
    'Curve:Quadratic':['a0','a1','a2','min_x','max_x'],
    'Curve:Cubic':['a0','a1','a2','a3','min_x','max_x'],
    'Curve:Biquadratic':['a0','a1','a2','b1','b2','ab','min_x','max_x','min_y','max_y'],
    'Curve:Bicubic':['a0','a1','a2','b1','b2','ab','a3','b3','aab','abb','min_x','max_x','min_y','max_y'],
    'Curve:ChillerPartLoadWithLift':['a0','a1','a2','b1','b2','ab','a3','b3','aab','abb','aabb','cb3','min_x','max_x','min_y','max_y'],
    'Coil:Cooling:DX:TwoSpeed':['schedule','rated_capacity','rated_sensible_heat_ratio','rated_COP','rated_air_flow','static_air_pressure','inlet','outlet','capacity_v_temperature_curve','capacity_v_flow_curve','energy_input_v_temperature_curve','energy_input_v_flow_curve','part_load_curve','rated_capacity2','rated_sensible_heat_ratio2','rated_COP2','rated_air_flow2','capacity_v_temperature_curve2','energy_input_v_temperature_curve2','condenser_inlet'],
    'Coil:Cooling:DX:SingleSpeed':['schedule','rated_capacity','rated_sensible_heat_ratio','rated_COP','rated_air_flow','rated_fan_power_per_volume','inlet','outlet','capacity_v_temperature_curve','capacity_v_flow_curve','energy_input_v_temperature_curve','energy_input_v_flow_curve','part_load_curve','min_ambient_temp',],
    'Coil:Cooling:Water':['schedule','rated_water_flow','rated_air_flow','water_inlet_temperature','air_inlet_temperature','air_outlet_temperature','air_inlet_humididty','air_outlet_humidity','inlet_water','outlet_water','inlet','outlet','analysis_type','heat_exchanger_configuration'],
    'Coil:Cooling:Water:DetailedGeometry':['schedule','rated_water_flow','tube_area_outside','tube_area_inside','fin_area','min_airflow_area','coil_depth','fin_diameter','fin_thickness','tube_id','tube_od','tube_conductivity','fin_conductivity','fin_spacing','tube_spacing','tube_rows','tubes_per_row','inlet_water','outlet_water','inlet','outlet'],
    'Coil:Heating:Fuel':['schedule','fuel','efficiency','capacity','inlet','outlet','temperature_setpoint'],
    'Coil:Heating:Water':['schedule','UA','rated_water_flow','inlet_water','outlet_water','inlet','outlet','input_method','capacity','water_inlet_temperature','air_inlet_temperature','water_outlet_temperature','air_outlet_temperature','air_water_convection_ratio'],
    'Coil:Heating:Electric':['schedule','efficiency','capacity','inlet','outlet','setpoint_node'],
    'Site:WaterMainsTemperature':['schedule','outdoor_average','max_temp_difference'],
    'EnvironmentalImpactFactors':['district_cool_cop','steam_efficiency','carbon_factor_n2o','carbon_factor_ch4','carbon_factor_co2'],
    'CoilSystem:Cooling:DX':['schedule','inlet','outlet','sensor','coil_type','coil_name'],
    'ZoneInfiltration:DesignFlowRate':['zone_name','schedule','method','nominal_set','per_area','per_ext_area','changes_per_hr','c1','t1','v1','v2'],
    'ZoneMixing':['receiving_zone','schedule','mix_type','nominal_set','per_area','per_ext_area','changes_per_area','source_zone'],
    'People':['zone_name','schedule','method','people','people_per_area','area_per_person','radiant','sensible_frac','activity','co2_rate','comfort_warnings','radiant_calc','surface_name','work_eff','insulation_method','insulation_calk_schedule','insulation_schedule','velocity_schedule','comfort_model'],
    'Lights':['zone_name','schedule','method','light_level','watt_area','watt_person','return_frac','radiant','visible','replacable','end_use','calc_from_plenum'],
    'ElectricEquipment':['zone_name','schedule','method','equip_level','watt_area','watt_person','latent','radiant','lost','end_use'],
    'GasEquipment':['zone_name','schedule','method','equip_level','watt_area','watt_person','latent','radiant','lost','end_use'],
    'Exterior:Lights':['schedule','nominal','control','category'],
    'Exterior:FuelEquipment':['fuel','schedule','nominal','category'],
    'Refrigeration:Case':['schedule','zone','rated_ambient_T','rated_ambient_RH','capacity_per_length','latent_heat_ratio','runtime_fraction','length','temperature','latent_credit_curve_type','latent_credit_curve_name','fan_power_per_length','operating_fan_power_per_length','standard_lighting_per_unit_length','installed_standard_lighting_per_unit_length','light_schedule','light_to_case','anti_sweat_heater_per_length','minimum_anti_sweat_per_length','anti_sweat_control','humidity_at_zero_percent','height','anti_sweat_heat_to_case','defrost_power_per_length','defrost_type','defrost_schedule','defrost_drip_down_schedule','defrost_curve_type','defrost_curve_name','return_air_frac','restock_schedule','case_credit_fraction_schedule'],
    'Refrigeration:CompressorRack':['heat_reject_location','design_COP','COP_curve','fan_power','fan_power_temperature_curve','condensor_type','water_inlet','water_outlet','water_loop_type','water_condensor_temperature_schedule','water_flow_rate','water_max_flow','water_max_outlet_T','water_min_inlet_T','evap_condenser_schedule','evap_condenser_effectiveness','evap_condenser_air_flow','basin_heater_capacity','basin_heater_setpoint','water_pump_power','water_supply_tank','condenser_air_inlet','end_use','case_name',],
    'Refrigeration:CaseAndWalkInList':['case'],
    'WaterUse:Equipment':['end_use_category','peak_flow','flow_schedule','target_temperature_schedule','hot_supply_temperature_schedule','cold_supply_temperature_schedule','zone','sensible_frac_schedule','latent_frac_schedule'],
    'WaterUse:Connections':['inlet','outlet','supply_tank','reclaimation_tank','hot_schedule','cold_schedule','drain_HX_type','drain_HX_destination','drain_HX_UA','equip_name'],
    'AirLoopHVAC':['controller','manager','supply_flow','branch_list','connector_list','supply_inlet','demand_outlet','demand_inlet','supply_outlet'],
    'BranchList':['branches'],
    'Sizing:Parameters':['cooling_sizing_factor','averaging_windows'],
    'SizingPeriod:DesignDay':['month','day','day_type','drybulb_temp','drybulb_range','db_range_modifier_type','db_range_modifier_schedule','humidity_type','wetbulb_temp','humidity_schedule','humidity_at_max','enthalpy_at_max','wetbulb_range','pressure','windspeed','winddir','rain_indicate','snow_indicate','daylight_savings_indicate','beam_solar_day_indicate','diffuse_solar_day_schedule','clear_sky_depth_beam','clear_sky_depth_diffuse','clearness'],
    'Sizing:System':['sizing_load_type','outdoor_flow','heating_max_flow','T_preheat','w_preheat','T_precool','w_precool','Tsupply_c','Tsupply_h','zone_sum_type','cool_all_outdoor_air','heat_all_outdoor_air','w_supply_c','w_supply_h','cooling_supply_flow_rate_method','cooling_supply_flow_rate','cooling_supply_flow_rate_area','cool_frac_autosized','cooling_supply_flow_rate_per_capacity','heating_supply_flow_rate','heating_supply_flow_rate_area','heat_frac_autosized','heating_supply_flow_rate_per_capacity','outdoor_air_method','cool_capacity_method','cool_capacity','cool_capacity_area','frac_autosize_cooling','heat_capacity_method','heat_capacity','heat_capacity_area','frac_autosize_heating','control_method'],
    'Branch':['pressure_curve','component_type','component_name','component_inlet','component_outlet'],
    'AirLoopHVAC:SupplyPath':['inlet','component_type','component_name'],
    'AirLoopHVAC:ReturnPath':['outlet','component_type','component_name'],
    'AirLoopHVAC:ZoneSplitter':['inlet','outlets'],
    'AirLoopHVAC:ZoneMixer':['outlet','inlets'],
    'AirLoopHVAC:ReturnPlenum':['zone','zone_node','outlet','induced_air','inlets'],
    'ZoneHVAC:EquipmentConnections':['hvac_equipment','inlet','exhaust','node_name','return_'],
    'ZoneHVAC:EquipmentList':['e_type','e_name','cool_sequence','heat_sequence'],
    'AirTerminal:SingleDuct:Uncontrolled':['schedule','inlet','max_flow'],
    'AirTerminal:SingleDuct:VAV:Reheat':['schedule','outlet_damper','inlet','max_flow','min_method','min_frac','min_flow','flow_frac_schedule','reheat_coil_type','reheat_coil_name','max_flow_water','min_flow_water','outlet','tolerance','damper_action','max_reheat_flow_per_area','max_reheat_frac'],
    'ZoneHVAC:AirDistributionUnit':['outlet','terminal_type','terminal'],
    'AirLoopHVAC:OutdoorAirSystem':['controller_list','equipment_list','manager_list'],
    'AirLoopHVAC:ControllerList':['controller_type','controller_name'],
    'Controller:OutdoorAir':['relief_outlet','return_air','mixed_air','actuator_node','min_flow','max_flow','economizer_control','economizer_action','economizer_max_T','economizer_max_h','economizer_max_dp','enthalpy_limit_curve','economizer_min_T','lockout','min_limit_type','min_air_schedule','min_frac_schedule','max_frac_schedule','mechanical_controller_name'],
    'AvailabilityManagerAssignmentList':['manager_type','manager_name'],
    'AvailabilityManager:NightCycle':['schedule','fan_schedule','control_type','thermostat_tolerance','runtime_control_type','runtime'],
    'AvailabilityManager:Scheduled':['schedule'],
    'PlantLoop':['fluid','user_fluid','operation_scheme','setpoint_node','max_temperature','min_temperature','max_flow_rate','min_flow_rate','loop_volume','supply_inlet','supply_outlet','supply_branch_list','supply_connector_list','demand_inlet','demand_outlet','demand_branch_list','demand_connector_list','load_scheme'],
    'CondenserLoop':['fluid','user_fluid','operation_scheme','setpoint_node','max_temperature','min_temperature','max_flow_rate','min_flow_rate','loop_volume','supply_inlet','supply_outlet','supply_branch_list','supply_connector_list','demand_inlet','demand_outlet','demand_branch_list','demand_connector_list','load_scheme'],
    'Connector:Mixer':['outlet','inlets'],
    'Connector:Splitter':['inlet','outlets'],
} 

EIO_FIELDS = {}
EIO_FIELDS['AirTerminal:SingleDuct:Uncontrolled'] = {'location':['hvac','terminals','name'],
                                                    'Design Size Maximum Air Flow Rate [m3/s]':['max_flow'],
                                                    'User-Specified Maximum Air Flow Rate [m3/s]':['max_flow']}
EIO_FIELDS['AirTerminal:SingleDuct:VAV:Reheat'] ={'location':['hvac','terminals','name'],
                                                   'Design Size Maximum Air Flow Rate [m3/s]':['max_flow'],
                                                   'Design Size Constant Minimum Air Flow Fraction':['min_frac'],
                                                   'Design Size Minimum Air Flow Rate [m3/s]':['min_flow'],
                                                   'Design Size Maximum Flow per Zone Floor Area during Reheat [m3/s-m2]':['max_reheat_flow_per_area'],
                                                   'Design Size Maximum Flow Fraction during Reheat []':['max_reheat_frac'],
                                                   'Design Size Maximum Reheat Water Flow Rate [m3/s]':['max_flow_water'],
                                                   'User-Specified Constant Minimum Air Flow Fraction':['min_frac']}

EIO_FIELDS['Coil:Heating:Water'] = {'location':['coils_heating'],
                                    'Design Size Rated Capacity [W]':['design_capacity'],
                                    'Design Size Maximum Water Flow Rate [m3/s]':['rated_water_flow'],
                                    'Design Size U-Factor Times Area Value [W/K]':['UA'],
                                    'Nominal Total Capacity {W}':['capacity']}
EIO_FIELDS['Coil:Heating:Fuel'] = {'location':['coils_heating'],
                                   'Design Size Nominal Capacity [W]':['capacity']}

EIO_FIELDS['Coil:Heating:Electric'] = {'location':['coils_heating'],
                                       'Design Size Nominal Capacity [W]':['capacity']}
EIO_FIELDS['Coil:Cooling:Water'] = {'location':['coils_cooling'],
                                    'Design Size Design Coil Load [W]':['design_capacity'],
                                    'Design Size Design Water Flow Rate [m3/s]':['rated_water_flow'],
                                    'Design Size Design Air Flow Rate [m3/s]':['rated_air_flow'],
                                    'User-Specified Design Air Flow Rate [m3/s]':['rated_air_flow'],
                                    'Design Size Design Inlet Air Temperature [C]':['air_inlet_temperature'],
                                    'Design Size Design Inlet Water Temperature [C]':['water_inlet_temperature'],
                                    'Design Size Design Outlet Air Temperature [C]':['air_outlet_temperature'],
                                    'Design Size Design Inlet Air Humidity Ratio':['air_inlet_humididty'],
                                    'Design Size Design Outlet Air Humidity Ratio':['air_outlet_humididty'],
                                    'Nominal Total Capacity {W}':['capacity'],
                                    'Nominal Sensible Capacity {W}':['sensible_capacity'],
                                    'Nominal Latent Capacity {W}':['latent_capacity'],
                                    'Nominal Sensible Heat Ratio':['sensible_heat_ratio'],
                                    'Nominal Coil UA Value {W/C}':['UA'],
                                    'Nominal Coil Surface Area {m2}':['area']}
EIO_FIELDS['Coil:Cooling:Water:DetailedGeometry'] = {'location':['coils_cooling'],
                                    'Design Size Design Coil Load [W]':['design_capacity'],
                                    'Design Size Maximum Water Flow Rate [m3/s]':['rated_water_flow'],
                                    'Design Size Number of Tubes per Row':['tubes_per_row'],
                                    'Design Size Fin Diameter [m]':['fin_diameter'],
                                    'Design Size Minimum Airflow Area [m2]':['min_airflow_area'],
                                    'Design Size Fin Surface Area [m2]':['fin_area'],
                                    'Design Size Total Tube Inside Area [m2]':['tube_area_inside'],
                                    'Design Size Tube Outside Surface Area [m2]':['tube_area_outside'],
                                    'Design Size Coil Depth [m]':['coil_depth'],
                                    'Nominal Total Capacity {W}':['capacity'],
                                    'Nominal Sensible Capacity {W}':['sensible_capacity'],
                                    'Nominal Latent Capacity {W}':['latent_capacity'],
                                    'Nominal Sensible Heat Ratio':['sensible_heat_ratio']}
EIO_FIELDS['Coil:Cooling:DX:TwoSpeed'] = {'location':['coils_cooling'],
                                          'Design Size High Speed Rated Air Flow Rate [m3/s]':['rated_air_flow'],
                                          'Design Size High Speed Gross Rated Total Cooling Capacity [W]':['rated_capacity'],
                                          'Design Size High Speed Rated Sensible Heat Ratio':['rated_sensible_heat_ratio'],
                                          'Design Size Low Speed Rated Air Flow Rate [m3/s]':['rated_air_flow2'],
                                          'Design Size Low Speed Gross Rated Total Cooling Capacity [W]':['rated_capacity2'],
                                          'Design Size Low Speed Gross Rated Sensible Heat Ratio':['rated_sensible_heat_ratio2']}
EIO_FIELDS['Coil:Cooling:DX:SingleSpeed'] = {'location':['coils_cooling'],
                                            'Design Size Rated Air Flow Rate [m3/s]':['rated_air_flow'],
                                            'Design Size Rated Total Cooling Capacity [W]':['rated_capacity'],
                                            'Design Size Gross Rated Total Cooling Capacity [W]':['rated_capacity'],
                                            'Design Size Rated Sensible Heat Ratio':['rated_sensible_heat_ratio'],
                                            'Design Size Gross Rated Sensible Heat Ratio':['rated_sensible_heat_ratio']}
EIO_FIELDS['AirLoopHVAC'] = {'location':['hvac','loop','name'],
                            'Design Supply Air Flow Rate [m3/s]':['max_flow']}

EIO_FIELDS['AirLoopHVAC:UnitaryHeatCool'] = {'location':['unitary_heat_cool','name'],
                                            'Supply Air Flow Rate [m3/s]':['max_air_flow'],
                                            'Supply Air Flow Rate During Heating Operation [m3/s]':['heating_air_flow'],
                                            'Supply Air Flow Rate During Cooling Operation [m3/s]':['cooling_air_flow'],
                                            'Supply Air Flow Rate When No Cooling or Heating is Needed [m3/s]':['no_load_air_flow'],
                                            'Nominal Heating Capacity [W]':['capacity_heating'],
                                            'Nominal Cooling Capacity [W]':['capacity_cooling'],
                                            'Maximum Supply Air Temperature from Supplemental Heater [C]':['max_temperature'],
                                            'Fraction of Supply Air Flow That Goes Through the Controlling Zone':['frac_2_zone']}
EIO_FIELDS['Controller:OutdoorAir'] = {'location':['hvac','outdoor_air','control'],
                                       'Maximum Outdoor Air Flow Rate [m3/s]':['max_flow'],
                                       'Minimum Outdoor Air Flow Rate [m3/s]':['min_flow']}

EIO_FIELDS['Fan:ConstantVolume'] = {'location':['fans'],
                           'Design Size Maximum Flow Rate [m3/s]':['flow_rate']}
EIO_FIELDS['Fan:VariableVolume'] = {'location':['fans'],
                           'Design Size Maximum Flow Rate [m3/s]':['flow_rate']}
EIO_FIELDS['Fan:OnOff'] = {'location':['fans'],
                           'Design Size Maximum Flow Rate [m3/s]':['flow_rate']}
EIO_FIELDS['PlantLoop'] = {'location':['plant_loop','name'],
                               'Maximum Loop Flow Rate [m3/s]':['max_flow_rate'],
                               'Plant Loop Volume [m3]':['loop_volume'],
                               'Condenser Loop Volume [m3]':['loop_volume']}
EIO_FIELDS['CondenserLoop'] = {'location':['plant_loop','name'],
                               'Maximum Loop Flow Rate [m3/s]':['max_flow_rate'],
                               'Plant Loop Volume [m3]':['loop_volume'],
                               'Condenser Loop Volume [m3]':['loop_volume']}
EIO_FIELDS['Pump:VariableSpeed'] = {'location':['pump'],
                                    'Design Flow Rate [m3/s]':['design_flow'],
                                    'Design Power Consumption [W]':['design_power']}
EIO_FIELDS['Pump:ConstantSpeed'] = {'location':['pump'],
                                    'Design Flow Rate [m3/s]':['design_flow'],
                                    'Design Power Consumption [W]':['design_power']}
EIO_FIELDS['WaterHeater:Mixed'] = {'location':['water_heater'],
                                   'Use Side Design Flow Rate [m3/s]':['use_side_design_flow'],
                                   'Source Side Design Flow Rate [m3/s]':['source_side_design_flow']}
EIO_FIELDS['Controller:WaterCoil'] = {'location':['controller','name'],
                                      'Maximum Actuated Flow [m3/s]':['max_actuated_flow'],
                                      'Controller Convergence Tolerance':['tolerance']}
EIO_FIELDS['Chiller:Electric:ReformulatedEIR'] = {'location':['chiller'],
                                      'Design Size Reference Chilled Water Flow Rate [m3/s]':['chilled_water_flow_ref'],
                                      'Design Size Reference Capacity [W]':['capacity'],
                                      'Design Size Reference Condenser Water Flow Rate [m3/s]':['condenser_water_flow_ref'],
                                      'Design Size Reference Condenser Fluid Flow Rate  [m3/s]':['condenser_water_flow_ref']}
EIO_FIELDS['Chiller:Electric:EIR'] = {'location':['chiller'],
                                      'Design Size Reference Chilled Water Flow Rate [m3/s]':['chilled_water_flow_ref'],
                                      'Design Size Reference Capacity [W]':['capacity'],
                                      'Design Size Reference Condenser Water Flow Rate [m3/s]':['condenser_water_flow_ref'],
                                      'Design Size Reference Condenser Fluid Flow Rate  [m3/s]':['condenser_water_flow_ref']}
EIO_FIELDS['Boiler:HotWater'] = {'location':['boiler'],
                                 'Design Size Nominal Capacity [W]':['capacity'],
                                 'Design Size Design Water Flow Rate [m3/s]':['design_flow_rate']}
EIO_FIELDS['CoolingTower:SingleSpeed'] = {'location':['cooling_tower'],
                                                   'Design Water Flow Rate [m3/s]':['water_flow'],
                                                   'Fan Power at Design Air Flow Rate [W]':['fan_power'],
                                                   'Design Air Flow Rate [m3/s]':['air_flow'],
                                                   'U-Factor Times Area Value at Design Air Flow Rate [W/C]':['UA'],
                                                   'Free Convection Regime Air Flow Rate [m3/s]':['free_convect_flow'],                                                   
                                                   'Free Convection U-Factor Times Area Value [W/K]':['free_convect_UA']}
EIO_FIELDS['CoolingTower:TwoSpeed'] = {'location':['cooling_tower'],
                                                   'Design Water Flow Rate [m3/s]':['water_flow'],
                                                   'Fan Power at Design Air Flow Rate [W]':['fan_power'],
                                                   'Design Air Flow Rate [m3/s]':['air_flow'],
                                                   'U-Factor Times Area Value at Design Air Flow Rate [W/C]':['UA'],
                                                   'Free Convection Regime Air Flow Rate [m3/s]':['free_convect_flow'],                                                   
                                                   'Free Convection U-Factor Times Area Value [W/K]':['free_convect_UA']}
EIO_FIELDS['CoolingTower:VariableSpeed:Merkel'] = {'location':['cooling_tower'],
                                                   'Design Water Flow Rate [m3/s]':['water_flow'],
                                                   'Fan Power at Design Air Flow Rate [W]':['fan_power'],
                                                   'Design Air Flow Rate [m3/s]':['air_flow'],
                                                   'U-Factor Times Area Value at Design Air Flow Rate [W/C]':['UA'],
                                                   'Free Convection Regime Air Flow Rate [m3/s]':['free_convect_flow'],                                                   
                                                   'Free Convection U-Factor Times Area Value [W/K]':['free_convect_UA']}
EIO_FIELDS['Humidifier:Steam:Electric'] = {'location':['humidifiers'],
                                           'Design Size Nominal Capacity Volume [m3/s]':['flow_capacity'],
                                           'User-Specified Nominal Capacity Volume [m3/s]':['flow_capacity'],
                                           'Design Size Rated Power [W]':['max_power'],
                                           'User-Specified Rated Power [W]':['max_power']}
EIO_FIELDS['ZoneHVAC:UnitHeater'] = {'location':['unitary_sys','name'],
                                     'Design Size Maximum Supply Air Flow Rate [m3/s]':['max_air_flow']}
EIO_FIELDS['ZoneHVAC:FourPipeFanCoil'] = {'location':['unitary_sys','name'],
                                          'Design Size Maximum Supply Air Flow Rate [m3/s]':['max_air_flow'],
                                          'Design Size Maximum Hot Water Flow [m3/s]':['max_cold_water'],
                                          'Design Size Maximum Cold Water Flow [m3/s]':['max_hot_water']}
EIO_FIELDS['ZoneHVAC:PackagedTerminalAirConditioner'] = {'location':['unitary_sys','name'],
                                                         'Design Size Cooling Supply Air Flow Rate [m3/s]':['cooling_air_flow'],
                                                         'Design Size Heating Supply Air Flow Rate [m3/s]':['heating_air_flow'],
                                                         'Design Size No Load Supply Air Flow Rate [m3/s]':['no_load_air_flow'],
                                                         'Supply Air Flow Rate When No Cooling or Heating is Needed [m3/s]':['no_load_air_flow'],
                                                         'Design Size Outdoor Air Flow Rate During Cooling Operation [m3/s]':['cooling_outdoor_air_flow'],
                                                         'Design Size Outdoor Air Flow Rate During Heating Operation [m3/s]':['heating_outdoor_air_flow'],
                                                         'Design Size Outdoor Air Flow Rate When No Cooling or Heating is Needed [m3/s]':['no_load_outdoor_air_flow']}