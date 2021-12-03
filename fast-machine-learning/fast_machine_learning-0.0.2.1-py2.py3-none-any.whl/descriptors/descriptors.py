
import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.preprocessing import LabelEncoder

selfpath = Path(Path(__file__).parent.resolve(), "dfs")

base_descriptor = pd.read_pickle(Path(selfpath, "base_descriptor.df"))
str_bool_descriptor = pd.read_pickle(Path(selfpath, "str_bool_descriptor.df"))
other_descriptor = pd.read_pickle(Path(selfpath, "other_descriptor.df"))
ionization_descriptor = pd.read_pickle(Path(selfpath, "ionization.df"))
ionic_radii_descriptor = pd.read_pickle(Path(selfpath, "ionic_radii.df"))
descriptor_name = pd.read_pickle(Path(selfpath, "name.df"))

onehot_str_bool_descriptor = []
str_bool_descriptor_fill_na = str_bool_descriptor.fillna("nan")
for i in range(str_bool_descriptor.shape[1]):
    tmp = LabelEncoder().fit_transform(str_bool_descriptor_fill_na.iloc[:, i])
    onehot_str_bool_descriptor.append(pd.Series(tmp))
onehot_str_bool_descriptor = pd.concat(onehot_str_bool_descriptor, axis=1)
onehot_str_bool_descriptor.index = str_bool_descriptor.index
onehot_str_bool_descriptor.columns = str_bool_descriptor.columns

def base_descriptor_func(atom):
    return base_descriptor.loc[atom]

def str_bool_descriptor_func(atom):
    return str_bool_descriptor.loc[atom]
def onehot_str_bool_descriptor_func(atom):
    return onehot_str_bool_descriptor.loc[atom]

def other_descriptor_func(atom):
    return other_descriptor.loc[atom]

def ionization_func(atom, degree=1):
    tmp = ionization_descriptor[ionization_descriptor.degree == degree]
    tmp = tmp.loc[atom]
    return pd.Series(tmp.iloc[-1], index=["ionization"])

def ionic_radii_func(atom, charge=None, coordination=None, spin=None):
    tmp = ionic_radii_descriptor
    if charge is not None:
        tmp = tmp[tmp.charge == charge]
    if coordination is not None:
        tmp = tmp[tmp.coordination == coordination]
    if spin is not None:
        tmp = tmp[tmp.spin == spin]
    
    try:
        tmp = tmp.loc[atom]
    except:
        tmp = ionic_radii_descriptor.loc[atom]
    if len(tmp.shape) > 1:
        tmp = tmp.iloc[0, :]
    return pd.Series(tmp.iloc[-1], index=["_ionic_radius_"])

B_site_chgs = {
    "Bi": 3,
    "Ag": 1,
    "La": 3,
    "Tb": 3,
    "Sb": 3,
    }
A_site_coors = {
    "Cs": "XII",
    "K": "XII",
    "Li": "VIII",
    "Na": "XII",
    "Rb": "XII"
    }

class Atom(object):
    
    def __init__(self, base=True, str_bool=True, other=False, ionization=True, ionic_radii=True):
        
        self.base = base
        self.str_bool = str_bool
        self.other = other
        self.ionization = ionization
        self.ionic_radii = ionic_radii

    def describe(self, atom, degree=1, charge=None, coordination=None, spin=None, ratio=1, prefix_name="", onehot=False):
        descriptors = []
        for index, flag, func in zip(
                range(5),
                [self.base, self.str_bool, self.other, self.ionization, self.ionic_radii],
                [base_descriptor_func, str_bool_descriptor_func, other_descriptor_func, ionization_func, ionic_radii_func]
        ):
            if flag:
                ratio = float(ratio)
                if index <= 2:
                    if onehot:
                        if func == str_bool_descriptor_func:
                            func = onehot_str_bool_descriptor_func
                        descriptors.append(func(atom) * ratio)
                    else:
                        if index == 1:
                            descriptors.append(func(atom))
                        else:
                            descriptors.append(func(atom) * ratio)
                elif index == 3:
                    descriptors.append(func(atom, degree) * ratio)
                elif index == 4:
                    descriptors.append(func(atom, charge, coordination, spin) * ratio)
        descriptors = pd.concat(descriptors)
        descriptors.index = prefix_name + descriptors.index
        return descriptors

