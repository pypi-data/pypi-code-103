import sys
sys.path.append("C:/Users/dheiver/Desktop/KalmanFilter/KalmanFilter")
from train_df import train_df
from pykalman import KalmanFilter

class KalmanFilter:

    for cols in train_df.columns:
        if cols == 'id':
            continue
        if cols == 'cycle':
            continue
        else:
        # print(cols)
            kf = KalmanFilter(transition_matrices = [1],
                        observation_matrices = [1],
                        initial_state_mean = train_df[cols].values[0],
                        initial_state_covariance = 1,
                        observation_covariance=1,
                        transition_covariance=.01)
            state_means,_ = kf.filter(train_df[cols].values)
            train_df[cols] = state_means.flatten()
