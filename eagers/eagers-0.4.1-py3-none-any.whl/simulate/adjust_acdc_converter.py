#TODO generalize so that when it crosses 0 on ac/dc conversion it switches the efficiency term
def adjust_acdc_converter(gen,solution,ac_power,dc_power,t):
    acdc_i = [i for i in range(len(gen)) if gen[i]['type']=='ACDCConverter']
    if len(acdc_i)>0:
        ac2dc = gen[acdc_i[0]]['output']['dc'][-1][0]
        dc2ac = gen[acdc_i[0]]['output']['e'][-1][-1]
        name = gen[acdc_i[0]]['name']
        if not dc_power is None:
            
            if solution['dispatch'][acdc_i[0]][t+1]<0: # power is going DC to AC (Value is in AC)
                #positive dc_power means more dc_power converted to ac electricity
                solution['dispatch'][acdc_i[0]][t+1] -= dc_power
                solution['generator_state'][name][t] -= dc_power
                ac_power = dc_power*dc2ac #power discrepancy is in AC --> adjust to DC
            else:
                #positive dc_power means less ac_power converted to dc electricity
                ac_power = dc_power/ac2dc # change in inverter power is increasing/decreasing the amount of DC supply (power discrepancy is in AC --> adjust to DC)
                solution['dispatch'][acdc_i[0]][t+1] -= ac_power
                solution['generator_state'][name][t] -= ac_power
            return ac_power
        if not ac_power is None: #An AC battery supplying a DC bus (unlikely but here for completion)

            if solution['dispatch'][acdc_i[0]][t+1]<0: # power is going DC to AC (Value is in AC)
                #positive ac_power means less dc_power converted to ac electricity
                dc_power = ac_power/dc2ac #(power discrepancy is in DC --> adjust to AC)
                solution['dispatch'][acdc_i[0]][t+1] += dc_power
                solution['generator_state'][name][t] += dc_power
            else:
                #positive ac_power means more ac_power converted to dc electricity
                solution['dispatch'][acdc_i[0]][t+1] += ac_power
                solution['generator_state'][name][t] += ac_power
                dc_power = ac_power*ac2dc #(power discrepancy is in DC --> adjust to AC)
            return dc_power