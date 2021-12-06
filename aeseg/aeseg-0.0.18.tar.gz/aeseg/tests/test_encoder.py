from aeseg.Encoder import Encoder
import numpy as np

# Prepare reference curves (normalized between 0 and 1)
reference_curve = np.array([
    [1, 1, 2, 4, 3, 3, 2, 4, 6, 7, 7, 4, 2, 1, 0],
    [1, 1, 2, 4, 3, 3, 2, 4, 6, 7, 7, 4, 2, 1, 0],
    [1, 1, 2, 4, 3, 3, 2, 4, 6, 7, 7, 4, 2, 1, 0],
    [1, 1, 2, 4, 3, 3, 2, 4, 6, 7, 7, 4, 2, 1, 0]
]).T
reference_curve = np.array([reference_curve])

reference_curve = (reference_curve - reference_curve.min()) / (
        reference_curve.max() - reference_curve.min()
)

# Prepare the expected outputs
encode_th_no_th = [{0: [(0.0, 3), (1.0, 1), (0.0, 3), (1.0, 5), (0.0, 3)],
                    1: [(0.0, 3), (1.0, 1), (0.0, 3), (1.0, 5), (0.0, 3)],
                    2: [(0.0, 3), (1.0, 1), (0.0, 3), (1.0, 5), (0.0, 3)],
                    3: [(0.0, 3), (1.0, 1), (0.0, 3), (1.0, 5), (0.0, 3)]
                    }]

encode_th_05th = encode_th_no_th
encode_th_02th = [{0: [(0.0, 2), (1.0, 11), (0.0, 2)],
                   1: [(0.0, 2), (1.0, 11), (0.0, 2)],
                   2: [(0.0, 2), (1.0, 11), (0.0, 2)],
                   3: [(0.0, 2), (1.0, 11), (0.0, 2)]
                   }]

encoder = Encoder(["dog"], 200, 0.2, 150)


# ==============================================================================
#
#       ENCODE THRESHOLD ALGORITHM
#
# ==============================================================================
def test_encode_threshold_no_threhsold():
    assert encoder.encode(
        reference_curve,
        method="threshold"
    ) == encode_th_no_th


def test_encoder_threshold_given_threshold():
    assert encoder.encode(
        reference_curve,
        method="threshold",
        thresholds=[0.5, 0.5, 0.5, 0.5]
    ) == encode_th_05th


def test_encode_th_given_th02():
    assert encoder.encode(
        reference_curve,
        method="threshold",
        thresholds=[0.2, 0.2, 0.2, 0.2]
    ) == encode_th_02th


# ==============================================================================
#
#       ENCODE GMEAN, GMEDIAN, FMEAN, FMEDIAN THREHOLDS
#
# ==============================================================================
r = encoder.encode(reference_curve, method="global_mean_threshold")
print(r)

