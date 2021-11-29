def wind_speed_calc(wind,height,terrain):
    d_met = 270 #boundary layer thickness at meterological site
    z_met = 10 #elevation of met site
    a_met = 0.14 #coefficient at met site
    if terrain =='city':
            a = .33
            d = 460
    elif terrain =='urban':
            a = .22
            d = 370
    elif terrain =='ocean':
            a = 0.1
            d = 210
    elif terrain =='flat':
            a = 0.14
            d = 270
    elif terrain =='rough':
            a = 0.22
            d = 370
    else:
         print('what is terrain?')
    wind_speed = [wind*(d_met/z_met)**a_met*(max(0,h)/d)**a for h in height]
    return wind_speed