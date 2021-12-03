from scipy.signal import find_peaks
import numpy as np

def superSample(y1, mult):
    """

    INPUT:
    y1: the 1D cross-shore surface water elevation vector
    mult: the supersampling multiplier [1D array]

    mult: multiple [number]

    OUTPUT:
    y2: the resulting supersampled cross-shore surface water elevation vector,
    with length mult * len(y1)

    So for example y1 would be the surface water elevation at a single cross-shore
    profile, and we want to do 10x supersampling. So mult = 10 and y2
    would be the supersampled timeseries, which would have length multi *
    len(y1).

    """

    sz1 = len(y1)
    x1 = np.arange(sz1)
    x2 = np.linspace(0, sz1 - 1, (sz1 - 1) * mult + 1)
    y2 = np.interp(x2, x1, y1)
    return y2

def runup_func(eta_original, h_original, x, r_depth=None):
    """

    Parameters:
    ----------
    eta          : Water surface elevation time series [m] [1D in cross-shore]
    h            : Bathymetry [m] (positive down)  [cross-shore bathy]
    x            : x coordinates of h [m]          [cross-shore position]
    r_depth      : Runup depth [m] (optional)

    Output:
    -------
    runup        : Water surface elevation time series relative to SWL given
                   a contour depth [m]
    x_runup      : Across-shore location of runup time series [m]
    r_depth      : Contour depth that was tracked

    Notes:
    ------
    - Really meant for 1D simulations.
    - Minimum runup depth as suggested by Salmon 2002 is estimated as
      h0 = 4 * max(dh)

    """
    h = superSample(h_original, 10)
    eta = superSample(eta_original, 10)

    # Find the maximum runup depth
    if r_depth is None:
        runupInd = h < 1.0
        r_depth = 4.0 * np.nanmax(np.abs(h[runupInd][1:] - h[runupInd][:-1]))

        # Preallocate runup variable
    runup = np.zeros(eta.shape[0])
    x_runup = np.zeros_like(runup)

    # Water depth
    wdepth = eta + h

    # Find the runup contour (search from left to right)
    wdepth_ind = np.argmax(wdepth >= r_depth)

    # Store the water surface elevation in matrix
    runup = eta[wdepth_ind]  # unrealistic values for large r_depth
    # runup[aa]= -h[wdepth_ind]

    # Store runup position
    x_runup = x[wdepth_ind]

    # Done
    return runup, x_runup, r_depth

