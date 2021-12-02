#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jan 18 12:17:48 2021

@author: benjamin
"""

import os
from sklearn.mixture import GaussianMixture
from sklearn import linear_model
import h5py
import numpy as np
import multiprocessing
from joblib import Parallel, delayed
import struct
from feattools import get_delta

def db(x):
    return 20 * np.log10(np.abs(x))

def cc2ceps(x, nwin):
    L = int(nwin / 2 + 1)
    return 10**(np.real(np.fft.fft(x, nwin, axis=0))/20)[:L,:]


def plot_mfcc(mfcc):
    import matplotlib.pyplot as plt
    S = mfcc.mfcc2melspectro()
    plt.figure()
    plt.imshow(np.log10(S.time_frequency_matrix), aspect='auto', origin='lower')

def read_list(list_file):
    fid = open(list_file, 'r')
    list_smpl = fid.readlines()
    fid.close()
    return list_smpl

def get_spk_list(list_smpl):
    spk_id = []
    for spk in list_smpl:
        spk_tmp = spk.split(' ')[0]
        if spk_tmp not in spk_id:
            spk_id.append(spk_tmp)
    return list(np.sort(spk_id))

def get_audio_list(list_smpl, spk):
    list_wom = [x.split(' ')[1] for x in list_smpl if x.split(' ')[0] == spk]
    list_m = [x.split(' ')[2].replace('\n', '') for x in list_smpl if x.split(' ')[0] == spk]

    return list_wom, list_m

def get_spk_id(x):
    file_name = os.path.split(x)[-1]
    return os.path.splitext(file_name)[0]

def get_features(list_audio, path=None, sro=8000,
                 nwin=256, novlp=int(256*3/4), norm='std', axis=0):
    feat_mtx = None
    for audio in list_audio:
        if path is not None:
            audio_file = os.path.join(path, audio)
        else:
            audio_file = audio
        Sp = file2speech(audio_file, sro=sro)
        X, fxx, txx = Sp.computecepstrumenvelope(nwin=nwin, novlp=novlp)
        feat_mtx = concat_mtx(feat_mtx, X)
    return norm_feat(feat_mtx, axis=axis, method=norm)

def get_cc_features(list_audio, nord=32, path=None, sro=8000, nwin=256,
                    novlp=int(256*3/4), norm='zscore', axis=0):

    feat_mtx = None
    for audio in list_audio:
        if path is not None:
            audio_file = os.path.join(path, audio)
        else:
            audio_file = audio
        Sp = file2speech(audio_file, sro=sro)
        X, fxx, txx = Sp.computecepstrumenvelope(nwin=nwin, novlp=novlp)
        L = X.shape[0]
        nfft = 2 * (L - 1)
        X_cc = symmetricifft(db(X), nfft)[:nord,:]
        feat_mtx = concat_mtx(feat_mtx, X_cc)
    return norm_feat(feat_mtx, axis=axis, method=norm)

def get_mfcc_features(list_audio, path=None, sro=8000,
                 nwin=256, novlp=int(256*3/4), norm='zscore',
                 nb_filter=24, nb_coeff=12, axis=0, replace=False):
    feat_mtx = None
    c0 = None
    for audio in list_audio:
        if path is not None:
            audio_file = os.path.join(path, audio)
        else:
            audio_file = audio
        Sp = file2speech(audio_file, sro=sro)
        Sp.mfcc(nwin=nwin, novlp=novlp, nb_filter=nb_filter,
                nb_coeff=nb_coeff, preemph=[1, -0.95],
                win='hamming', replace=replace)
        X = Sp.mfcc.coeff
        if replace:
            c0 = concat_mtx(c0, X[0,:].reshape(1,-1))
        feat_mtx = concat_mtx(feat_mtx, X)
    return (norm_feat(feat_mtx, axis=axis, method=norm), c0)

def norm_feat(A, axis=0, method='std'):

    if method not in ['zscore', 'mean', 'std', 'max']:
        return A

    if method in ['zscore', 'mean']:
        mean_A = np.mean(A, axis=axis, keepdims=True)
    else:
        mean_A = 0
    A = A - mean_A
    if method in ['zscore', 'std']:
        return A / np.std(A, axis=axis, keepdims=True)
    elif method=='max':
        return A / np.max(A, axis=axis, keepdims=True)
    else:
        return A

def concat_mtx(x, y, axis=1):
    if x is None:
        x = y
    elif len(x.shape) == 1:
        x = np.vstack((x.reshape(-1, 1),
                       y.reshape(-1, 1)))
    elif axis == 1:
        x = np.hstack((x,y))
    elif axis == 0:
        x = np.vstack((x,y))
    return x.squeeze()

def gmm(features, nb_gauss):
    clf = GaussianMixture(n_components=nb_gauss, covariance_type='full')
    clf.fit(features)
    return clf

def regul_res(A_source, A_target):
    nb_feat, nb_ph = A_source.shape
    Tk = []
    for k in range(nb_ph):
        As_tmp = A_source[:,k].reshape(-1,1)
        At_tmp = A_target[:,k].reshape(-1,1)
        Tk.append(At_tmp @ np.linalg.pinv(As_tmp))

    return Tk

def trans_oper(A_source_norm, A_target):

    nb_ph, nb_feat = A_source_norm.shape
    Tk = []

    for k in range(nb_ph):
        As_tmp = A_source_norm[k,:].reshape(-1)
        At_tmp = A_target[k,:].reshape(-1)
        Tk.append(At_tmp / As_tmp)

    return Tk

def warp_res(A_targ, W_s, T_k, R_s):
    nb_feat, nb_ph = A_targ.shape
    nb_frame = R_s.shape[1]
    X_t = np.zeros_like(R_s)
    T_k.append(np.eye(nb_feat))
    W_plus = np.vstack((W_s, np.ones((1, nb_frame))))

    for k_fr in range(nb_frame):
        s = 0
        for k_ph in range(nb_ph + 1):
            s += W_plus[k_ph, k_fr] * T_k[k_ph]
        X_t[:, k_fr] = A_targ @ W_s[:, k_fr] + s @ R_s[:, k_fr]

    return X_t

def read_cep(file_name, details=False):
    
    with open(file_name, 'rb') as f:
        file_read = f.read()

    nb_utt = struct.unpack('i', file_read[:4])[0]
    nb_feat = struct.unpack('i', file_read[4:8])[0]
    
    fmat_one = 'f'
    fmat = fmat_one * nb_feat
    nb_byte = 4 * nb_feat
    if fmat_one == 'd':
        nb_byte *= 2
    
    imax = len(file_read)
    i0 = 8 + 4 * nb_utt
    i1 = i0 + nb_byte
    features = []
    while i1 <= imax:
        features.append(struct.unpack(fmat, file_read[i0:i1]))
        i0 += nb_byte
        i1 = i0 + nb_byte
        
    if details:
        nb_frame = struct.unpack('i'*nb_utt, file_read[8:8+4*nb_utt])
        return np.array(features).T, nb_frame
    else:
        return np.array(features).T

def write_cep(file_name, features, nb_frame, nb_utt=None, nb_feat=None):
    if nb_feat is None:
        nb_feat = features.shape[1]
    if nb_utt != len(nb_frame):
        nb_utt = len(nb_frame)
        
    f = open(file_name, 'w+b')
    l1 = struct.pack('i', nb_utt)
    l2 = struct.pack('i', nb_feat)
    f.write(l1)
    f.write(l2)
    
    for curr_frame in nb_frame:
        l3 = struct.pack('i', curr_frame )
        f.write(l3)
    for k1 in range(features.shape[0]):
        for k2 in range(features.shape[1]):
            l4 = struct.pack('f', features[k1, k2])
            f.write(l4)
    f.close()

def get_cep_features(list_cep, path=None):

    feat_mtx = None
    for cep in list_cep:
        if path is not None:
            cep_file = os.path.join(path, cep)
        else:
            cep_file = cep
        X = read_cep(cep_file, details=False)
        feat_mtx = concat_mtx(feat_mtx, X)
    return feat_mtx

def save_spk_model(gmm_model, a_mask, output_name, nd=2):

    hf = h5py.File(output_name, 'w')
    hf.create_dataset('means_nominal', data=gmm_model.means_)
    hf.create_dataset('weights', data=gmm_model.weights_)
    hf.create_dataset('cov', data=gmm_model.covariances_)
    hf.create_dataset('prec', data=gmm_model.precisions_)
    hf.create_dataset('prec_chol', data=gmm_model.precisions_cholesky_)
    hf.create_dataset('means_mask', data=a_mask)
    hf.create_dataset('nb_delta', data=nd)

    hf.close()

def read_spk_model(fileName):

    f = h5py.File(fileName, 'r')
    a_mask = f['means_mask'][()]
    nb_gauss, nb_feat = a_mask.shape
    gmm_model = GaussianMixture(n_components=nb_gauss, covariance_type='full')
    gmm_model.means_ = f['means_nominal'][()]
    gmm_model.weights_ = f['weights'][()]
    gmm_model.covariances_ = f['cov'][()]
    gmm_model.precisions_ = f['prec'][()]
    gmm_model.precisions_cholesky_ = f['prec_chol'][()]

    f.close()
    return gmm_model, a_mask

def read_spk_model_list(file_list):

    A_wom = None
    A_weights = None
    A_cov = None
    A_prec = None
    A_prec_chol = None
    A_m = None
    for fileName in file_list:   
        f = h5py.File(fileName, 'r')
        A_wom = concat_mtx(A_wom, f['means_nominal'][()], axis=0)        
        A_m = concat_mtx(A_m, f['means_mask'][()], axis=0)
        A_weights = concat_mtx(A_weights, f['weights'][()], axis=0)
        A_cov = concat_mtx(A_cov, f['cov'][()], axis=0)
        A_prec = concat_mtx(A_prec, f['prec'][()], axis=0)
        A_prec_chol = concat_mtx(A_prec_chol, f['prec_chol'][()], axis=0)
        nb_gauss, nb_feat = A_wom.shape

    gmm_model = GaussianMixture(n_components=nb_gauss, covariance_type='full')
    gmm_model.means_ = A_wom
    gmm_model.weights_ = A_weights
    gmm_model.covariances_ = A_cov
    gmm_model.precisions_ = A_prec
    gmm_model.precisions_cholesky_ = A_prec_chol

    f.close()
    return gmm_model, A_m

def transform_ceps(gmm_model, features, W_mask, norm='std', axis=0):

    A_source = gmm_model.means_    
    Tk_lin = trans_oper(A_source, W_mask)
    nb_feat, nb_frame = features.shape

    idx_test_atoms = gmm_model.predict(norm_feat(features.T, axis=axis,
                                                            method=norm))
    feat_out = np.zeros_like(features)
    for k in range(nb_frame):
        feat_out[:, k] = Tk_lin[idx_test_atoms[k]] * features[:, k]

    return feat_out

def transform_ceps_sparse(W_nominal, features, W_mask, norm='std', reg='res_only',
                           alpha=0.5, tol=1e-5, max_iter=100000, positive=False):

    clf = linear_model.Lasso(alpha=alpha, tol=tol, max_iter=max_iter,
                             positive=positive)
    
    clf.fit(W_nominal.T, features)
    W = clf.coef_.T
     
    X_nom = W_nominal.T @ W
    Rs = features - X_nom
    W_raw = W_mask.T @ W
    W_res = W_raw + Rs
    Tk = regul_res(W_nominal.T, W_mask.T)  
    W_full = warp_res(W_mask.T, W, Tk, Rs)
    if reg == 'full_all':
        return [W_raw, W_res, W_full]    
    elif reg == 'full_only':
        return W_full
    elif reg == 'res_only':
        return W_res
    elif reg == 'raw_only':
        return W_raw
    else:
        raise ValueError("Wrong method for regularization")

def display_speakers(spk_id, spk_done):
    if spk_done is None:
        l_spk = 'Processing ' + str(len(spk_id)) + ' speakers: '
        for spk in spk_id:
            l_spk += spk + ' '

        print(l_spk[:-1])
    else:
        spk_new_list = [x for x in spk_id if x not in spk_done]
        l_spk = 'Processing ' + str(len(spk_new_list)) + ' remaining speakers: '
        for spk in spk_new_list:
            l_spk += spk + ' '

        print(l_spk[:-1])

def coeff2mfcc(coeff, sro=8000, nb_filter=24, nb_coeff=12, nfft=1024, c0=None):

    filters, mels, mel_freqs = mel_filter_bank(sr=sro, fmin=0, fmax=sro/2,
                                               nb_filter=nb_filter, nfft=nfft)
    if c0 is None:
        c0 = np.array([x for x in coeff[0,:]])
    mfcc_object = MFCC('coeff', coeff, 'frequency_vector', mel_freqs,
                       'time_vector', np.arange(coeff.shape[1]) / sro,
                       'mel_vector', mels, 'nb_coeff', nb_coeff, 'c0', c0)

    return mfcc_object

def comp_list(a, b):
    if len(a) != len(b):
        return False
    for k1, k2 in zip(a, b):
        if k1 != k2:
            return False
        
    return True

def convert_cep_file(cep_file, file_list, method='sparse'):
    gmm_model, W_mask = read_spk_model_list(file_list)
    features = get_cep_features([cep_file], path=None)
    if method == 'sparse':
        return transform_ceps_sparse(gmm_model.means_, features,
                                         W_mask, norm=None)

    elif method == 'linear':
        return transform_ceps(gmm_model, features, W_mask, norm=None, axis=1)
    
def convert_cep_files(cep_list, file_list, method='sparse', path=None,
                      reg='full_all', nd=0):
    gmm_model, W_mask = read_spk_model_list(file_list)
    features = get_delta(get_cep_features(cep_list, path=path).T, nd).T
    if method == 'sparse':
        return transform_ceps_sparse(gmm_model.means_, features, W_mask, 
                                     norm=None, reg=reg)
    elif method == 'linear':
        return transform_ceps(gmm_model, features, W_mask, norm=None)

def convert_audio(audio_file, file_list, sro=8000, nwin=256, novlp=int(256*3/4),
                   norm=None, method='sparse', nb_filter=24, nb_coeff=12,
                  feat_type='ceps', chn=1, axis=0, replace=False):

    Sp = file2speech(audio_file, chn=chn, sro=sro)
    gmm_model, W_mask = read_spk_model_list(file_list)

    if feat_type == 'ceps':
        features = get_features([audio_file], path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, axis=axis)
        norm = 'std'
    if feat_type == 'log_ceps':
        features = get_features([audio_file], path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=None, axis=axis)
        features = np.log(features)
        norm = 'zscore'
    elif feat_type == 'cc':
        nb_coeff = W_mask.shape[1]
        features = get_cc_features([audio_file], nord=nb_coeff, path=None,
                           sro=sro, nwin=nwin, novlp=novlp, norm=norm, axis=axis)
        norm = 'zscore'
    elif feat_type == 'mfcc':
        features, c0 = get_mfcc_features([audio_file], path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, nb_filter=nb_filter,
                            nb_coeff=nb_coeff, axis=axis, replace=replace)
        norm = 'zscore'
    if method == 'sparse':
        feat_out = transform_ceps_sparse(gmm_model.means_, features,
                                         W_mask, norm=norm)

    elif method == 'linear':
        feat_out = transform_ceps(gmm_model, features, W_mask, norm=norm,
                                  axis=axis)
    else:
        raise ValueError('Method is not correct. Choose either sparse or linear')

    if feat_type in ['log_ceps', 'ceps', 'cc']:
        if feat_type == 'cc':
            feat_out = cc2ceps(feat_out, nwin)
        elif feat_type == 'log_ceps':
            feat_out = np.exp(feat_out)        
        return Sp.cepstraltransform(feat_out, nwin=nwin, novlp=novlp,
                                method='target')
    elif feat_type == 'mfcc':
        mfcc_out = coeff2mfcc(feat_out, sro=sro, nb_filter=nb_filter,
                              nb_coeff=nb_coeff, nfft=1024, c0=c0)
        return Sp.cepstraltransform(mfcc_out, nwin=nwin, novlp=novlp,
                                method='target', feat_type='mfcc')

def extract_speaker(spk, list_smpl, spk_done, spk_id, sro, nwin, novlp,
                    nb_gauss, verb, ext_name, feat_type, nb_filter, nb_coeff,
                    axis, replace):
    list_wom, list_m = get_audio_list(list_smpl, spk)

    if verb:
        display_speakers(spk_id, spk_done)
        print('Extracting features of ' + spk + '...')
    if feat_type == 'ceps':
        norm = 'std'
        feat_wom = get_features(list_wom, path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, axis=axis)
        feat_m = get_features(list_m, path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, axis=axis)
    elif feat_type == 'log_ceps':
        norm = None
        feat_wom = get_features(list_wom, path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, axis=axis)
        feat_m = get_features(list_m, path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, axis=axis)
        feat_wom = norm_feat(np.log(feat_wom), axis=axis, method='zscore')
        feat_m = norm_feat(np.log(feat_m), axis=axis, method='zscore')

    elif feat_type == 'mfcc':
        norm = 'zscore'
        feat_wom, c0 = get_mfcc_features(list_wom, path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, nb_filter=nb_filter,
                            nb_coeff=nb_coeff, axis=axis, replace=replace)
        feat_m, c0 = get_mfcc_features(list_m, path=None, sro=sro, nwin=nwin,
                            novlp=novlp, norm=norm, nb_filter=nb_filter,
                            nb_coeff=nb_coeff, axis=axis)
    elif feat_type == 'cc':
        norm = 'zscore'
        feat_wom = get_cc_features(list_wom, nord=nb_coeff, path=None,
                           sro=sro, nwin=nwin, novlp=novlp, norm=norm, axis=axis)
        feat_m = get_cc_features(list_m, nord=nb_coeff, path=None,
                           sro=sro, nwin=nwin, novlp=novlp, norm=norm, axis=axis)

    if verb:
        print('Extracting features of ' + spk + ' done')
        print('Estimating ' + str(nb_gauss) + ' gaussians for ' + spk + ' without mask...')

    clf_wom = gmm(feat_wom.T, nb_gauss)

    if verb:
        print('Estimating ' + str(nb_gauss) + ' gaussians for ' + spk + ' without mask done')

    idx_atoms = clf_wom.predict(feat_m.T)
    n_gauss_final = len(np.unique(idx_atoms))

    clf_wom.n_components = n_gauss_final
    if verb:
        print('Keeping ' + str(n_gauss_final) + ' gaussians out of ' + str(nb_gauss))
    clf_wom.means_ = clf_wom.means_[np.unique(idx_atoms),:]
    clf_wom.weights_ = clf_wom.weights_[np.unique(idx_atoms)]
    clf_wom.covariances_ = clf_wom.covariances_[np.unique(idx_atoms),:]
    clf_wom.precisions_ = clf_wom.precisions_[np.unique(idx_atoms),:]
    clf_wom.precisions_cholesky_ = clf_wom.precisions_cholesky_[np.unique(idx_atoms),:]

    A_wom = clf_wom.means_
    A_m = np.zeros_like(A_wom)

    for k_idx, idx in enumerate(np.unique(idx_atoms)):
        X = np.array([feat_m[:, x] for x in idx_atoms if x == idx])
        A_m[k_idx, :] = np.mean(X, 0)

    output_name = os.path.join(ext_name, spk + '.h5')
    save_spk_model(clf_wom, A_m, output_name)
    print('Dictionary file for ' + spk + ' has been successfully saved')
    if spk_done is None:
        spk_done = [spk]
    else:
        spk_done.append(spk)
        
        
def extract_speaker_2(spk, list_smpl_nomask, list_smpl_mask, spk_done, spk_id,
                    nb_gauss, verb, ext_name, nd):
    
    list_wom = [x for x in list_smpl_nomask if get_spk_id(x) == spk]
    list_m = [x for x in list_smpl_mask if get_spk_id(x) == spk]

    if verb:
        display_speakers(spk_id, spk_done)
        print('Extracting features of ' + spk + '...')
    
    feat_wom = get_delta(get_cep_features(list_wom, path=None).T, nd).T
    feat_m = get_delta(get_cep_features(list_m, path=None).T, nd).T
   
    if verb:
        print('Extracting features of ' + spk + ' done')
        print('Estimating ' + str(nb_gauss) + ' gaussians for ' + spk + ' without mask...')

    clf_wom = gmm(feat_wom.T, nb_gauss)

    if verb:
        print('Estimating ' + str(nb_gauss) + ' gaussians for ' + spk + ' without mask done')
    
    # clf_wom.means_ = (clf_wom.means_ , 1, 'zscore')
    idx_atoms = clf_wom.predict(feat_m.T)
    n_gauss_final = len(np.unique(idx_atoms))

    clf_wom.n_components = n_gauss_final
    if verb:
        print('Keeping ' + str(n_gauss_final) + ' gaussians out of ' + str(nb_gauss))
    clf_wom.means_ = clf_wom.means_[np.unique(idx_atoms),:]
    clf_wom.weights_ = clf_wom.weights_[np.unique(idx_atoms)]
    clf_wom.covariances_ = clf_wom.covariances_[np.unique(idx_atoms),:]
    clf_wom.precisions_ = clf_wom.precisions_[np.unique(idx_atoms),:]
    clf_wom.precisions_cholesky_ = clf_wom.precisions_cholesky_[np.unique(idx_atoms),:]

    A_wom = clf_wom.means_
    A_m = np.zeros_like(A_wom)

    for k_idx, idx in enumerate(np.unique(idx_atoms)):
        X = np.array([feat_m[:, x] for x in idx_atoms if x == idx])
        A_m[k_idx, :] = np.mean(X, 0)

    output_name = os.path.join(ext_name, spk + '.h5')
    
    save_spk_model(clf_wom, A_m, output_name, nd)
    print('Dictionary file for ' + spk + ' has been successfully saved')
    if spk_done is None:
        spk_done = [spk]
    else:
        spk_done.append(spk)

def extract_dict(list_file, nb_gauss, sro, nwin, novlp, ext_name, njobs, verb,
                  feat_type, nb_filter, nb_coeff, axis, replace):
    list_smpl = read_list(list_file)
    spk_id = get_spk_list(list_smpl)
    spk_done = None

    njobs = min(njobs, len(spk_id))
    print('Expected number of parallel jobs is ' + str(njobs))
    if njobs > 1:
        verb = False
        display_speakers(spk_id, spk_done)

    if not os.path.isdir(ext_name):
        os.mkdir(ext_name)

    pList = Parallel(n_jobs=njobs)(delayed(extract_speaker)(spk,
                          list_smpl, spk_done, spk_id, sro, nwin, novlp,
                    nb_gauss, verb, ext_name, feat_type,
                    nb_filter, nb_coeff, axis, replace) for spk in spk_id)
    print('All dictionaries have been successfully saved')
    
def extract_dict_2(nomask_set, mask_set, nb_gauss, ext_name, njobs, nd, verb, spk):
    
    list_cep_nomask = [os.path.join(nomask_set, x) for x in np.sort(os.listdir(nomask_set))
                       if '.cep' in x]
    list_cep_mask = [os.path.join(mask_set, x) for x in np.sort(os.listdir(mask_set))
                       if '.cep' in x]
    
    spk_id_nom = [os.path.splitext(x)[0] for x in np.sort(os.listdir(nomask_set)) if '.cep' in x]
    spk_id_mask = [os.path.splitext(x)[0] for x in np.sort(os.listdir(mask_set)) if '.cep' in x]
    
    if not comp_list(spk_id_nom, spk_id_mask):
        raise ValueError('Speaker lists are different. ' + 
                         'Please ensure speakers are the same for both mask and non-mask lists')
    spk_id = get_spk_list(spk_id_nom)
    if spk is not None:
        spk_id = [x for x in spk_id if x in spk]
    spk_done = None
    njobs = min(njobs, len(spk_id))
    print('Expected number of parallel jobs is ' + str(njobs))
    if njobs > 1:
        verb = False
        display_speakers(spk_id, spk_done)

    if not os.path.isdir(ext_name):
        os.mkdir(ext_name)

    pList = Parallel(n_jobs=njobs)(delayed(extract_speaker_2)(spk,
                          list_cep_nomask, list_cep_mask, spk_done, spk_id,
                    nb_gauss, verb, ext_name, nd) for spk in spk_id)
    print('All dictionaries have been successfully saved')
