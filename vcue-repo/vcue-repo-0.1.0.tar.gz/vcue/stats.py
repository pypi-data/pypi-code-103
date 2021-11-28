# -*- coding: utf-8 -*-
"""
Created on Sat Nov 27 11:24:25 2021

@author: carlo
"""
import random
import pandas as pd
import time 

from sklearn import cluster
from sklearn.metrics import silhouette_score



def iterate_kmeans(df, min_clusters, max_clusters, step=1, seed=1):
    '''
    Fit kmeans for the series range(min_clusters, max_clusters, step )
    
    Parameters
    ----------
    df : numpy.ndarray
        Data to fit.
    min_clusters : int
        minimum # of clusters to try.
    max_clusters : int
        maximum # of clusters to try 
    seed : int, optional
        Set seed. The default is 1.

    Returns
    -------
    mycenters : padnas.DataFrame()
        Returns dataframe with columns 'Clusters' (# of clusters), 'WSS' (inertia), 'Sillouette' (sillouette score)

    '''
    random.seed(seed)
    
    silhouette_scores = []
    
    K=range(min_clusters, max_clusters, step)
    wss = []
    
    start_time = time.time() 
    for k in K:
        loop_start = time.time()
        print('Working on loop',str(k))
        kmeans=cluster.KMeans(n_clusters=k,init="k-means++")
        kmeans=kmeans.fit(df)
        
        # silhouette score
        labels=kmeans.labels_
        silhouette = silhouette_score(df, labels)
        silhouette_scores.append(silhouette)
        
        # inertia
        wss_iter = kmeans.inertia_
        wss.append(wss_iter)
        print('Time for loop:',str((time.time() - loop_start)/60),'min')
        print('Time so far',str((time.time() - start_time)/60),'min')
        
    mycenters = pd.DataFrame({'Clusters' : K, 'WSS' : wss, 'Silhouette': silhouette_scores})
    return mycenters
    
