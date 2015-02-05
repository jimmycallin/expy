import pandas as pd
import seaborn as sns
import numpy as np
from . import measures


def confusion_matrix(actual, predicted):
    confmat = measures.confusion_matrix(actual, predicted).apply(np.log1p)
    return sns.heatmap(confmat)
