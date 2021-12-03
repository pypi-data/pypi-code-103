import sys, numpy as np, pandas as pd
sys.path.append("..")
from fml.searching import HOIPHTSWithVotingRegressor as HTS
import joblib

votingmodel = joblib.load("vr.joblib")
hts = HTS(verbose=True)
formular_info = [
    ["MA", "FA", "Cs", "K"], 
    ["Pb", "Sn"], 
    ["Cl", "I"]
    ]
hts.fit_with_full_range(votingmodel, formular_info, [2, 1, 1], [0.1, 0.1, 0.5])
predictions = hts.predictions
predictions_2 = hts.predictions_2
