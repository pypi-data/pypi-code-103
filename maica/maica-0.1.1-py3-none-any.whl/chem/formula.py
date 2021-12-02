"""
Chemical Formula
----------------
Before machine learning, the chemical formulas should be converted into the machine-readable feature vectors.
The ``maica.chem.formula`` module provides data_old processing functions to convert
the chemical formulas to the feature vectors.
"""


import numpy
from chemparse import parse_formula
from maica.chem.base import atom_nums


def get_compact_form_vec(form: str,
                         elem_feats: numpy.ndarray):
    """
    Convert a given chemical formula in ``form`` into a feature vector.
    For a set of computed atomic features :math:`S = \{\mathbf{h} = f(e) | e \in c \}`
    where :math:`c` is the given chemical formula, the feature vector is calculated as a concatenated vector based on
    weighted sum with a weight :math:`w_\mathbf{h}`, standard deviation :math:`\sigma`, and max operation as:

    .. math::
        \mathbf{x} = \sum_{\mathbf{h} \in S} w_\mathbf{h} h \oplus \sigma(S) \oplus \max(S).

    Note that the standard deviation :math:`\sigma` and the max operations are applied feature-wise (not element-wise).
    This formula-to-vector conversion method is common in chemical machine learning
    [`1 <https://pubs.acs.org/doi/abs/10.1021/acs.jpclett.8b00124>`_,
    `2 <https://journals.aps.org/prb/abstract/10.1103/PhysRevB.93.115104>`_,
    `3 <https://www.nature.com/articles/s41524-021-00564-y>`_].

    :param form: (*str*) Chemical formula (e.g., ZnIn2S4).
    :param elem_feats: (*numpy.ndarray*) The NumPy array of elemental features.
    :return: (*numpy.ndarray*) A feature vector of the given chemical formula.
    """

    wt_sum_feats = numpy.zeros(elem_feats.shape[1])
    list_atom_feats = list()

    # Convert the refined chemical formula to a dictionary of the chemical formula.
    form_dict = parse_formula(form)
    sum_elem_nums = numpy.sum([float(form_dict[e]) for e in form_dict.keys()])

    # Get atomic features for each element.
    for e in form_dict.keys():
        atom_feats = elem_feats[atom_nums[e] - 1, :]
        list_atom_feats.append(atom_feats)
        wt_sum_feats += (float(form_dict[e]) / sum_elem_nums) * atom_feats

    # Generate a feature vector of the formula based on the weighted sum, std., and max. of the atomic features.
    form_vec = numpy.hstack([wt_sum_feats, numpy.std(list_atom_feats, axis=0), numpy.max(list_atom_feats, axis=0)])

    return form_vec


def get_sparse_form_vec(form: str,
                        elem_feats: numpy.ndarray,
                        max_elems: int):
    """
    Convert a given chemical formula in ``form`` into a feature vector.
    For a set of computed atomic features :math:`S = \{\mathbf{h} = f(e) | e \in c \}`
    where :math:`c` is the given chemical formula, the feature vector is calculated as a concatenated vector of the atomic features.
    If the number of elements is less than ``max_elems``, a zero vector is concatenated to fill the empty values.
    Thus, it always returns the feature vector with the same dimension based on ``max_elems``
    regardless of the number of elements in the chemical formula.

    :param form: (*str*) Chemical formula (e.g., ZnIn2S4).
    :param elem_feats: (*numpy.ndarray*) The NumPy array of elemental features.
    :param max_elems: (*int*) The maximum number of elements in the chemical formula.
    :return: (*numpy.ndarray*) A feature vector of the given chemical formula.
    """

    # The number of features = the number of elemental features + ratio of the atom in the formula.
    form_feats = list()
    form_dict = parse_formula(form)

    # Get atomic features for each element.
    for e in form_dict.keys():
        form_feats.append(float(form_dict[e]))
        form_feats.append(elem_feats[atom_nums[e] - 1, :])

    # Fill zero vectors to the empty features.
    form_feats.append(numpy.zeros((max_elems - len(form_dict)) * (elem_feats.shape[1] + 1)))

    # Generate a sparse feature vector of the given chemical formula.
    form_feats = numpy.hstack(form_feats)

    return form_feats


def get_dop_form_vec(form: str,
                     elem_feats: numpy.ndarray,
                     max_dops: int,
                     dop_threshold: float = 0.1):
    form_host = ''
    form_dop = ''
    form_dict = parse_formula(form)

    # Split the given chemical formula into chemical formulas of the host material and the dopant(s).
    for e in form_dict.keys():
        if form_dict[e] <= dop_threshold:
            form_dop += e + str(numpy.exp(form_dict[e]))
        else:
            form_host += e + str(form_dict[e])

    # Calculate feature vectors of the host material and the dopant(s).
    host_feats = get_compact_form_vec(form_host, elem_feats)
    dop_feats = get_sparse_form_vec(form_dop, elem_feats, max_elems=max_dops)

    return host_feats, dop_feats
