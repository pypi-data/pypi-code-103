# -*- coding: utf-8 -*-
"""
Created on Wed Nov 10 14:38:33 2021

@author: nkdi
"""

def output_field(u0,v0,w0,params,TurbOptions = None):
    
    import numpy as np
    import struct    
    
    if TurbOptions is None:
        TurbOptions = {'FileFormat':0}               
    
    # APPLY MEAN AND VARIANCE CORRECTION
    if 'Umean' in TurbOptions:
        MFFWS = TurbOptions['Umean']
    else:
        MFFWS = 0
        
    if 'TI_u' in TurbOptions:        
        TI_U = TurbOptions['TI_u']
        TI_V = TurbOptions['TI_v']
        TI_W = TurbOptions['TI_w']
                
        u = (u0 - np.mean(u0))*(TI_U*MFFWS/np.std(u0))
        v = (v0 - np.mean(v0))*(TI_V*MFFWS/np.std(v0))
        w = (w0 - np.mean(w0))*(TI_W*MFFWS/np.std(w0))    
    else:
        # Just zero-mean
        u = (u0 - np.mean(u0))
        v = (v0 - np.mean(v0))
        w = (w0 - np.mean(w0))        
    
    
    # BOX DIMENSIONS AND SPACING
    if 'Nx' in params:
        Nx = params['Nx']
    else:
        Nx = u.shape[0]
    if 'Ny' in params:
        Ny = params['Ny']
    else:
        Ny = u.shape[1]
    if 'Nz' in params:
        Nz = params['Nz']
    else:
        Nz = u.shape[2]             

    dx = params['dx']
    dy = params['dy']
    dz = params['dz']           
        
    # APPLY SHEAR CORRECTION IF NECESSARY                    
    
    if 'ShearLaw' in TurbOptions:
        ShearLaw = TurbOptions['ShearLaw']
    else:
        ShearLaw = 'pwr'
        
    if 'zHub' in TurbOptions:
        zHub = TurbOptions['zHub']
    else:
        zHub = dz*(Nz-1)/2
            
    zGoffset = 0.0 # Can in principle be an input
    z1   = zHub - zGoffset - dz*(Nz-1)/2 #  this is the bottom of the grid
    zbox = np.arange(Nz)*dz + z1
    
    if ShearLaw == 'pwr':
        alpha = TurbOptions['alpha']
        zOffset = zHub
        z0 = np.exp(( - np.log(zOffset)*(1/zOffset)**alpha)/(1 - (1/zOffset)**alpha)) # Roughness length [m]
        ShearMultiplier = np.tile((zbox/zHub)**alpha, (Nx,Ny,1))
    elif ShearLaw == 'log':
        z0 = TurbOptions['z0']
        zOffset = zHub
        ShearMultiplier = np.tile(np.log(zbox/z0)/np.log(zOffset/z0), (Nx,Ny,1))
        
    u = u + MFFWS*ShearMultiplier
    
    # ROTATE FIELDS IF NECESSARY
    if 'Yaw' in TurbOptions:
        YawAngle = TurbOptions['Yaw']
    else:
        YawAngle = 0
        
    if 'Pitch' in TurbOptions:
        PitchAngle = TurbOptions['Pitch']
    else:
        PitchAngle = 0    
        
    if 'Roll' in TurbOptions:
        PitchAngle = TurbOptions['Roll']
    else:
        RollAngle = 0      
    
    if abs(YawAngle) + abs(PitchAngle) + abs(RollAngle) > 0:
        pi = np.pi
        c0 = np.cos(YawAngle*pi/180)
        s0 = np.sin(YawAngle*pi/180)
        c1 = np.cos(PitchAngle*pi/180)
        s1 = np.sin(PitchAngle*pi/180)
        c2 = np.cos(RollAngle*pi/180)
        s2 = np.sin(RollAngle*pi/180)    
        
        RotationMatrix = np.zeros((3,3))
        RotationMatrix[0,0] = c0*c1
        RotationMatrix[0,1] = c0*s1*s2 - s0*c2
        RotationMatrix[0,2] = c0*s1*c2 + s0*s2
        RotationMatrix[1,0] = s0*c1
        RotationMatrix[1,1] = s0*s1*s2 + c0*c2
        RotationMatrix[1,2] = s0*s1*c2 - c0*s2
        RotationMatrix[2,0] = -s1
        RotationMatrix[2,1] = c1*s2
        RotationMatrix[2,2] = c1*c2
        
        urot = RotationMatrix[0,0]*u + RotationMatrix[0,1]*v + RotationMatrix[0,2]*w
        vrot = RotationMatrix[1,0]*u + RotationMatrix[1,1]*v + RotationMatrix[1,2]*w
        wrot = RotationMatrix[2,0]*u + RotationMatrix[2,1]*v + RotationMatrix[2,2]*w
        
        u = urot
        v = vrot
        w = wrot             
            
    if 'FileFormat' not in TurbOptions:
        FileFormat = 0
    else:
        FileFormat = TurbOptions['FileFormat']      
        
    if 'BaseName' in params:
        BaseName = params['BaseName']
    else:
        BaseName = 'turb_py'
        
    if 'SeedNo' in params:
        SeedNo = params['SeedNo']
    else:
        SeedNo = 1       
        
    if 'SaveToFile' in params:
        SaveToFile = params['SaveToFile']
    else:
        SaveToFile = 0
        
    
    if (SaveToFile == 1) | (SaveToFile == True):
        
        if (FileFormat == 0) | (FileFormat == 'Hawc2') | (FileFormat == 'Mann'):
            u.reshape(Nx*Ny*Nz).astype('single').tofile(BaseName + '_' + str(SeedNo) + '_u' + '.bin',sep = '')
            v.reshape(Nx*Ny*Nz).astype('single').tofile(BaseName + '_' + str(SeedNo) + '_v' + '.bin',sep = '')
            w.reshape(Nx*Ny*Nz).astype('single').tofile(BaseName + '_' + str(SeedNo) + '_w' + '.bin',sep = '')
        elif (FileFormat == 'Bladed') | (FileFormat == 'wnd') | (FileFormat == 'TurbSim'):                
        
            Scale    = 0.00001*MFFWS*np.asarray([TI_U*100, TI_V*100, TI_W*100])
            Offset   = np.array([MFFWS,0,0])
            
            
            uOut = np.asarray((u - Offset[0])/Scale[0], dtype = 'int16')
            vOut = np.asarray((v - Offset[1])/Scale[1], dtype = 'int16')
            wOut = np.asarray((w - Offset[2])/Scale[2], dtype = 'int16')
            
            OutFileName = str(BaseName + '_' + str(SeedNo) + '.wnd')
            wnd_file = open(OutFileName,'wb')
            
            # HEADER OF THE .WND FILE
            wnd_file.write(struct.pack('<h',-99))             # ID - must be -99
            wnd_file.write(struct.pack('<h',4))               # ID2 - must be 4
            wnd_file.write(struct.pack('<i', 3))              # number of components (should be 3)
            wnd_file.write(struct.pack('<f',0.0))             # latitude (deg)
            wnd_file.write(struct.pack('<f',z0))              # Roughness length (m)
            wnd_file.write(struct.pack('<f',zOffset))         # Reference height (m) = Z(1) + GridHeight / 2.0
            wnd_file.write(struct.pack('<f',TI_U*100))        # Turbulence Intensity of u component (%)
            wnd_file.write(struct.pack('<f',TI_V*100))        # Turbulence Intensity of v component (%)
            wnd_file.write(struct.pack('<f',TI_W*100))        # Turbulence Intensity of w component (%)
            wnd_file.write(struct.pack('<f',dz))              # delta z in m 
            wnd_file.write(struct.pack('<f',dy))              # delta y in m 
            wnd_file.write(struct.pack('<f',dx))              # delta x in m 
            wnd_file.write(struct.pack('<i',int(Nx/2)))       # half the number of time steps (points in longitudinal direction)
            wnd_file.write(struct.pack('<f',MFFWS))           # mean full-field wind speed
            wnd_file.write(struct.pack('<f',0.0))             # zLu - unused variable
            wnd_file.write(struct.pack('<f',0.0))             # yLu - unused variable
            wnd_file.write(struct.pack('<f',0.0))             # xLu - unused variable
            wnd_file.write(struct.pack('<i',0))               # _ - unused variable
            wnd_file.write(struct.pack('<i',0))               # RandSeed1 - unused variable
            wnd_file.write(struct.pack('<i',Nz))              # number of points in vertical direction
            wnd_file.write(struct.pack('<i',Ny))              # number of points in horizontal direction
            wnd_file.write(struct.pack('<i',0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i',0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i',0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i',0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i',0))               # Unused variable - for BLADED
            wnd_file.write(struct.pack('<i',0))               # Unused variable - for BLADED
            
            
            # WRITE WIND FIELD DATA OUT
            Clockwise = True # Should be loaded from the summary file in principle
            if Clockwise == True:
                y_ix = np.flip(np.arange(Ny))
            else:
                y_ix = np.arange(Ny)
            
            for it in range(Nx):
                for iz in range(Nz):
                    for iy in y_ix:
                        wnd_file.write(struct.pack('<h',uOut[it,iy,iz]))
                        wnd_file.write(struct.pack('<h',vOut[it,iy,iz]))
                        wnd_file.write(struct.pack('<h',wOut[it,iy,iz]))
            
            wnd_file.close()
    
    return u,v,w