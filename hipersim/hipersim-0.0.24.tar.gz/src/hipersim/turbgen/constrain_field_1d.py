# -*- coding: utf-8 -*-
"""
Created on Mon May  3 11:39:55 2021

@author: nkdi
"""

def constrain_field_1d(Constraints, Component = None,c = None, BaseName = 'Turb', \
                        alphaepsilon = 1,L = 30,Gamma = 3, Nx = 8192, Ny = 32, Nz = 32, \
                        dx = 1,dy = 1,dz = 1,SaveToFile = 0, UseNormalization = 0, TurbOptions = None):
    import numpy as np
    import time
    
    '''
    Parse inputs 
    '''
    if Component is None:
        Component = 'u'
        print('Warning: the turbulence component to be constrained was not specified.')
        print('Assuming u-component.')
    
    if TurbOptions is None:
        SeedNo = 0
        HighFreqComp = 0        
    else:
        if 'SeedNo' not in TurbOptions:
            SeedNo = 0
        else:
            SeedNo = TurbOptions['SeedNo']
            
        if 'HighFreqComp' not in TurbOptions:
            HighFreqComp = 0
        else:
            HighFreqComp = TurbOptions['HighFreqComp']
    
    if (c is None):
        if Component == 'u':
            if 'Udatafile' not in TurbOptions:
                print('Source turbulence boxes for constrained simulation do not exist.')
                print('Generating turbulence boxes:')
                '''
                ======================================================================================
                If not given as inputs, load turbulence boxes from files or generate them if necessary
                ======================================================================================'''
                from hipersim.turbgen.generate_field import generate_field 
                # from . generate_field import generate_field
                # from generate_field import generate_field 
                u,v,w = generate_field(BaseName,alphaepsilon,L,Gamma,SeedNo,Nx,Ny,Nz,dx,dy,dz, \
                                        HighFreqComp, SaveToFile = 0)
                c = u
            else:
                '''
                Load source turbulence boxes 
                '''
                c = np.fromfile(TurbOptions['Udatafile'],dtype = 'single').reshape((Nx,Ny,Nz))
        if Component == 'v':
            if 'Vdatafile' not in TurbOptions:
                print('Source turbulence boxes for constrained simulation do not exist.')
                print('Generating turbulence boxes:')
                '''
                ======================================================================================
                If not given as inputs, load turbulence boxes from files or generate them if necessary
                ======================================================================================'''
                from hipersim.turbgen.generate_field import generate_field 
                # from . generate_field import generate_field
                # from generate_field import generate_field 
                u,v,w = generate_field(BaseName,alphaepsilon,L,Gamma,SeedNo,Nx,Ny,Nz,dx,dy,dz, \
                                        HighFreqComp, SaveToFile = 0)
                c = v
            else:
                '''
                Load source turbulence boxes 
                '''
                c = np.fromfile(TurbOptions['Vdatafile'],dtype = 'single').reshape((Nx,Ny,Nz))
        if Component == 'w':
            if 'Wdatafile' not in TurbOptions:
                print('Source turbulence boxes for constrained simulation do not exist.')
                print('Generating turbulence boxes:')
                '''
                ======================================================================================
                If not given as inputs, load turbulence boxes from files or generate them if necessary
                ======================================================================================'''
                from hipersim.turbgen.generate_field import generate_field 
                # from . generate_field import generate_field
                # from generate_field import generate_field 
                u,v,w = generate_field(BaseName,alphaepsilon,L,Gamma,SeedNo,Nx,Ny,Nz,dx,dy,dz, \
                                        HighFreqComp, SaveToFile = 0)
                c = w
            else:
                '''
                Load source turbulence boxes 
                '''
                c = np.fromfile(TurbOptions['Wdatafile'],dtype = 'single').reshape((Nx,Ny,Nz))
    
    ''' 
    ===============================================
    APPLY CONSTRAINTS
    ==============================================='''
    
    '''
    ====================================================================
     COMPUTE MANN TENSOR VALUES, THEN IFFT TO GET CORRELATIONS
    ===================================================================='''
    print('Computing Mann tensor / correlation arrays for constrained simulation:')
    
    from hipersim.turbgen.manntensor import manntensorcomponents    
    # from . manntensor import manntensorcomponents
    tstart = time.time()
    R0 = np.zeros((Nx,2*Ny,2*Nz), dtype = 'cfloat')
    
    '''
    The u-v, and v-w components are not considered because Rho_uv and Rho_vw
    are zero in the Mann turbulence model
    '''
    pi = np.pi
    k1sim = np.concatenate([np.arange(0,Nx),np.arange(-Nx,0)])*(pi/(Nx*dx))
    k2sim = np.concatenate([np.arange(0,Ny),np.arange(-Ny,0)])*(pi/(Ny*dy))
    k3sim = np.concatenate([np.arange(0,Nz),np.arange(-Nz,0)])*(pi/(Nz*dz))
    
    k2simgrid,k3simgrid = np.meshgrid(k2sim,k3sim)
    '''
    Only half of the wave numbers are considered, it is considered that
    the correlation will be symmetric about k1 = 0 
    '''
    if Component == 'u':
        for ik1 in range(Nx):    
            Phi11ij, __, __, __, __, __ = manntensorcomponents(k1sim[ik1]*np.ones(k2simgrid.shape),k2simgrid,k3simgrid,Gamma,L,alphaepsilon,2)
            R0[ik1,:,:] = np.fft.ifft2(Phi11ij,axes = (0,1))
    if Component == 'v':
        for ik1 in range(Nx):    
            __, Phi22ij, __, __, __, __ = manntensorcomponents(k1sim[ik1]*np.ones(k2simgrid.shape),k2simgrid,k3simgrid,Gamma,L,alphaepsilon,2)
            R0[ik1,:,:] = np.fft.ifft2(Phi22ij,axes = (0,1))
    if Component == 'w':
        for ik1 in range(Nx):    
            __, __, Phi33ij, __, __, __ = manntensorcomponents(k1sim[ik1]*np.ones(k2simgrid.shape),k2simgrid,k3simgrid,Gamma,L,alphaepsilon,2)
            R0[ik1,:,:] = np.fft.ifft2(Phi33ij,axes = (0,1))
                   
    R = np.zeros((2*Nx,Ny,Nz))
    for ik2 in range(Ny):
        for ik3 in range(Nz):
            ''' 
            !!! Needs to be checked !!!
            Changing the choice of where we apply the complex conjugate ends up with 
            somewhat different constrained fields '''
            R[:,ik2,ik3] = np.real(np.fft.ifft(np.concatenate([np.conj(R0[:,ik2,ik3]), np.flip((R0[:,ik2,ik3]))])))
    
    R = R[:Nx,:Ny,:Nz]    
    R = R/R[0,0,0]
    
    del R0 # Clear memory from unnecessary variables        
            
    t1 = time.time()
    print('Correlation computations complete')
    print('Time elapsed is ' + str(t1-tstart))
    
    '''
    ================================================================
     Compute distances, normalize wind fields and constraint fields
    ================================================================'''
    
    
    if UseNormalization == 1:
        varUdata = np.var(c)
        muUdata = np.mean(c)
        stdUdata = np.sqrt(varUdata)
        Unorm = (c - muUdata)/varUdata
        ConstraintValuesUNorm = (Constraints[:,3] - muUdata)/stdUdata
    else:
        ConstraintValuesUNorm = Constraints[:,3]
        Unorm = c
    
    #del u, v, w
    
    '''
    ==========================================
     ASSEMBLE CONSTRAINT COVARIANCE MATRIX
    =========================================='''
    print('Populating covariance matrix for the constraints:')
    Clocx = np.rint(Constraints[:,0]/dx)
    Clocy = np.rint(Constraints[:,1]/dy)
    Clocz = np.rint(Constraints[:,2]/dz)
    '''
    ---------------------------------
     Eliminate overlapping constraints
    ---------------------------------'''
    ClocA = np.concatenate([np.atleast_2d(Clocx), np.atleast_2d(Clocy), np.atleast_2d(Clocz)]).T
    __,ClocIndex = np.unique(ClocA,axis=0,return_index = True)
    Constraints = Constraints[ClocIndex,:]
    Clocx = Clocx[ClocIndex]
    Clocy = Clocy[ClocIndex]
    Clocz = Clocz[ClocIndex]
    ConstraintValuesUNorm = ConstraintValuesUNorm[ClocIndex]
    Nconstraints = Constraints.shape[0]
    
    '''
    ---------------------------------------------
     Eliminate constraints too close to each other
    ---------------------------------------------'''
    Xdist = np.dot(np.atleast_2d(Constraints[:,0]).T,np.ones([1,Nconstraints])) - np.dot(np.ones([Nconstraints,1]),np.atleast_2d(Constraints[:,0]))
    Ydist = np.dot(np.atleast_2d(Constraints[:,1]).T,np.ones([1,Nconstraints])) - np.dot(np.ones([Nconstraints,1]),np.atleast_2d(Constraints[:,1]))
    Zdist = np.dot(np.atleast_2d(Constraints[:,2]).T,np.ones([1,Nconstraints])) - np.dot(np.ones([Nconstraints,1]),np.atleast_2d(Constraints[:,2]))
    
    Rdist = np.sqrt(Xdist**2 + Ydist**2 + Zdist**2)
    Rlimit = max( [L/10, min([dx, dy, dz])])
    Rexceed = (Rdist > 0) & (Rdist < Rlimit)
    ValidDistIndex = np.full((Rdist.shape[0]),True,dtype = 'bool')
    for i in range(Nconstraints):
        if np.any(Rexceed[i,:i]):
            Rexceed[i,:] = 0
            Rexceed[:,i] = 0
            ValidDistIndex[i] = False
    Constraints = Constraints[ValidDistIndex,:]
    Clocx = Clocx[ValidDistIndex].astype('int')
    Clocy = Clocy[ValidDistIndex].astype('int')
    Clocz = Clocz[ValidDistIndex].astype('int')
    ConstraintValuesUNorm = ConstraintValuesUNorm[ValidDistIndex]
    Nconstraints = Constraints.shape[0]
    
    del Rdist, Rexceed, ValidDistIndex
    
    
    '''
    -----------------------------
     Assemble u-v-w-correlation matrix
    -----------------------------'''
    CorrCMannU = np.zeros((Nconstraints,Nconstraints))
    
    for iC in range(Nconstraints):
        xloci = Clocx[iC]
        yloci = Clocy[iC]
        zloci = Clocz[iC]
        xlocCij = np.abs(xloci-Clocx).astype('int')
        ylocCij = np.abs(yloci-Clocy).astype('int')
        zlocCij = np.abs(zloci-Clocz).astype('int')
        
        CorrUUij = R[xlocCij,ylocCij,zlocCij]

    
        # CorrUUij = np.zeros(Nconstraints)
        # CorrVVij = np.zeros(Nconstraints)
        # CorrWWij = np.zeros(Nconstraints)
        # CorrUWij = np.zeros(Nconstraints)
        # for jC in range(Nconstraints):
        #     CorrUUij[jC] = Ruu[xlocCij[jC],ylocCij[jC],zlocCij[jC]]
        #     CorrVVij[jC] = Rvv[xlocCij[jC],ylocCij[jC],zlocCij[jC]]
        #     CorrWWij[jC] = Rww[xlocCij[jC],ylocCij[jC],zlocCij[jC]]
        #     CorrUWij[jC] = Ruw[xlocCij[jC],ylocCij[jC],zlocCij[jC]]
    
        CorrCMannU[:Nconstraints,iC] = CorrUUij
        CorrCMannU[iC,:Nconstraints] = CorrUUij  
           
        
    t2 = time.time()
    print('Constraint-constraint covariance matrix has been assembled')
    print('Time elapsed is ' + str(t2-t1))
    
    '''
    =========================================================
     APPLY CONSTRAINT EQUATIONS TO COMPUTE THE RESIDUAL FIELD
    =========================================================
     Using eq.(2) from Dimitrov & Natarajan (2016) to compute 
     the residual field which is to be added to the unconstrained
     field in order to obtain the constrained result.
    
     Due to memory limitations, eq. (2) is evaluated in batches intended
     to avoid the need of fully assembling the first term in the equation,
     which is a matrix with size (Nx*Ny*Nz)x(Nconstraints).
     First, the product of the second and third term is evaluated, 
     then it is multiplied piecewise to a subset of the rows of the 
     first term.
    '''
    print('Applying constraints...')
    Ucontemporaneous = Unorm[Clocx,Clocy,Clocz]
    
    '''
     Computing the product of the second and third terms in eq.(2) in 
     Dimitrov & Natarajan (2016)
    '''
    
    CConstU = np.linalg.solve(CorrCMannU, (ConstraintValuesUNorm - Ucontemporaneous))
    # CConstUVW = np.dot(np.linalg.inv(CorrCMannUVW), ConstraintValuesUVWNorm - UVWcontemporaneous)
    
    CConstU = np.atleast_2d(CConstU[:Nconstraints]).T
    del CorrCMannU
    
    R = R.reshape(Nx*Ny*Nz)
    
    ygrid, xgrid, zgrid = np.meshgrid(np.arange(Ny),np.arange(Nx),np.arange(Nz))
    xvect = xgrid.reshape(Nx*Ny*Nz)
    yvect = ygrid.reshape(Nx*Ny*Nz)
    zvect = zgrid.reshape(Nx*Ny*Nz)
    
    del xgrid, ygrid, zgrid
    
    ures = np.zeros(Nx*Ny*Nz)
    
    # Npoints = Nx*Ny*Nz
    
    for iC in range(Nconstraints):
        # dxCov = np.abs(xvect - Clocx[iC])
        # dyCov = np.abs(yvect - Clocy[iC])
        # dzCov = np.abs(zvect - Clocz[iC])
        dlinear = np.abs(xvect - Clocx[iC])*(Ny*Nz) + np.abs(yvect - Clocy[iC])*Ny + np.abs(zvect - Clocz[iC])
        CorrUUi = R[dlinear]
        ures+= CorrUUi*CConstU[iC]
        
    Uconstrained = Unorm + np.reshape(ures,(Nx,Ny,Nz))
    
    
    '''
    OLDER IMPLEMENTATION - SIGNIFICANTLY FASTER IN MATLAB BUT SLOW IN PYTHON
    DUE TO ARRAY INDEXING SPEED '''
    
    # Uconstrained = np.zeros((Nx,Ny,Nz))
    # Vconstrained = np.zeros((Nx,Ny,Nz))
    # Wconstrained = np.zeros((Nx,Ny,Nz))   
    
    # CorrUUxyz = np.zeros((Nx,Nconstraints))
    # CorrVVxyz = np.zeros((Nx,Nconstraints))
    # CorrUVxyz = np.zeros((Nx,Nconstraints))
    # CorrVWxyz = np.zeros((Nx,Nconstraints))
    # CorrUWxyz = np.zeros((Nx,Nconstraints))
    # CorrWWxyz = np.zeros((Nx,Nconstraints)) 
    
    # for yloc in range(Ny):
    #     for zloc in range(Nz):
    #         xloc = np.arange(Nx)
    #         dyCov = np.abs(yloc - Clocy).astype('int')
    #         dzCov = np.abs(zloc - Clocz).astype('int')
    #         '''
    #         !!! This loop needs optimization !!!
    #         '''
    #         for iC in range(Nconstraints):
    #             dxCov = np.abs(xloc - Clocx[iC])
    #             CorrUUxyz[:,iC] = Ruu[dxCov,dyCov[iC],dzCov[iC]]
    #             CorrVVxyz[:,iC] = Rvv[dxCov,dyCov[iC],dzCov[iC]]
    #             CorrUWxyz[:,iC] = Ruw[dxCov,dyCov[iC],dzCov[iC]]
    #             CorrWWxyz[:,iC] = Rww[dxCov,dyCov[iC],dzCov[iC]]
    
    #         '''
    #           Computing the product of the first term in eq. (2) with the
    #           second and third terms - for one point in the y-z plane at a
    #           time.
    #         '''        
    #         CtermUYZ = np.dot(CorrUUxyz,CConstU) + np.dot(CorrUVxyz,CConstV) + np.dot(CorrUWxyz,CConstW) # Residual field term - u
    #         CtermVYZ = np.dot(CorrUVxyz,CConstU) + np.dot(CorrVVxyz,CConstV) + np.dot(CorrVWxyz,CConstW) # Residual field term - v
    #         CtermWYZ = np.dot(CorrUWxyz,CConstU) + np.dot(CorrVWxyz,CConstV) + np.dot(CorrWWxyz,CConstW) # Residual field term - w
    
    #         Uconstrained[:,yloc,zloc] = Unorm[:,yloc,zloc] + np.squeeze(CtermUYZ)
    #         Vconstrained[:,yloc,zloc] = Vnorm[:,yloc,zloc] + np.squeeze(CtermVYZ)
    #         Wconstrained[:,yloc,zloc] = Wnorm[:,yloc,zloc] + np.squeeze(CtermWYZ)
    
    # if Options.UseNormalization == 1
    #     Uconstrained = Uconstrained.*stdUdata + muUdata;
    #     Vconstrained = Vconstrained.*stdVdata + muVdata;
    #     Wconstrained = Wconstrained.*stdWdata + muWdata;
    # end
    
    t3 = time.time()
    print('Constraint application complete')
    print('Time elapsed is ' + str(t3 - t2))
    
    if SaveToFile == 1:
        Uconstrained.reshape(Nx*Ny*Nz).astype('single').tofile(BaseName + '_' + str(SeedNo) + '_c_' + Component + '_py.bin',sep = '')
    
    
    # if nargout > 0
    #     u = Uconstrained;
    #     v = Vconstrained;
    #     w = Wconstrained;
    # end
    
    # if Options.SaveToFile == 1
    #     disp('Saving resulting turbulence boxes:')
    #     clear Unorm Vnorm Wnorm CorrUUxyz CorrVVxyz CorrWWxyz CorrUVxyz CorrUWxyz CorrVWxyz
    #     Uvect = zeros(Nx*Ny*Nz,1);
    #     Vvect = zeros(Nx*Ny*Nz,1);
    #     Wvect = zeros(Nx*Ny*Nz,1);
    #     for xloc = 1:Nx
    #         for yloc = 1:Ny
    #             dataindex = Ny*Nz*(xloc - 1) + Ny*(yloc-1);
    #             UperZ = Uconstrained(xloc,yloc,:);
    #             VperZ = Vconstrained(xloc,yloc,:);
    #             WperZ = Wconstrained(xloc,yloc,:);
    #             Uvect(dataindex+1:dataindex+Nz) = UperZ;                        
    #             Vvect(dataindex+1:dataindex+Nz) = VperZ;                        
    #             Wvect(dataindex+1:dataindex+Nz) = WperZ;                        
    #         end
    #     end    
    #     OutputFileU = fopen([Input.BaseName '_' num2str(SeedNo) '_c_u.bin'],'w');
    #     fwrite(OutputFileU,Uvect,'single');    
    #     fclose(OutputFileU);
    #     OutputFileV = fopen([Input.BaseName '_' num2str(SeedNo)  '_c_v.bin'],'w');    
    #     fwrite(OutputFileV,Vvect,'single');    
    #     fclose(OutputFileV);
    #     OutputFileW = fopen([Input.BaseName '_' num2str(SeedNo)  '_c_w.bin'],'w');
    #     fwrite(OutputFileW,Wvect,'single');    
    #     fclose(OutputFileW);
    #     disp('DONE!');
    # end
    tend = time.time()
    print('Constrained simulation complete')
    print('Total time elapsed is ' + str(tend-tstart))

    return Uconstrained