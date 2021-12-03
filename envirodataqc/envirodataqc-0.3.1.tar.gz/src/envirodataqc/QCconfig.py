'''
Defines quality control settings for different variables
- Section 1 defines ranges for different variables
- Section 2 associated a name with the range
'''

#-------------- Section 1 -------------#

#Test ranges
#Units - N/A
#Ref - XXXX
testVar = {
    'good':{
        'range':[(0,5),(14,16)],
        'rate':[(0,1.4)],
        'flat':[(0,15)]
    },
    'suspicious':{
        'range':[(11,13)],
        'rate':[(1.4,2)],
        'flat':[(15,30)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[]
    }
}

#2m air temperature
#Units - C, C/min, minutes
#Ref - XXXX
airT = {
    'good':{
        'range':[(-30,45)],
        'rate':[(-1.4,1.4)],
        'flat':[(0,20)]
    },
    'suspicious':{
        'range':[(-40,-30),(45,50)],
        'rate':[(1.4,2),(-2,-1.4)],
        'flat':[(20,35)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[]
    }
}

#2m humidity in open air
#Units - %, %/min, minutes
#Ref - XXXX
rh = {
    'good':{
        'range':[(5,100)],
        'rate':[(-4.4,4.4)],
        'flat':[(0,15)]
    },
    'suspicious':{
        'range':[(0,5),(100,105)],
        'rate':[(4.4,5),(-5,-4.4)],
        'flat':[(15,30)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[0,100]
    }
}

#2m barometric pressure in open air
#This could potentially be a function of elevation
#Units - mb, mb/min, minutes
#Ref - XXXX
bp = {
    'good':{
        'range':[(700,1050)],
        'rate':[(-1,1)],
        'flat':[(0,40)]
    },
    'suspicious':{
        'range':[],
        'rate':[],
        'flat':[(40,60)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[0]
    }
}

#Wind Speed
#Units - m/s, m/s per min, minutes
#Ref - XXXX
ws = {
    'good':{
        'range':[(0,40)],
        'rate':[(-6,6)],
        'flat':[(0,60)]
    },
    'suspicious':{
        'range':[],
        'rate':[],
        'flat':[(60,90)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[0]
    }
}

#Wind Gust
#Units - m/s, m/s per min, minutes
#Ref - XXXX
wg = {
    'good':{
        'range':[(10,60)],
        'rate':[(-10,10)],
        'flat':[] #Two days without a gust OK
    },
    'suspicious':{
        'range':[],
        'rate':[],
        'flat':[]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[0]
    }
}

#Wind Direction
#Units - mb, mb/min, minutes
#Ref - XXXX
wd = {
    'good':{
        'range':[(0,360)],
        'rate':[(-360,360)],
        'flat':[(0,15)]
    },
    'suspicious':{
        'range':[],
        'rate':[],
        'flat':[(15,30)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[]
    }
}

#Solar Radiation
#Units - W/m2, W/m2 per min, minutes
#Ref - XXXX
swrad = {
    'good':{
        'range':[(0,1500)],
        'rate':[(-160,160)],
        'flat':[(0,15)]
    },
    'suspicious':{
        'range':[],
        'rate':[],
        'flat':[(15,30)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[0]
    }
}

#Precipitation rate
#Units - in/hr, none, minutes
#Ref - Fiebrich et al. 2010 for the most part
precip = {
    'good':{
        'range':[(0,6)],
        'rate':[(-0.6,0.6)],
        'flat':[(0,60)]
    },
    'suspicious':{
        'range':[(6,24)],
        'rate':[],
        'flat':[(60,90)]
    },
    'ignore_vals':{
        'range':[],
        'rate':[],
        'flat':[0]
    }
}



#---------------- Section 2 ----------------
qcsettings = {
    'testVar':testVar,
    'air_temperature':airT,
    'humidity':rh,
    'air_pressure':bp,
    'wind_speed':ws,
    'wind_direction':wd,
    'solar_radiation':swrad,
    'precipitation':precip
    }