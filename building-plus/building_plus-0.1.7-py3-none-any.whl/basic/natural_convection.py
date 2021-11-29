def natural_convection(normal,dT,nat_buoyancy,method):
    n = len(dT)
    if method =='DOE-2':
        # h = [max(.1,1.77*abs(dT[i])**(1/4)) for i in range(n)] # page 538 https://www.researchgate.net/publication/264308543_COMPARISON_OF_ENERGYPLUS_AND_DOE-2_DETAILED_WINDOW_HEAT_TRANSFER_MODELS
        h = [max(.1,1.31*abs(dT[i])**(1/3)) for i in range(n)] #ASHRAE vertical surface %https://www.nrel.gov/docs/fy12osti/55787.pdf page 18
    elif method =='Detailed' or method =='BLAST' or method =='TARP':
        ## TARP method %A) simple buoyancy
        h = [max(0.1,1.31*abs(dT[i])**(1/3))for i in range(n)] #ASHRAE vertical surface
        for i in range(len(dT)):
            cos_phi = normal[i][2]/(normal[i][0]**2 + normal[i][1]**2 + normal[i][2]**2)**.5 #portion of surface pointed upwards
            if (normal[i][2]<-1e-3 and dT[i]>0) or (normal[i][2]>1e-3 and dT[i]<0): #stable
                h[i] = max(0.1,1.81*abs(dT[i])**(1/3)/(1.382-abs(cos_phi))) #Walton for tilted surfaces
            elif (normal[i][2]<-1e-3 and dT[i]<0) or (normal[i][2]>1e-3 and  dT[i]>0): #unstable
                h[i] = max(0.1,9.482*abs(dT[i])**(1/3)/(7.283-abs(cos_phi))) #Walton for tilted surfaces
    else:
        ## other methods see pg 105 of reference
        print('need the adaptive convection algorithm')
    return h