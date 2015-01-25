from __future__ import print_function, division, absolute_import
import numpy as np
from sklearn.metrics import precision_score, recall_score, accuracy_score
from sklearn.metrics import f1_score as f1
from scipy.stats import chi2


def precision(actual, predicted):
    return precision_score(actual, predicted)


def recall(actual, predicted):
    return recall_score(actual, predicted)


def f1_score(actual, predicted):
    return f1(actual, predicted)


def accuracy(actual, predicted):
    return accuracy_score(actual, predicted)


def mcnemar_test(ec_a, ec_b):
    """
    McNemar's test. Accepts multidimensional arrays as well, so we can compute the p-value
    for multiple classes at once.

    see
    Detterich, Thomas G, Statistical Tests for Comparing Supervised Classification Learning Algorithms. ( 1997).

    NOTE: Classes with no instances return a p-value of 0
    """
    nc_a = np.logical_not(ec_a)
    nc_b = np.logical_not(ec_b)

    n01 = np.logical_and(nc_a, ec_b).sum(axis=0)
    n10 = np.logical_and(ec_a, nc_b).sum(axis=0)

    # Ignore division by zero on the computation of the statistic, it is the result of unused classes
    prev_set = np.seterr(divide='ignore')
    stat = np.square(np.abs(n01 - n10) - 1 ) / np.array(n01+n10, dtype=float)
    np.seterr(**prev_set)

    rv = chi2(1)
    p = rv.sf(stat)
    return p
