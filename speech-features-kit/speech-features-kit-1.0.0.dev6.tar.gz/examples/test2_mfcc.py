import speech_features_kit.MFCC.MFCC as mf

import scipy.io.wavfile as wav

(rate,sig) = wav.read("../data/english.wav")
mfcc_feat = mf.mfcc(sig, rate)
d_mfcc_feat = mf.delta(mfcc_feat, 2)
fbank_feat = mf.logfbank(sig, rate)

print(fbank_feat[1:3,:])
