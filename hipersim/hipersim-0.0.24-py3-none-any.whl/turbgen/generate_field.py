# -*- coding: utf-8 -*-
"""
Created on Sat Apr 24 12:23:07 2021

@author: nkdi, astah
"""

def generate_field(BaseName,alphaepsilon,L,Gamma,SeedNo,Nx,Ny,Nz,dx,dy,dz, \
                        HighFreqComp = 0, SaveToFile = 0, TurbOptions = None):

    # Nx = 8192
    # Ny = 32
    # Nz = 32
    # dx = 2
    # dy = 4
    # dz = 4
    # L = 30
    # Gamma = 3
    # alphaepsilon = 1
    # SeedNo = [10,11]
    # HighFreqComp = 1
    # SaveToFile = 1
    # BaseName = 'Turb'
    HighFreqCompCheat = 1      
    
    
    ''' TURBULENCE GENERATION ROUTINE '''
    import numpy as np
    from hipersim.turbgen.manntensor import manntensorcomponents, manntensorsqrtcomponents
    from hipersim.turbgen.trapezoidal_sum_2d import trapezoidal_sum_2d 
    import time
    pi = np.pi
    '''
    =====================================================================
    Advanced inputs
    =====================================================================
    --------------------------------------------------------------------
    Upscaling the 2-3 direction to avoid periodicity of the output field
    --------------------------------------------------------------------
    Nx, Ny, Nz: required box dimensions. N1, N2, N3: dimensions used in the generation phase
    N2,N3 = 2*(Ny,Nz) removes periodicity in the 2-3 dimensions. 
    N1 = 2*Nx would remove periodicity in longitudinal direction, however
    this is less important than removing the periodicity in the 2-3 plane
    ---------------------------------------------------------------------'''
    N1 = Nx
    N2 = Ny*2
    N3 = Nz*2
    '''
    -----------------------------------------
    Settings for low frequency correction. 
    -----------------------------------------'''
    #     knormlim = [Inf Inf Inf]  Apply low-freq correction to all wavenumbers
    # knormlim = np.array([0, 0, 0]) # No low-freq correction
    knormlim = np.array([3/L, 4*pi/(N2*dy), 4*pi/(N3*dz)]) # Recommendation from Mann 1998
    
    print('Generating turbulence boxes..')
    tstart = time.time()
    '''
    ===========================================
     Define wave number vectors
    ==========================================='''
    L1 = N1*dx
    L2 = N2*dy
    L3 = N3*dz
    
    m1 = np.concatenate([np.arange(0,N1/2),np.arange(-N1/2,0)])
    m2 = np.concatenate([np.arange(0,N2/2),np.arange(-N2/2,0)])
    m3 = np.concatenate([np.arange(0,N3/2),np.arange(-N3/2,0)])
    
    k1 = m1*2*pi/L1
    k2 = m2*2*pi/L2
    k3 = m3*2*pi/L3
    
    VolumeCoef = np.sqrt((8*(pi**3)/(L1*L2*L3)))
    
    '''
    ==================================================================
     Prepare numerical integration for accurate low-frequency spectra
    ==================================================================
    '''
    SincCorrectionFactors = np.array([1.22686,1.10817,1.07072,1.05248,1.04171])
    Nsinc = 1
    SincCorrection = SincCorrectionFactors[Nsinc-1]
    k2local = np.linspace(- Nsinc*2*pi/L2, Nsinc*2*pi/L2,N2)
    k3local = np.linspace(- Nsinc*2*pi/L3, Nsinc*2*pi/L3,N3)
    k2localgrid,k3localgrid = np.meshgrid(k2local,k3local)
    S2 = k2localgrid*L2/2
    Sinc2 = (np.sin(S2)/S2)**2
    Sinc2[S2==0] = 1
    S3 = k3localgrid*L3/2
    Sinc3 = (np.sin(S3)/S3)**2
    Sinc3[S3==0] = 1                        
    SincProd = Sinc2*Sinc3
    
    '''
    ======================================================================
     Pre-generate arrays with the Mann Tensor square-root matrices
    ======================================================================'''
    ik2grid,ik1grid,ik3grid = np.meshgrid(np.arange(N2),np.arange(N1),np.arange(N3))
    ik1vect = np.reshape(ik1grid,N1*N2*N3)
    ik2vect = np.reshape(ik2grid,N1*N2*N3)
    ik3vect = np.reshape(ik3grid,N1*N2*N3)
    ComputeRangeList = ((ik1vect+1)/N1 + (ik2vect+1)/N2 + (ik3vect+1)/N3 - 3/2 - 1/N3) <= 0
    InVolList = np.asarray(np.where(((abs(k1[ik1vect])<knormlim[0]) & (abs(k2[ik2vect]) < knormlim[1]) & (abs(k3[ik3vect]) < knormlim[2])) & ComputeRangeList)[0])
    ComputeRangeList = np.asarray(np.where(ComputeRangeList)[0])
    SqrtPhi = np.zeros((3,3,N1,N2,N3),dtype = 'csingle')
    k2grid, k3grid = np.meshgrid(k2,k3)
    
    '''
    ==============================================================================
    Implementation of eq. 46 in Mann (1998) over all wave numbers. 
    The square root of the Mann tensor is computed, however without multiplying 
    with random complex standard normal coefficients yet.
    
    Some of the values for low wave numbers will later be overwritten by the 
    implementation of eq. 47 in Mann (1998), but this is normally less than 0.1%
    of the total number of coefficients, so it is not convenient to exclude 
    these wave number ranges. 
    
    If no high-frequency compensation is required, just the Mann tensor square root 
    over all wave numbers is computed. It is done in a loop over k1, as a 
    compromise between computational speed requirements (best avoiding all loops)
    and memory requirements (making a full 3-D grid of k1, k2 and k3 values will
    require many megabytes of extra memory).
    =============================================================================='''
    
    if HighFreqComp == 1:
        '''
        ---------------------------------------------------------------------
        Implementation of high-frequency compensation based on computing the 
        variance loss due to aliasing. Significantly faster than implementing
        eq. A6 in Mann (1998). The variance loss ratio is computed by integrating
        the u, v, w components of the Mann spectrum over two k2-k3 planes with 
        different spans: one with the k2-k3 span of the desired turbulence box, 
        the other one with much bigger span to approximate the range of k's from 
        -Inf to Inf.  
        ---------------------------------------------------------------------'''
        p2delta = 4
        p3delta = 4
        nk2deltapoints = N2
        nk3deltapoints = N3        
    
        k2deltaint0 = np.concatenate([k2[int(N2/2):], k2[0:int(N2/2)]])
        k3deltaint0 = np.concatenate([k3[int(N3/2):], k3[0:int(N3/2)]])
        k2deltaintgrid0,k3deltaintgrid0 = np.meshgrid(k2deltaint0,k3deltaint0)
    
        k2deltarange1 = [N2*pi/L2, (p2delta+1)*N2*pi/L2]
        k3deltarange1 = [N3*pi/L3, (p3delta+1)*N3*pi/L3]
        k21p = 10**(np.linspace(np.log10(k2deltarange1[0]),np.log10(k2deltarange1[1]),int(np.floor(nk2deltapoints/2))))
        k31p = 10**(np.linspace(np.log10(k3deltarange1[0]),np.log10(k3deltarange1[1]),int(np.floor(nk3deltapoints/2))))
        k2deltaint1 = np.concatenate([-np.flip(k21p[1:]), k2deltaint0, k21p])
        k3deltaint1 = np.concatenate([-np.flip(k31p[1:]), k3deltaint0, k31p])
        k2deltaintgrid1,k3deltaintgrid1 = np.meshgrid(k2deltaint1,k3deltaint1)
    
        VarRatio = np.ones((N1,3,3))
        k1p = np.linspace(0,N1*pi/L1,int(np.floor(np.max([(N1/32 + 1),33]))))
        k1interp = np.concatenate([-np.flip(k1p[1:]), k1p])
        VarRatioInterp = np.ones((k1interp.shape[0],3))
        
        for ik1 in range(k1interp.shape[0]):
            PhiHiFreq11ij, PhiHiFreq22ij, PhiHiFreq33ij,__,__,__ = manntensorcomponents(k1interp[ik1]*np.ones(k2deltaintgrid1.shape), \
            k2deltaintgrid1,k3deltaintgrid1,Gamma,L,alphaepsilon,2)    
            VarHigh11 = trapezoidal_sum_2d(PhiHiFreq11ij,k2deltaint1,k3deltaint1)
            VarHigh22 = trapezoidal_sum_2d(PhiHiFreq22ij,k2deltaint1,k3deltaint1)
            VarHigh33 = trapezoidal_sum_2d(PhiHiFreq33ij,k2deltaint1,k3deltaint1)
            PhiLowFreq11ij, PhiLowFreq22ij, PhiLowFreq33ij,__,__,__ = manntensorcomponents(k1interp[ik1]*np.ones(k2deltaintgrid0.shape), \
               k2deltaintgrid0,k3deltaintgrid0,Gamma,L,alphaepsilon,2)        
            VarLow11 = trapezoidal_sum_2d(PhiLowFreq11ij,k2deltaint0,k3deltaint0)
            VarLow22 = trapezoidal_sum_2d(PhiLowFreq22ij,k2deltaint0,k3deltaint0)
            VarLow33 = trapezoidal_sum_2d(PhiLowFreq33ij,k2deltaint0,k3deltaint0)
            VarRatioInterp[ik1,0] = VarHigh11/VarLow11
            VarRatioInterp[ik1,1] = VarHigh22/VarLow22
            VarRatioInterp[ik1,2] = VarHigh33/VarLow33
        
        VarRatio[:,0,0] = np.interp(k1,k1interp,VarRatioInterp[:,0])
        VarRatio[:,1,1] = np.interp(k1,k1interp,VarRatioInterp[:,1])
        VarRatio[:,2,2] = np.interp(k1,k1interp,VarRatioInterp[:,2])
        
        if HighFreqCompCheat == 1:
            '''
            -------------------------------------------------------------------------
            High-frequency compensation is done by directly applying the compensation
            terms to the main diagonal of the "sheared tensor" matrix given in eq.13
            in Mann (1998). May not be ideal as it also introduces variance increase
            in the off-diagonal terms in the full Mann tensor - but it allows to 
            directly assemble the square-root Mann tensor, avoiding the need for
            computing a matrix square root. This is especially important for the 
            Python implementation of the code, because the np.linalg.eig() and 
            np.lib.scimath.sqrt() functions are extremely slow, increasing the
            computation time 20-fold.
            ----------------------------------------------------------------------'''
            for ik1 in range(int(N1/2)+1):
                Phi11ij, Phi12ij, Phi13ij, Phi21ij, Phi22ij, Phi23ij, Phi31ij, Phi32ij, Phi33ij = manntensorsqrtcomponents(k1[ik1]*np.ones(k2grid.shape), \
                               k2grid,k3grid,Gamma,L,alphaepsilon,2,ElementChoice = None, VarianceRatios = np.sqrt(np.array([VarRatio[ik1,0,0],VarRatio[ik1,1,1],VarRatio[ik1,2,2]])))       
                #Phi11[ik1,:,:] = VarRatio[ik1,0,0]*Phi11ij
                #Phi22[ik1,:,:] = VarRatio[ik1,1,1]*Phi22ij
                #Phi33[ik1,:,:] = VarRatio[ik1,2,2]*Phi33ij
                #Phi12[ik1,:,:] = Phi12ij
                #Phi13[ik1,:,:] = Phi13ij
                #Phi23[ik1,:,:] = Phi23ij
                SqrtPhi[0,0,ik1,:,:] = Phi11ij
                SqrtPhi[1,1,ik1,:,:] = Phi22ij
                SqrtPhi[2,2,ik1,:,:] = Phi33ij
                SqrtPhi[0,1,ik1,:,:] = Phi12ij
                SqrtPhi[1,0,ik1,:,:] = Phi21ij
                SqrtPhi[0,2,ik1,:,:] = Phi13ij
                SqrtPhi[2,0,ik1,:,:] = Phi31ij
                SqrtPhi[1,2,ik1,:,:] = Phi23ij
                SqrtPhi[2,1,ik1,:,:] = Phi32ij       
            
        else:
            '''
            ------------------------------------------------------------------------
            High-frequency compensation by multiplying the main-diagonal terms in 
            the Mann tensor with the variance compensation ratios. Requires computing
            the matrix square root of the Mann tensor (very slow in Python)
            -----------------------------------------------------------------------'''
            
            for ik1 in range(int(N1/2) + 1):
        
                Phi11ij, Phi22ij, Phi33ij, Phi12ij, Phi13ij, Phi23ij = manntensorcomponents(k1[ik1]*np.ones(k2grid.shape), \
                               k2grid,k3grid,Gamma,L,alphaepsilon,2)       
                #Phi11[ik1,:,:] = VarRatio[ik1,0,0]*Phi11ij
                #Phi22[ik1,:,:] = VarRatio[ik1,1,1]*Phi22ij
                #Phi33[ik1,:,:] = VarRatio[ik1,2,2]*Phi33ij
                #Phi12[ik1,:,:] = Phi12ij
                #Phi13[ik1,:,:] = Phi13ij
                #Phi23[ik1,:,:] = Phi23ij
                SqrtPhi[0,0,ik1,:,:] = VarRatio[ik1,0,0]*Phi11ij
                SqrtPhi[1,1,ik1,:,:] = VarRatio[ik1,1,1]*Phi22ij
                SqrtPhi[2,2,ik1,:,:] = VarRatio[ik1,2,2]*Phi33ij
                SqrtPhi[0,1,ik1,:,:] = Phi12ij
                SqrtPhi[1,0,ik1,:,:] = Phi12ij
                SqrtPhi[0,2,ik1,:,:] = Phi13ij
                SqrtPhi[2,0,ik1,:,:] = Phi13ij
                SqrtPhi[1,2,ik1,:,:] = Phi23ij
                SqrtPhi[2,1,ik1,:,:] = Phi23ij
                
            for ik in ComputeRangeList:
                EigValC,EigVectC = np.linalg.eig(SqrtPhi[:,:,ik1vect[ik],ik2vect[ik],ik3vect[ik]])
                SqrtPhiij = np.dot(EigVectC,np.dot(np.diag(np.lib.scimath.sqrt(EigValC)),EigVectC.T))  
                #SqrtCij = VolumeCoef*SqrtPhiij
                # SqrtPhiij = linalg.sqrtm(SqrtPhi[:,:,ik1vect[ik],ik2vect[ik],ik3vect[ik]])
                SqrtPhi[:,:,ik1vect[ik],ik2vect[ik],ik3vect[ik]] = SqrtPhiij
                    
    else:
        '''
        ----------------------------------------------------------------------------
        Implementation of eq. 46 in Mann (1998) over all wave numbers without 
        high-frequency compensation. 
        ----------------------------------------------------------------------------'''
    
        for ik1 in range(int(N1/2) + 1):
            Phi11, Phi12, Phi13, Phi21, Phi22, Phi23, Phi31, Phi32, Phi33 = manntensorsqrtcomponents(k1[ik1]*np.ones(k2grid.shape),k2grid,k3grid,Gamma,L,alphaepsilon,2)
            SqrtPhi[0,0,ik1,:,:] = Phi11
            SqrtPhi[1,1,ik1,:,:] = Phi22
            SqrtPhi[2,2,ik1,:,:] = Phi33
            SqrtPhi[0,1,ik1,:,:] = Phi12
            SqrtPhi[1,0,ik1,:,:] = Phi21
            SqrtPhi[0,2,ik1,:,:] = Phi13
            SqrtPhi[2,0,ik1,:,:] = Phi31
            SqrtPhi[1,2,ik1,:,:] = Phi23
            SqrtPhi[2,1,ik1,:,:] = Phi32  
    
    SqrtPhi*= VolumeCoef
    
    
    '''
    ==============================================================================
     Implementation of eq. 47 in Mann (1998) for low wave numbers where the sinc
     function is not delta-function like. 
    =============================================================================='''  
    for ik in InVolList:
                                                       
        k2primei = k2[ik2vect[ik]] - k2local 
        k3primei = k3[ik3vect[ik]] - k3local
        k2primegridi,k3primegridi = np.meshgrid(k2primei,k3primei)
    
        PhiInt11ij,PhiInt22ij,PhiInt33ij,PhiInt12ij,PhiInt13ij,PhiInt23ij = manntensorcomponents(k1[ik1vect[ik]]*np.ones(k2primegridi.shape), \
                                    k2primegridi,k3primegridi,Gamma,L,alphaepsilon,2)
    
        C11i = trapezoidal_sum_2d(PhiInt11ij*SincProd,k2primei,k3primei)
        C22i = trapezoidal_sum_2d(PhiInt22ij*SincProd,k2primei,k3primei)
        C33i = trapezoidal_sum_2d(PhiInt33ij*SincProd,k2primei,k3primei)
        C12i = trapezoidal_sum_2d(PhiInt12ij*SincProd,k2primei,k3primei)
        C13i = trapezoidal_sum_2d(PhiInt13ij*SincProd,k2primei,k3primei)
        C23i = trapezoidal_sum_2d(PhiInt23ij*SincProd,k2primei,k3primei)
    
        Cij = (SincCorrection*2*pi/L1)*np.array([[C11i, C12i, C13i],[C12i, C22i, C23i], [C13i, C23i, C33i]])  
        if HighFreqComp == 1:
            '''
            ----------------------------------------
              Apply eq. A6 in Mann (1998). 
            ----------------------------------------'''                                                         
            Cij*= VarRatio[ik1vect[ik],:,:]
            # end of if HighFreqComp == 1
        EigValC,EigVectC = np.linalg.eig(Cij)
        SqrtCij = np.dot(EigVectC,np.dot(np.diag(np.lib.scimath.sqrt(EigValC)),EigVectC.T))
        # SqrtCij = linalg.sqrtm(Cij)
        SqrtPhi[:,:,ik1vect[ik],ik2vect[ik],ik3vect[ik]] = SqrtCij
     
    '''
    ---------------------------------------------------------
    Clear all unnecessary variables to free memory
    ------------------------------------------------------'''
    
    del k2primegridi, k3primegridi, PhiInt11ij, PhiInt22ij, PhiInt33ij, PhiInt12ij, PhiInt13ij, PhiInt23ij
    del InVolList, ComputeRangeList
        
     
    '''
    ===================================================================================
    The rest of the code multiplies the Mann tensor square root values with
    random complex Gaussian coefficients and inverse Fourier-transforms to obtain
    the final turbulence box. This is done over a loop to allow quicker generation
    of multiple turbulence boxes with identical spectral properties but different seeds.
    ==================================================================================='''
    from numpy.random import Generator, PCG64
    # use Generator, MT19937 to match the (SeedNo,'twister') behavior in Matlab
    
    for iSeed in np.atleast_1d(np.asarray(SeedNo)):
        '''
        ===========================================================================
         Initialize random number generator with the seed number requested
        ==========================================================================='''
        
        rg = Generator(PCG64(iSeed))
        n = (rg.standard_normal((3,1,N1,N2,N3),dtype = 'float32') + rg.standard_normal((3,1,N1,N2,N3),dtype = 'float32')*1j)/np.sqrt(2)
        Cx = (SqrtPhi[0,0,:,:,:]*n[0,0,:,:,:] + SqrtPhi[0,1,:,:,:]*n[1,0,:,:,:] + SqrtPhi[0,2,:,:,:]*n[2,0,:,:,:])
        Cy = (SqrtPhi[1,0,:,:,:]*n[0,0,:,:,:] + SqrtPhi[1,1,:,:,:]*n[1,0,:,:,:] + SqrtPhi[1,2,:,:,:]*n[2,0,:,:,:])
        Cz = (SqrtPhi[2,0,:,:,:]*n[0,0,:,:,:] + SqrtPhi[2,1,:,:,:]*n[1,0,:,:,:] + SqrtPhi[2,2,:,:,:]*n[2,0,:,:,:])
        
        del n
        
        if np.asarray(SeedNo).size <= 1:
            del SqrtPhi # clear up some extra memory - only works if we are generating just one box
            
        '''
        ============================================================================================
         Adjust coefficients to enforce symmetry (only about half of the coefficients are filled in)
        ============================================================================================
                    Symmetry by astah
        -------------------------------------------------------------------------------------------'''
        
        
        # Symmetry in 3D around the plane x = N1/2 and excluding the zero edge plane and the centerplane:
        Cind = np.where( (ik1grid > 0) & (ik1grid < N1/2) ) #&
        Cx[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cx[Cind])
        Cy[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cy[Cind])
        Cz[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cz[Cind])
        # Symmetry in the two 2d planes:
        Cind = np.where( ((ik1grid == 0) | (ik1grid == N1/2)) &
                        ((ik2grid > 0) & (ik2grid < N2/2)) )
        Cx[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cx[Cind])
        Cy[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cy[Cind])
        Cz[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cz[Cind])
        # Symmetry along the edges in the planes:
        Cind = np.where( ((ik1grid == 0) | (ik1grid == N1/2)) &
                        ((ik2grid == 0) | (ik2grid == N2/2)) &
                        ((ik3grid > 0) & (ik3grid < N3/2)) )
        Cx[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cx[Cind])
        Cy[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cy[Cind])
        Cz[-Cind[0], -Cind[1], -Cind[2]] = np.conj(Cz[Cind])
        # Make the zero and centerpoints real:
        Cind = np.where( ((ik1grid==0) | (ik1grid==N1/2) ) & 
                        ( (ik2grid==0) | (ik2grid==N2/2)) &
                        ( (ik3grid==0) | (ik3grid==N3/2) ) )
        Cx[Cind] = np.real(Cx[Cind])
        Cy[Cind] = np.real(Cy[Cind])
        Cz[Cind] = np.real(Cz[Cind])
            
        
        # '''
        # ============================================================================================
        #  Adjust coefficients to enforce symmetry (only about half of the coefficients are filled in)
        # ============================================================================================
        #  The logics of the symmetry conditions are based on Lasse Gilling's
        #  "TuGen" code (Gilling, L. (2009) TuGen: Synthetic Turbulence
        #  Generator, Manual and User's Guide)
        # -------------------------------------------------------------------------------------------'''
        
        # Cxconj = np.conj(Cx)
        # Cyconj = np.conj(Cy)
        # Czconj = np.conj(Cz)
        
        # Cprev = np.full((N1,N2,N3),False)
        # Cindex = ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2+1 )) & ( ((ik2grid+1)==1) | ((ik2grid+1) == N2/2+1)) & (( (ik3grid+1) == 1) | ((ik3grid+1) == N3/2+1 ))
        # Cx[Cindex] = np.real(Cx[Cindex])
        # Cy[Cindex] = np.real(Cy[Cindex])
        # Cz[Cindex] = np.real(Cz[Cindex])
        # Cprev[Cindex] = True
        # Cindex = ( ((ik2grid+1) == 1) | ((ik2grid+1) == N2/2+1) ) & ( ((ik3grid+1)==1) | ((ik3grid+1) == N3/2+1)) & ((ik1grid+1) > (N1/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = 0),axis = 0)[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = 0),axis = 0)[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = 0),axis = 0)[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2+1) ) & ( ((ik3grid+1)==1) | ((ik3grid+1) == N3/2+1)) & ((ik2grid+1) > (N2/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = 1),axis = 1)[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = 1),axis = 1)[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = 1),axis = 1)[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2+1) ) & ( ((ik2grid+1)==1) | ((ik2grid+1) == N2/2+1)) & ((ik3grid+1) > (N3/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = 2),axis = 2)[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = 2),axis = 2)[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = 2),axis = 2)[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik1grid+1) > N1/2 + 1) & ( ((ik2grid+1) == 1) | ((ik2grid+1) == N2/2 + 1)) & (Cprev == False)
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik1grid+1) > N1/2 + 1) & ( ((ik3grid+1) == 1) | ((ik3grid+1) == N3/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik2grid+1) > N2/2 + 1) & ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik2grid+1) > N2/2 + 1) & ( ((ik3grid+1) == 1) | ((ik3grid+1) == N3/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,1)),axis = (0,1))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik3grid+1) > N3/2 + 1) & ( ((ik1grid+1) == 1) | ((ik1grid+1) == N1/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (1,2)),axis = (1,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = ( (ik3grid+1) > N3/2 + 1) & ( ((ik2grid+1) == 1) | ((ik2grid+1) == N2/2 + 1))
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,2)),axis = (0,2))[Cindex]
        # Cprev[Cindex] = True
        # Cindex = (( (ik1grid+1)/N1 + (ik2grid+1)/N2 + (ik3grid+1)/N3 - 3/2 - 1/N3) > 0) & (Cprev == False)
        # Cx[Cindex] = np.flip(np.roll(Cxconj, -1, axis = (0,1,2)),axis = (0,1,2))[Cindex]
        # Cy[Cindex] = np.flip(np.roll(Cyconj, -1, axis = (0,1,2)),axis = (0,1,2))[Cindex]
        # Cz[Cindex] = np.flip(np.roll(Czconj, -1, axis = (0,1,2)),axis = (0,1,2))[Cindex]
        
        # del Cprev, Cindex, Cxconj, Cyconj, Czconj
        
        '''
        %===================================================
        % Inverse n-dimensional Fourier transform
        %==================================================='''
        ScaleCoef = N1*N2*N3
        
        u = np.fft.ifftn(ScaleCoef*Cx)
        v = np.fft.ifftn(ScaleCoef*Cy)
        w = np.fft.ifftn(ScaleCoef*Cz)
        
        # Uncomment for output at the center of the box
        # u = np.real(u[:Nx,int(Ny/2):int(Ny/2+Ny),int(Nz/2):int(Nz/2+Nz)])
        # v = np.real(v[:Nx,int(Ny/2):int(Ny/2+Ny),int(Nz/2):int(Nz/2+Nz)])
        # w = np.real(w[:Nx,int(Ny/2):int(Ny/2+Ny),int(Nz/2):int(Nz/2+Nz)])
        
        # Default output choice - "lower-left" corner of the box
        u = np.real(u[:Nx,:Ny,:Nz])
        v = np.real(v[:Nx,:Ny,:Nz])
        w = np.real(w[:Nx,:Ny,:Nz])
        
        if SaveToFile == 1:
            if TurbOptions is None:
                FileFormat = 0
            else:            
                if 'FileFormat' not in TurbOptions:
                    FileFormat = 0
                else:
                    FileFormat = TurbOptions['FileFormat']              
            if (FileFormat == 0) | (FileFormat == 'Hawc2') | (FileFormat == 'Mann'):
                u.reshape(Nx*Ny*Nz).astype('single').tofile(BaseName + '_' + str(iSeed) + '_u' + '.bin',sep = '')
                v.reshape(Nx*Ny*Nz).astype('single').tofile(BaseName + '_' + str(iSeed) + '_v' + '.bin',sep = '')
                w.reshape(Nx*Ny*Nz).astype('single').tofile(BaseName + '_' + str(iSeed) + '_w' + '.bin',sep = '')
            elif (FileFormat == 'Bladed') | (FileFormat == 'wnd') | (FileFormat == 'TurbSim'):                
                from hipersim.turbgen.turb_utils import output_field
                params = {'dx':dx, 'dy':dy, 'dz':dz, 'Nx':Nx, 'Ny': Ny, 'Nz':Nz,'SeedNo': SeedNo, 'BaseName': BaseName, 'SaveToFile':1}
                output_field(u,v,w,params,TurbOptions)
        
        tend = time.time()
        print('Turbulence box generation complete.')
        print('Time elapsed is ' + str(tend-tstart))
    return u,v,w