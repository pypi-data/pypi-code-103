
import sys, numpy as np, pandas as pd
sys.path.append("..")
from fml.searching import HOIPHyperSearchingWithVotingRegressor as HyperSearching
import joblib

votingmodel = joblib.load("vr.joblib")
a = HyperSearching(verbose=False, verbose_2=True)
a.fit_with_full_range(votingmodel, [["MA", "FA"], ["Pb", "Sn"], ["Cl", "I"]], 1.35, 0.01)
b = a.formulars
c = a.trials
d = pd.DataFrame(c)