def timeSeriesAnalysis1D(time, eta, **kwargs):
    """process 1D timeserise analysis, function will demean data by default.  It can operate on
    2D spatial surface elevation data, but will only do 1D analysis (not puv/2D directional waves)
    for frequency band averaging, will label with band center

    Args:
        time: time (datetime object)
        eta: surface timeseries

        **kwargs:
            'windowLength': window length for FFT, units are minutes (Default = 10 min)
            'overlap': overlap of windows for FFT, units are percentage of window length (Default=0.75)
            'bandAvg': number of bands to average over (default=3)
            'timeAx' (int): a number defining which axis in eta is time (Default = 0)
            'returnSetup' (bool): will calculate and return setup (last postion)  (Default = False)
            'confInterval' (float): confidence interval for DOF calculation (Default=0.95)

    Returns:
        fspec (array): array of power spectra, dimensioned by [space, frequency]
        frqOut (array): array of frequencys associated with fspec

    Raises:
        Warnings if not all bands are processed (depending on size of freqeuency bands as output by FFT
            and band averaging chosen, function will neglect last few (high frequency) bands

    TODO:
        can add surface correction for pressure data

    """
    raise NotImplementedError('please use waveLib analysis scripts, they''re more advanced')
    # function [fm, Spp, Spplo, Sppup, nens, dof] = get_spectrum(P, nfft, fs,alpha)
    # % [fm, Spp, Spplo, Sppup, nens, dof] = get_spectrum(P, nfft, fs,alpha)
    # % Makes a spectrum for a single point only
    # %
    # % Input:
    # %   P: timeseries to be analyzed (should be size (nt,1))
    # %   nfft: window size for spectral averaging
    # %   fs: sampling rate (Hz)
    # %   alpha: for confidence intervals (alpha = 0.05 is standard 95% Conf Int)
    # %
    # % Output:
    # %   fm: frequency
    # %   Spp: Spectra (inputUnits^2/Hz)
    # %   Spplo/Sppup: lower and upper bounds of confidence intervals
    # %   nens: number of ensembles used
    # %   dof: degrees of freedom
    #
    # [m,n] = size(P);
    # if m<n
    #     P = P';
    # [Amp,nens] = calculate_fft2(P(:,1),nfft,fs);
    # nens2 = 0;
    #
    # % TODO: FIX THIS, FOR NOW only use one-dim P
    # % if n==2
    # % [Amp2,nens2] = calculate_fft2(P(:,2),nfft,fs);
    # % Amp = [Amp; Amp2];
    # % end
    #
    # df = fs/(nfft-1);   % This is the frequency resolution
    # nnyq = nfft/2 +1;
    #
    # fm = [0:nnyq-1]*df;
    # Spp = mean( Amp .* conj(Amp) ) / (nnyq * df);  % need to normalize by freq resolution
    # Spp = Spp(1:nnyq);
    # nens = nens+nens2;
    # % Confidence Intervals (CI)
    # dof = 8/3*nens; % for Hanning window
    #
    # a = dof.*sum(Spp).^2./(sum(Spp.^2)); % effective dof
    # adof = a/(1+2/dof); % unbiased edof
    #
    # chi2 = [chi2inv(alpha/2,dof) chi2inv(1-alpha/2,dof)];
    # CI_chi2 = [(1/chi2(1)).*(dof*Spp) (1/chi2(2)).*(dof*Spp)];
    # Spplo = CI_chi2(:,1);
    # Sppup = CI_chi2(:,2);

    from scipy.signal import welch
    import warnings
    assert isinstance(time, np.ndarray), 'Must be input as an array'
    assert isinstance(time[0], float), 'time must not be in datetime'
    ## kwargs below
    nPerSeg = kwargs.get('WindowLength', 10) * 60   # window length (10 minutes in seconds)
    overlapPercentage = kwargs.get('overlap', 3/4)  # 50% overlap per segment
    bandAvg = kwargs.get('bandAvg', 6)              # average 6 bands
    myAx = kwargs.get('timeAx', 0)                  # time dimension of eta
    alpha = 1 - kwargs.get('confInterval', 0.95)    # confidence interval used for degrees of freedom calculation
    overlap = nPerSeg * overlapPercentage
    ## preprocessing steps
    etaDemeaned = np.nan_to_num(eta - np.nanmean(eta, axis=0))

    # etaDemeaned = np.ma.masked_array(etaD, mask=np.isnan(eta).data, fill_value=-999)   # demean surface time series
    assert eta.shape[myAx] == time.shape[0], "axis selected for eta doesn't match time"
    freqSample = 1/np.median(np.diff(time))

    freqsW, fspecW = welch(x=etaDemeaned, window='hanning', fs=freqSample, nperseg=int(nPerSeg *freqSample),
                           noverlap=int(overlap*freqSample), nfft=None, return_onesided=True, detrend='linear',
                           axis=myAx)
    # remove first index of array (DC components)--?
    freqW = freqsW[1:]
    fspecW = fspecW[1:]
    ## TODO: add surface correction here

    # initalize for band averaging
    # dk = np.floor(bandAvg/2).astype(int)  # how far to look on either side of band of interest
    frqOut, fspec = [], []
    for kk in range(0, len(freqsW), bandAvg):
        avgIdxs = np.linspace(kk, kk + bandAvg - 1, num=bandAvg).astype(int)
        try:
            frqOut.append(freqW[avgIdxs].sum(axis=myAx) / len(avgIdxs))  # taking average of freq for label (band centered label)
            fspec.append(fspecW[avgIdxs].sum(axis=myAx) / len(avgIdxs))
        except IndexError:  # when there's not enough bins to average
            warnings.warn('neglected last {} freq bands (at highest frequency)'.format(max(avgIdxs) - kk))

    frqOut = np.array(frqOut).T
    fspec = np.array(fspec).T
    # output as masked array
    # fspec = np.ma.masked_array(fspec, mask=np.tile((fspec == 0).all(axis=1), (frqOut.size, 1)).T)
    out = {'fspec': fspec,
           'freq': frqOut}
    return out

