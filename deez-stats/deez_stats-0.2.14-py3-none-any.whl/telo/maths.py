import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import expon


elo = [854, 821, 765, 721, 716, 701, 691, 671, 671, 625, 621, 617]


plt.plot(elo,'.')
# plt.hist(elo, density=True, histtype='stepfilled', alpha=0.2)
plt.show()