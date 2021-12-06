"""
DATA_PREP - Prepare expression and known covariate data for use in lvreml functions
DATA_PREP prepares the expression and known covariate data for use in
other functions of the lvreml package. Details and rationale are in
Section S2 of the paper.
 
USAGE: [C,Yn,Zn] = data_prep(Y,Z)

INPUT: Y - (n x m) matrix of expression data for m genes in n samples
       Z - (n x d) matrix of data for d covariates (known confounders) in
           n samples

OUTPUT: C  - empirical sample covariance matrix for the expression data,
        Yn - centred expression data (all samples centred to have mean zero)   
        Zn - normalized covariate data (all variables scaled to have unit
             L2 norm)
        
AUTHOR: Muhammad Ammar Malik
        muhammad.malik@uib.no
        https://ammarmalik93.github.io/

REFERENCE: MA Malik and T Michoel. Restricted maximum-likelihood method
for learning latent variance components in gene expression data with
known and unknown confounders.

"""
import numpy as np
import warnings


def data_prep(Y,Z):
# Check that data is in right format (columns are variables, rows are samples)    
    if Z.size != 0:
        if Y.shape[0] != Z.shape[0]:
            # rows are not matching, check columns
            if Y.shape[1] == Z.shape[1]:
                # columns are samples -> transpose both
                Y = Y.T
                Z = Z.T
            else:
                raise Exception('Cannot determine sample dimension')
    else:
        warnings.warn("No covariates provided, assuming expression data is in format samples x genes")
    
    # Center Y to remove fixed effects on mean and get overlap matrix         
    Yn = Y - np.array(Y.mean(axis=1)).reshape(Y.shape[0],1)
    C = np.dot(Yn,Yn.T)/Y.shape[1]
    
    if Z.size != 0:

        Zn = (Z.T/np.sqrt(np.sum(np.square(Z),axis=0)).reshape(Z.shape[1],1)).T
    else:
        Zn = np.empty((0,0))
    return C,Zn,Yn
