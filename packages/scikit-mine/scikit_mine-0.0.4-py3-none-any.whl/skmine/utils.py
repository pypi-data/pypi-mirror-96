"""
utils functions
"""

import numpy as np
import pandas as pd
from sortedcontainers import SortedList


def _check_random_state(random_state):
    if random_state is None or isinstance(random_state, int):
        random_state = np.random.RandomState(random_state)
    elif not isinstance(random_state, np.random.RandomState):
        raise TypeError("random_state should be an int or a RandomState instance")

    return random_state


def _check_min_supp(min_supp, accept_absolute=True):
    if isinstance(min_supp, int):
        if not accept_absolute:
            raise ValueError(
                "Absolute support is prohibited, please provide a float value between 0 and 1"
            )
        if min_supp < 1:
            raise ValueError("Minimum support must be strictly positive")
    elif isinstance(min_supp, float):
        if min_supp < 0 or min_supp > 1:
            raise ValueError("Minimum support must be between 0 and 1")
    else:
        raise TypeError("Mimimum support must be of type int or float")
    return min_supp


def _check_growth_rate(gr):
    if not gr > 1:
        raise ValueError("growth ratio should be greater than 1")
    return gr


def filter_maximal(itemsets):
    """filter maximal itemsets from a set of itemsets

    Parameters
    ----------
    itemsets: Iterator[frozenset]
        a set of itemsets

    Returns
    -------
    SortedList
    """
    maximals = SortedList(key=len)
    itemsets = sorted(itemsets, key=len, reverse=True)
    for iset in itemsets:
        gts = maximals.irange(iset)
        # is there a superset amongst bigger itemsets ?
        if not any(map(lambda e: e > iset, gts)):
            maximals.add(iset)  # O(log(len(maximals)))

    return maximals


def filter_minimal(itemsets):
    """filter minimal itemsets from a set of itemsets

    Parameters
    ----------
    itemsets: Iterator[frozenset]
        a set of itemsets

    Returns
    -------
    SortedList
    """
    minimals = SortedList(key=len)
    itemsets = sorted(itemsets, key=len)
    for iset in itemsets:
        lts = minimals.irange(None, iset)
        # is there a subset amongst the smaller itemsets ?
        if not any(map(lambda e: e < iset, lts)):
            minimals.add(iset)

    return minimals


def supervised_to_unsupervised(D, y):
    """
    for sklearn compatibility, eg. sklearn.multiclass.OneVSRest

    Parameters
    ----------
    D: pd.DataFrame
        input transactional dataset

    y: np.ndarray of shape (n_samples,)
        corresponding labels
    """
    mask = np.where(y.reshape(-1))[0]
    D = D.iloc[mask]

    return D


def _check_D_sklearn(D):
    if object in D.dtypes.values:  # SKLEARN : check_dtype_object
        raise TypeError("argument must be a string or a number")

    if D.shape[1] == 0:  # SKLEARN : check_empty_data_messages
        raise ValueError("Empty data")

    pd.options.mode.use_inf_as_na = True
    if D.isnull().values.any():
        raise ValueError("esimator does not check for NaN and inf")
    pd.options.mode.use_inf_as_na = False


def _check_D(D):
    if isinstance(D, pd.DataFrame):
        D = D.reset_index(drop=True)  # positional indexing
    elif isinstance(D, np.ndarray):
        D = pd.DataFrame(D)
    else:
        raise TypeError("D should be an instance of np.ndarray or pd.DataFrame")

    _check_D_sklearn(D)

    return D


def _check_y(y):
    if not isinstance(y, (pd.Series, np.ndarray)):
        raise TypeError("y should be an instance of np.ndarray or pd.Series")

    # TODO : pd.Categorical
    return y


def _check_D_y(D, y=None):
    D = _check_D(D)
    if y is not None:
        y = _check_y(y)
    return D, y
