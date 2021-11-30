# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 12:47:19 2018

@author: nkdi
"""
import numpy as np
#from w2l import activation_functions
#from surrogates import math_utils
from hipersim.surrogates import math_utils

class ann:
    def __init__(self,**kwargs):
        #print(kwargs)
        if 'layersizes' in kwargs:
            self.layersizes = kwargs['layersizes']
        else:
            self.layersizes = [1, 10, 1]
            
        self.nlayers = len(self.layersizes) - 1 # Input layer is not counted
        
        if 'neurontypes' in kwargs:
            self.neurontypes = kwargs['neurontypes']
        else:
            self.neurontypes = ['Linear']*self.nlayers
            
        if 'activation' in kwargs:
            self.activation = kwargs['activation']
        else:
            self.activation = ['Relu']*(self.nlayers-1) + ['Linear']
            
        if 'testratios' in kwargs:
            self.testratios = kwargs['testratios']
        else:
            self.testratios = [0.7, 0.2, 0.1]
            
        if 'output_style' in kwargs:
            self.output_style = kwargs['output_style']
        else:
            self.output_style = 'None'
            
        if 'params' in kwargs:
            self.params = kwargs['params']
        else:
            self.params = {'weightinit': [0.01]*self.nlayers, 
                           'regularization': 0.1, 
                           'learningrate': 0.1, 
                           'costfunction': 'Lsq', 
                           'minibatchsize': 0, 
                           'maxiter': 1500, 
                           'RMSprop': 0.999, 
                           'Momentum': 0.9, 
                           'Xscaling': True, 
                           'Yscaling': True}
        # Parse parameters that may have not been given in the input
        if not 'weightinit' in self.params:
            self.params['weightinit'] = [0.01]*self.nlayers
        if not 'regularization' in self.params:
            self.params['regularization'] = 0.1
        if not 'learningrate' in self.params:           
            self.params['learningrate'] = 0.1
        if not 'costfunction' in self.params:
            self.params['costfunction'] = 'Lsq'
        if not 'minibatchsize' in self.params:
            self.params['minibatchsize'] = 0
        if not 'maxiter' in self.params:
            self.params['maxiter'] = 1500 # Same as nepochs
        if not 'RMSprop' in self.params:
            self.params['RMSprop'] = 0.999
        if not 'Momentum' in self.params:
            self.params['Momentum'] = 0.9
        if not 'nepochs' in self.params:
            self.params['nepochs'] = self.params['maxiter']
        if not 'Xscaling' in self.params:
            self.params['Xscaling'] = True
        if not 'Yscaling' in self.params:
            self.params['Yscaling'] = True


    def initialize_weights(self):
        W = []
        b = []
        #np.random.seed(1) # Used only in case we need to maintan consisteny with Matlab
        for i in range(self.nlayers):
            if self.neurontypes[i] == 'Linear':
                #Wi = np.random.randn(self.layersizes[i],self.layersizes[i+1])*self.params['weightinit'][i] # Regular way of initializing weights
                Wi = math_utils.NormalDist(2,np.random.rand(self.layersizes[i],self.layersizes[i+1]),0,1)*self.params['weightinit'][i] # For consistency with Matlab
                bi = np.zeros([1,self.layersizes[i+1]])
            elif self.neurontypes[i] == 'LinearPretrained':
                Wi = self.weights['W'][i]
                bi = self.weights['bias'][i]
            elif self.neurontypes[i] == 'LinearNonTrainable':
                Wi = self.weights['W'][i]
                bi = self.weights['bias'][i]                
            W.append(Wi)
            b.append(bi)
            
        if hasattr(self, 'weights'):
            self.weights['W'] = W    
            self.weights['bias'] = b
        else:
            self.weights = {'W':W, 'bias':b}
                        
        return W,b
    
    def forward_propagation(self,X):
        A = []
        Z = []
        A.append(X)
        Ai = X
        for i in range(self.nlayers):
            if self.neurontypes[i]=='Linear':
                Zi = np.dot(Ai,self.weights['W'][i]) + self.weights['bias'][i]
            elif self.neurontypes[i]=='LinearPretrained':
                Zi = np.dot(Ai,self.weights['W'][i]) + self.weights['bias'][i]
            elif self.neurontypes[i]=='LinearNonTrainable':
                Zi = np.dot(Ai,self.weights['W'][i]) + self.weights['bias'][i]
            else:
                raise ValueError('Unknown or unspecified neuron type')

            if self.activation[i] == 'Relu':
                Ai = math_utils.relu(Zi)
            elif self.activation[i] == 'Linear':
                Ai = Zi
            elif self.activation[i] == 'Tanh':
                Ai = math_utils.hyperbolic_tangent(Zi)
            elif self.activation[i] == 'Softplus':
                Ai = math_utils.softplus(Zi)
            else:
                raise ValueError('Unknown or unspecified activation function')
            
            A.append(Ai)
            Z.append(Zi)
            
        Ypredict = Ai
        ANNcache = (A,Z)
        return Ypredict, ANNcache
    
    def backward_propagation(self,X,Y,Ypredict,ANNcache):
        if self.params['costfunction'] == 'Log':
            dJdAprev = -Y/Ypredict + (1 - Y)/(1 - Ypredict)
        elif self.params['costfunction'] == 'Lsq':
            dJdAprev = (Ypredict -Y)
        else:
            raise ValueError('Unknown cost function type')
        
        dJdA = [None]*self.nlayers
        dAdZ = [None]*self.nlayers
        dJdW = [None]*self.nlayers
        dJdb = [None]*self.nlayers 
        dJdZ = [None]*self.nlayers
        A,Z = ANNcache
        
        for i in range(self.nlayers-1, -1,-1):
            dJdA[i] = dJdAprev
            if self.activation[i] == 'Linear':
                dAdZ[i] = np.ones(Z[i].shape)
            elif self.activation[i] == 'Relu':
                dAdZ[i] = np.ones(Z[i].shape)*(Z[i] > 0)
            elif self.activation[i] == 'Softplus':
                dAdZ[i] = math_utils.logistic(Z[i])
            elif self.activation[i] == 'Tanh':
                dAdZ[i] = 1 - math_utils.hyperbolic_tangent(Z[i])**2
            elif self.activation[i] == 'Logistic':
                dAdZ[i] = math_utils.logistic(Z[i])*(1 - math_utils.logistic(Z[i]))
            else:
                raise ValueError('Unknown activation function')
            
            dJdZ[i] = dAdZ[i]*dJdA[i]
            mlength = X.shape[0]
            if self.neurontypes[i] == 'Linear':
                dJdW[i] = (1/mlength)*np.dot(A[i].T,dJdZ[i])
                dJdb[i] = (1/mlength)*np.sum(dJdZ[i],0,keepdims = True)
            elif self.neurontypes[i] == 'LinearPretrained':
                dJdW[i] = (1/mlength)*np.dot(A[i].T,dJdZ[i])
                dJdb[i] = (1/mlength)*np.sum(dJdZ[i],0,keepdims = True)
            elif self.neurontypes[i] == 'LinearNonTrainable':
                dJdW[i] = np.zeros(Z[i].shape)
                dJdb[i] = np.zeros((1,Z[i].shape[1]))
            else:
                raise ValueError('Unknown neuron type')

            dJdAprev = np.dot(dJdZ[i],self.weights['W'][i].T)            
        
        return dJdW, dJdb

    def backward_propagation_dy(self,X):
        if self.params['Xscaling']:
            X = (X - self.Xbias)/self.Xscale # Lots of broadcasting taking place here
            
        Y, ANNcache = self.forward_propagation(X)
        if self.params['Yscaling']:
            Y = Y*self.Yscale + self.Ybias
        
        A,Z = ANNcache
        noutputs = Y.shape[1]
                
        dY = [None]*noutputs
        
        for iY in range(noutputs):
        
            for i in range(self.nlayers-1, -1,-1):
                
                if i == self.nlayers - 1:
                    Zi = Z[i][:,iY]
                    Zi = Zi.reshape(Zi.shape[0],1)
                    Wi = self.weights['W'][i][:,iY]
                    Wi = Wi.reshape(Wi.shape[0],1)
                else:
                    Zi = Z[i]
                    Wi = self.weights['W'][i]
                    
                if self.activation[i] == 'Linear':
                    dAdZ = np.ones(Zi.shape)
                elif self.activation[i] == 'Relu':
                    dAdZ = np.ones(Zi.shape)*(Zi > 0)
                elif self.activation[i] == 'Softplus':
                    dAdZ = math_utils.logistic(Zi)
                elif self.activation[i] == 'Tanh':
                    dAdZ = 1 - math_utils.hyperbolic_tangent(Zi)**2
                elif self.activation[i] == 'Logistic':
                    dAdZ = math_utils.logistic(Zi)*(1 - math_utils.logistic(Zi))
                else:
                    raise ValueError('Unknown activation function')
                
                if i == self.nlayers-1:
                    dYi = np.dot(dAdZ,Wi.T)
                else:
                    dYi = np.dot((dAdZ*dYi),Wi.T)

            if self.params['Yscaling']:
                dYi = dYi*self.Yscale[0,iY]
            if self.params['Xscaling']:
                dYi = dYi/self.Xscale
            
            dY[iY] = dYi
                        
        return Y, dY
    
    def check_gradients(self,X):
        if not hasattr(self,'weights'):
            self.initialize_weights()
            
            
    def check_gradients_dxdy(self,X):
        Yout,dYout = self.backward_propagation_dy(X)
    
    def compute_cost(self,X,Y):
        #Computes the cost using log-functions
        mtrain = X.shape[0]
        noutputs = Y.shape[1]
        Ypredict,ANNcache = self.forward_propagation(X)
        if self.params['costfunction'] == 'Log':
            Loss = - (np.multiply(Y,np.log(Ypredict)) + np.multiply((1 - Y), np.log(1 - Ypredict)))
        elif self.params['costfunction'] == 'Lsq':
            Loss = 0.5*np.multiply((Ypredict - Y),(Ypredict - Y))
        else:
            print('Unknown loss function type!')

        if self.params["regularization"] == 0:
            J = (1/mtrain)*np.sum(Loss)*(1/noutputs)
        else:
            v = cell_to_vector(self.weights['W'], self.weights['bias'])
            J = (1/mtrain)*np.sum(Loss)*(1/noutputs) + (self.params['regularization']/(2*mtrain))*(np.dot(v.T,v))

        return J, Ypredict, ANNcache

    
    def train(self,X,Y):
        """
        Uses input-output data pair (X,Y) to train the weights of a neural-net object
        """        
        # Parse hyperparameters
        beta2 = self.params['RMSprop']
        if beta2 == 0:
            epsroundoff = 0
        else:
            epsroundoff = 1e-8
        beta1 = self.params['Momentum']                    
        minibatchsize = self.params['minibatchsize']
        nepochs = self.params['nepochs']
                    
        self.Xbias = np.mean(X,axis=0, keepdims = True) # Keepdims = True needed to allow broadcasting
        self.Ybias = np.mean(Y,axis=0, keepdims = True)
        self.Xscale = np.std(X,axis=0, ddof = 1, keepdims = True)
        self.Yscale = np.std(Y,axis=0, ddof = 1, keepdims = True)
        
        if self.params['Xscaling']:
            X = (X - self.Xbias)/self.Xscale
        if self.params['Yscaling']:
            Y = (Y - self.Ybias)/self.Yscale

        # Split data into training, validation and test sets            
        Ntotal = X.shape[0]
        Ntrain = int(np.floor(Ntotal*self.testratios[0]))
        Ndev = int(np.floor(Ntotal*self.testratios[1]))
        Xtrain = X[:Ntrain,:]
        Ytrain = Y[:Ntrain,:]
        Xdev = X[Ntrain:Ntrain+Ndev,:]
        Ydev = Y[Ntrain:Ntrain+Ndev,:]
        Xtest = X[Ntrain+Ndev:,:]
        Ytest = Y[Ntrain+Ndev:,:]

        # Determine iteration scheme
        if minibatchsize == 0: # Minibatch functionality off
            minibatchsize = Ntrain # Each iteration is on the entire train set            
            Nbatches = 1
            Niter = self.params['nepochs']
        else:
            Nbatches = int(np.ceil(Ntrain/minibatchsize))
            Niter = nepochs*Nbatches
                        
        # Initialize variables and weights
        noutputs = Y.shape[1]
        Jhist = np.zeros([Niter,1])
        Jgradnorm = np.zeros([Niter,1])
        Jdevhist = np.zeros([Niter,1])
        Rsqhist = np.zeros([Niter,noutputs])
        Rsqdevhist = np.zeros([Niter,noutputs])
        
        self.initialize_weights()
        ntotal = 0
        for i in range(self.nlayers):
            ntotal+= self.weights['W'][i].shape[0]*self.weights['W'][i].shape[1] + self.weights['bias'][i].shape[0]*self.weights['bias'][i].shape[1] 
        
        # Initialize interactive plot/inline-output functionalities
        if self.output_style == 'Verbose':
            print('Verbose output')
        elif self.output_style == 'Plot':
            import tkinter
            import matplotlib            
            import matplotlib.pyplot as plt
            plt.ion()
            matplotlib.use('TkAgg')
            fig, axs = plt.subplots(1,2,figsize = (8,4))
            plt00 = axs[0].plot(0,0,'-k')[0]
            plt01 = axs[0].plot(0,0,'-r')[0]
            axs[0].set_xlabel('Number of iterations')
            axs[0].set_ylabel('Cost function value J')
            plt10 = axs[1].plot(0,0,'-k')[0]
            plt11 = axs[1].plot(0,0,'-r')[0]
            plt12 = axs[1].plot(0,0,'--k')[0]
            plt13 = axs[1].plot(0,0,'--r')[0]
            
            axs[1].set_xlabel('Number of iterations')
            axs[1].set_ylabel('R-squared')
            axs[1].set_ylim([0,1])
            fig.tight_layout()
            fig.show()
            fig.canvas.draw()
            
        elif self.output_style == 'None': 
            print('Training neural net model:')
            
            
        # Begin iterations
        go = 1
        i = 0
        ibatch = 0
        iepoch = 0
        Vd = np.zeros([ntotal,1])
        Sd = np.zeros([ntotal,1])
        while go == 1:
            # Look at the dev(validation) set and compute cost function and R-square
            Jdev,Ypredictdev, _ = self.compute_cost(Xdev,Ydev)
            Jdevhist[i] = Jdev
            Rsqdevhist[i,:] = math_utils.pairwise_correlation(Ypredictdev,Ydev)**2
            
            # Pick a single minibatch of training data samples
            if ibatch == Nbatches:
                Xtraini = Xtrain[ibatch*minibatchsize:,:]
                Ytraini = Ytrain[ibatch*minibatchsize:,:]
            else:
                Xtraini = Xtrain[ibatch*minibatchsize:(ibatch+1)*minibatchsize,:]
                Ytraini = Ytrain[ibatch*minibatchsize:(ibatch+1)*minibatchsize,:]
                
            # Compute cost function, cost function gradients, and R-square on one minibatch
            J,Ypredict,ANNcache = self.compute_cost(Xtraini,Ytraini) # Cost function
            [dJdW,dJdb] = self.backward_propagation(Xtraini,Ytraini,Ypredict,ANNcache) # Cost function gradients
            dvecti = cell_to_vector(dJdW,dJdb)
            Jhist[i] = J
            Jgradnorm[i] = (1/minibatchsize)*np.sqrt(np.dot(dvecti.T,dvecti)) # Gradient norm for monitoring purposes
            Rsqhist[i,:] = math_utils.pairwise_correlation(Ypredict,Ytraini)**2 # R-square
            
            # Update weights based on gradient descent
            if (beta1 != 0) & (beta2 != 0): # Adam algorithm
                Vd = beta1*Vd + (1 - beta1)*dvecti
                Sd = beta2*Sd + (1 - beta2)*(dvecti**2)
                Vcorr = Vd/(1 - beta1**(i+1))
                Scorr = Sd/(1 - beta2**(i+1))
                vupd = cell_to_vector(self.weights['W'], self.weights['bias']) - self.params['learningrate']*(Vcorr/(np.sqrt(Scorr) + epsroundoff)  + cell_to_vector(self.weights['W'], self.weights['bias'])*self.params['regularization']/Xtraini.shape[0])
            elif beta1 > 0 & beta2 == 0: # Only momentum, no RMSprop, optional regularization
                Vd = beta1*Vd + (1 - beta1)*dvecti
                Vcorr = Vd/(1 - beta1**(i+1))
                vupd = cell_to_vector(self.weights['W'], self.weights['bias']) - self.params['learningrate']*(Vcorr + cell_to_vector(self.weights['W'], self.weights['bias'])*self.params['regularization']/Xtraini.shape[0])
            else:
                # Simple gradient descent with optional regularization
                vupd = cell_to_vector(self.weights['W'], self.weights['bias']) - self.params['learningrate']*(cell_to_vector(dJdW,dJdb) + cell_to_vector(self.weights['W'], self.weights['bias'])*self.params['regularization']/Xtraini.shape[0])

            self.weights['W'], self.weights['bias'] = vector_to_cell(vupd,self.weights['W'], self.weights['bias'])
            
            # Print/plot iteration outputs
            if self.output_style == 'Verbose':
                print('Epoch #' + str(iepoch) + ', batch #' + str(ibatch) + ', cost function value = ' + str(J[0]))
            elif (self.output_style == 'Plot') & (i >=1):
                
                # Update plot with results from current iteration
                xplot = np.arange(i)
                plt00.set_data(xplot,Jhist[:i])
                plt01.set_data(xplot,Jdevhist[:i])
                axs[0].relim()
                axs[0].autoscale_view(True,True,True) #Autoscale                
                plt10.set_data(xplot,np.min(Rsqhist[:i,:],1))
                plt11.set_data(xplot,np.min(Rsqdevhist[:i,:],1))
                plt12.set_data(xplot,np.max(Rsqhist[:i,:],1))
                plt13.set_data(xplot,np.max(Rsqdevhist[:i,:],1))
                
                axs[1].relim()
                axs[1].autoscale_view(True,True,True) #Autoscale                
                
                plt.pause(0.001)
                fig.canvas.draw()
                plt.show()

            
            i+=1
            ibatch+=1
            if i >= Niter:
                go = 0
            if ibatch >= Nbatches:
                if iepoch >= nepochs:
                    go = 0
                else:
                    ibatch=0
                    iepoch+=1
                    
        Jout,Yout, _ = self.compute_cost(Xtest,Ytest)    
        Rsqout = math_utils.pairwise_correlation(Yout,Ytest)**2
        
        if self.params['Yscaling']:
            Testbias = (np.mean(Yout,0) - np.mean(Ytest,0))*self.Yscale
        else:
            Testbias = np.mean(Yout,0) - np.mean(Ytest,0)
        
        self.metrics = {'RsqTest':Rsqout, 'RsqDev':Rsqdevhist[i-1,:],'RsqTrain':Rsqhist[i-1,:],'Testbias':Testbias}
        
        self.neurontypes = ['LinearPretrained' if ni == 'Linear' else ni for ni in self.neurontypes] # Start from previous trained state in case a new training command is issued
                    
        Outdata = {'Jhist':Jhist, 'Yout':Yout, 'Jout':Jout}
        
                
        return Outdata
    
    def predict(self,X):
        """
        Run a model prediction (forward propagation + scaling)
        """        
        if self.params['Xscaling']:
            X = (X - self.Xbias)/self.Xscale # Lots of broadcasting taking place here
        
        Y, _ = self.forward_propagation(X)
        if self.params['Yscaling']:
            Y = Y*self.Yscale + self.Ybias # Lots of broadcasting also taking place here
        
        return Y
        
def cell_to_vector(W,b):
    """
    Reshapes an array from dictionary-type structure to vector
    """
    nlayers = len(W)
    ntotal = 0
    for i in range (nlayers):
        ntotal+= W[i].shape[0]*W[i].shape[1] + b[i].shape[0]*b[i].shape[1]        
    v = np.zeros([ntotal,1])
    vcount = 0
    for i in range(nlayers):
        vinc = W[i].shape[0]*W[i].shape[1]
        v[vcount:vcount+vinc] = np.reshape(W[i],(vinc,1))
        vcount+= vinc
    for i in range(nlayers):
        vinc = b[i].shape[0]*b[i].shape[1]
        v[vcount:vcount+vinc] = np.reshape(b[i],(vinc,1))
        vcount+= vinc
        
    return v
        
def vector_to_cell(v,W,b):
    """
    Reshapes an array from a 1-D vector to a dictionary-type structure
    """

    nlayers = len(W)
    vcount = 0
    
    for i in range(nlayers):
        vinc = W[i].shape[0]*W[i].shape[1]
        W[i] = np.reshape(v[vcount:vcount+vinc],(W[i].shape[0],W[i].shape[1]))
        vcount+= vinc
    
    for i in range(nlayers):
        vinc = b[i].shape[0]*b[i].shape[1]
        b[i] = np.reshape(v[vcount:vcount+vinc],(b[i].shape[0],b[i].shape[1]))
        vcount+= vinc
    
    return W, b   


