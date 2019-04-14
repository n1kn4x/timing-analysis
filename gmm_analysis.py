import numpy as np
import pandas as pd
from sklearn.mixture import BayesianGaussianMixture
"""
    This file provides functionality for Gaussiam Mixture Modelling.
    It is uses as a utility file for password_timing_analysis.py.
"""

num_queries = None
g = BayesianGaussianMixture(n_components=2,
    weight_concentration_prior=np.finfo(np.longdouble).resolution*2,
    warm_start=True)

def flatten(data):
    data_vec = data.values.flatten()
    data_vec = data_vec[~np.isnan(data_vec)]
    data_vec = data_vec.reshape(-1, 1)
    return data_vec

def max_gaussian(g):
    return g.means_.argmax()

def middle_gaussian(g):
    a = pd.DataFrame([x[0] for x in g.means_])
    idx = a[a==a.median()].dropna().index[0]
    if len(a) % 2 == 0:
        idx = int(idx-.5)
    return idx

def build_gmm(data, states):
    data_vec = flatten(data)
    g.fit(data_vec)
    return g

def get_gmm_predictions(data, g):
    result = pd.DataFrame()
    for char, obs in data.iteritems():
        obs = flatten(obs)
        if len(obs) > 0:
            Y = g.predict(obs)
            u, counts = np.unique(Y, return_counts=True)
            result[char] = pd.Series(counts)
    return result

def get_gmm_prediction_ratios(data, g, idx):
    predictions = get_gmm_predictions(data, g)
    predictions[predictions.isnull()] = 0
    def comp_ratio(counts):
        S = np.sum(counts)
        if S < num_queries*2/3:
            return None
        cc = counts[idx]
        l1, l2 = cc, S
        return l1 / l2
    try:
        ratios = predictions.apply(comp_ratio)
    except:
        print("Couldn't apply GMM successfully")
        return None
    return ratios

def do_gmm_analysis(data, states=2):
    data = data[data > 0]
    g = build_gmm(data, states)
    select_state = max_gaussian(g)
    ratios = get_gmm_prediction_ratios(data, g, select_state)
    return ratios
