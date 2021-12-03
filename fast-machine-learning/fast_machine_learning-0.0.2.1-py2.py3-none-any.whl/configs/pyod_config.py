
from pyod.models.abod import ABOD
# from pyod.models.auto_encoder import AutoEncoder
# from pyod.models.auto_encoder_torch import AutoEncoder as AutoEncoderPytorch
from pyod.models.cblof import CBLOF
from pyod.models.cof import COF
from pyod.models.copod import COPOD
# from pyod.models.deep_svdd import DeepSVDD
# from pyod.models.feature_bagging import FeatureBagging
from pyod.models.hbos import HBOS
from pyod.models.iforest import IForest
from pyod.models.knn import KNN
from pyod.models.lmdd import LMDD
from pyod.models.loda import LODA
from pyod.models.lof import LOF
from pyod.models.loci import LOCI
# from pyod.models.lscp import LSCP
# from pyod.models.mad import MAD
from pyod.models.mcd import MCD
# from pyod.models.mo_gaal import MO_GAAL
from pyod.models.ocsvm import OCSVM
from pyod.models.pca import PCA
from pyod.models.rod import ROD
from pyod.models.sod import SOD
# from pyod.models.so_gaal import SO_GAAL
from pyod.models.sos import SOS
# from pyod.models.vae import VAE
from hyperopt import hp


outlier_algos = [
    ABOD,
    # AutoEncoder,
    # AutoEncoderPytorch,
    CBLOF,
    COF,
    COPOD,
    # DeepSVDD,
    # FeatureBagging,
    HBOS,
    IForest,
    KNN,
    LMDD,
    LODA,
    LOF,
    LOCI,
    # LSCP,
    # MAD,
    MCD,
    # MO_GAAL,
    OCSVM,
    PCA,
    ROD,
    SOD,
    # SO_GAAL,
    SOS,
    # VAE,
]
hp_outlier_config = {
    "outlier_algo": hp.choice("outlier_algo", outlier_algos),
    "contamination": hp.uniform("contamination", 0, 0.2),
}