def identifyR2(runupTS, plot=False, percentile=2):
    """find R2 percentage from a runup time series.  Uses traditional method of only identifying one peak per up
    crossing (stockdon '03).  Algorithm will find first time point in past the zero location point.  There's a
    smarter way to find the apprpriate peaks.  The current method is slow.

    Args:
        runupTS: runup time-series  elevation values [elevation value]
        plot(bool): turn QA/QC plots on/off
        percentile: pick top X percentile (default=2).  Code will take 100-x to find percentile of CDF (e.g. 98%)
    
    Returns:
        R2: demeaned 2 percent runupTS exceedance
        peaks: locations of max zero crossing values
        setup: mean of the runupTS

    TODO:
        - fit an analytical model to R2 calculation
        - increase speed
        
    """
    invPer = 100 - percentile
    setup = np.nanmean(runupTS)
    runupTS = runupTS - setup  # demean setup

    # calculate up and downcrossings
    downcrossings, upcrossing = [], []
    for rr, R in enumerate(runupTS):
        if rr > 1 and runupTS[rr] >= 0 and runupTS[rr - 1] < 0:
            upcrossing.append(rr),
        elif rr > 1 and runupTS[rr] <= 0 and runupTS[rr - 1] > 0:
            downcrossings.append(rr)
    
    downcrossings = np.array(downcrossings)
    upcrossing = np.array(upcrossing)
    downcrossings = downcrossings[downcrossings > upcrossing[0]]  # start on an upcrossing
    upcrossing = upcrossing[upcrossing < downcrossings[-1]]       # finish on a downcrossing
    peaks = []
    
    for ii, uc in enumerate(upcrossing):
        rangeR2 = runupTS[upcrossing[ii]:downcrossings[ii]]
        idx = uc + np.argwhere(max(rangeR2) == rangeR2).squeeze()
        if np.size(idx) > 1:
            idx = idx[0]
        peaks.append(idx)   # arg max provides weird answers some times
    
    assert len(peaks) == len(upcrossing) == len(downcrossings), 'Calculating R2, the peak count does''t match ' \
                                                                ' up/down crossings'
    
    R2 = np.percentile(np.array(runupTS)[np.array(peaks).astype(int)], invPer)

    if plot is True:
        from matplotlib import pyplot as plt
        plt.figure()
        plt.plot(runupTS, label='runupTS')
        plt.plot(upcrossing,np.zeros_like(upcrossing), 'r.', label="identifed upcrossing points")
        plt.plot(peaks, runupTS[peaks], 'x', label='identified runupTS peaks')
        plt.legend()

    return R2, np.array(peaks), setup

def identifyRunupTS(timeDT, xFRF, eta, bathy, **kwargs):
    """runup time series identification from eta
    
    Args:
        timeDT:
        xFRF:
        eta:
        bathy:
        **kwargs:
            r_depth - runup contour to track
    Returns:

    """
    r_depth = kwargs.get('runupDepthContour', 0.1)
    # first identify Runup timeseries
    runupTS = np.zeros_like(timeDT, dtype=float)
    xFRF_runup = np.zeros_like(timeDT, dtype=float)
    for aa in range(runupTS.shape[0]):
        wdepth = eta[aa, :] + bathy # Water depth
        # Find the runup contour (search from left to right)
        wdepth_ind = np.argmin(abs(wdepth - r_depth))  # changed from Chuan's original code
        # Store the water surface elevation in matrix
        runupTS[aa] = eta[aa, wdepth_ind]  # unrealistic values for large r_depth
        # Store runup position
        xFRF_runup[aa] = xFRF[wdepth_ind]
    return runupTS, xFRF_runup