class HOIP(Atom):

    """
    formualr: [
        {
            "MA": 0.7,
            "FA": 0.3,
        },
        {
            "Pb": 0.1,
            "Sn": 0.9,
        },
        {
            "Cl": 2.7,
            "Br": 0.3,
        },

    ]
    """

    def __init__(self, base=True, str_bool=True, other=False, ionization=True, ionic_radii=True):
        super(HOIP, self).__init__(base, str_bool, other, ionization, ionic_radii)
        pass

    def describe_formular(self, formular, onehot=None):
        formular_name = ""
        a_site = formular[0]
        b_site = formular[1]
        c_site = formular[2]
        a_site_descriptor = None
        for atom, ratio in a_site.items():
            if onehot is None:
                if len(a_site) == 1:
                    onehot = False
                else:
                    onehot = True
            else:
                onehot = onehot
            if atom in A_site_coors.keys():
                coordination = A_site_coors[atom]
            else:
                coordination = "VI"
            d = self.describe(atom, degree=1, charge=1, coordination=coordination, spin=None, ratio=ratio, prefix_name="A_", onehot=onehot)
            if a_site_descriptor is None:
                a_site_descriptor = d
            else:
                a_site_descriptor += d
            formular_name += str(atom)
            if float(ratio) != 1:
                formular_name += str(ratio)

        b_site_descriptor = None
        for atom, ratio in b_site.items():
            if onehot is None:
                if len(b_site) == 1:
                    onehot = False
                else:
                    onehot = True
            else:
                onehot = onehot
            if atom in B_site_chgs.keys():
                charge = B_site_chgs[atom]
            else:
                charge = 2
            d = self.describe(atom, degree=1, charge=charge, coordination="VI", spin=None, ratio=ratio, prefix_name="B_", onehot=onehot)
            if b_site_descriptor is None:
                b_site_descriptor = d
            else:
                b_site_descriptor += d
            formular_name += str(atom) 
            if float(ratio) != 1:
                formular_name += str(ratio)

        c_site_descriptor = None
        for atom, ratio in c_site.items():
            formular_name += str(atom) 
            if float(ratio) != 1:
                formular_name += str(ratio)
            ratio = float(ratio) / 3
            if onehot is None:
                if len(c_site) == 1:
                    onehot = False
                else:
                    onehot = True
            else:
                onehot = onehot
            d = self.describe(atom, degree=1, charge=-1, coordination="VI", spin=None, ratio=ratio, prefix_name="C_", onehot=onehot)
            if c_site_descriptor is None:
                c_site_descriptor = d
            else:
                c_site_descriptor += d
            

        adds = None
        if self.ionic_radii:
            a_radii = a_site_descriptor.A__ionic_radius_
            b_radii = b_site_descriptor.B__ionic_radius_
            c_radii = c_site_descriptor.C__ionic_radius_

            tf = tolerance_factor(a_radii, b_radii, c_radii)
            tau = tau_factor(1, a_radii, b_radii, c_radii)
            of = octahedral_factor(b_radii, c_radii)

            adds = pd.Series([tf, tau, of], index=["tf", "tau", "of"])
        series = [a_site_descriptor, b_site_descriptor, c_site_descriptor]
        if adds is not None:
            series.append(adds)
        series = pd.concat(series)
        series.name = formular_name
        return series

def tolerance_factor(ra, rb, rc):
    return (ra + rc) / (np.sqrt(2) * (rb + rc))

def tau_factor(na, ra, rb, rc):
    left = rc/rb
    right_denominator = np.log(ra/rb)
    right_numerator = ra/rb
    right = na * (na - right_numerator/right_denominator)
    return left - right

def octahedral_factor(rb, rc):
    return rb/rc