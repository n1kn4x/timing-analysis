import string
import itertools
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import gmm_analysis as ga


"""
    fill_char must not be in alphabet.
"""

class Timea:
    # Default configuration
    def __init__(self,
                query_func,
                length,
                prefix = "",
                fill_char=":",
                queries = 400,
                char_collection = list(string.digits+string.ascii_letters),
                decision_metric = "mean",
                decision_rule = "max",
                gmm_thresh = 0.9,
                percentile = 3
                ):

        assert(decision_metric in
                ["gmm","mean","median","variance","percentile"])
        assert(decision_rule in
                ["max", "min"])
        assert(len(fill_char) == 1)
        self.query_func = query_func
        self.length = length
        self.prefix = prefix
        self.fill_char = fill_char
        self.queries = queries
        self.char_collection = char_collection
        self.decision_metric = decision_metric
        self.decision_rule = decision_rule
        self.thresh = gmm_thresh
        self.percentile = percentile

        ga.num_queries = self.queries

        self.char_collection = [fill_char] + char_collection

        if (self.decision_rule == "max"):
            self.decide = pd.Series.idxmax
        elif (self.decision_rule == "min"):
            self.decide = pd.Series.idxmin

        if (self.decision_metric == "mean"):
            self.analyze = pd.DataFrame.mean
        elif (self.decision_metric == "gmm"):
            self.analyze = ga.do_gmm_analysis
        elif (self.decision_metric == "median"):
            self.analyze = pd.DataFrame.median
        elif (self.decision_metric == "variance"):
            self.analyze = pd.DataFrame.var
        elif (self.decision_metric == "percentile"):
            p = lambda x: np.nanpercentile(x, self.percentile)
            self.analyze = lambda x: pd.DataFrame.apply(x, p)

    def compose_password(self, prefix):
        filler = self.fill_char * (self.length - len(prefix))
        return prefix + filler

    def make_measurements(self, prefix=""):
        all_candidates = [self.compose_password(prefix+char) for char in self.char_collection]
        ref_candidate = self.compose_password(prefix)
        result = pd.DataFrame(columns=self.char_collection)
        for k in range(self.queries):
            measurements = []
            for candidate in all_candidates:
                ref_meas = self.query_func(ref_candidate)
                meas = self.query_func(candidate)
                measurements.append(meas - ref_meas)
            result.loc[k] = measurements
        return result

    def sanitize_data(self, data):
        def outliers(col):
            median = col.median()
            q1 = col.quantile(.1)
            q3 = col.quantile(.9)
            iq_range = q3 - q1
            res = np.logical_or(col > (median + (1.5* iq_range)), \
                                col < (median - (1.5* iq_range)))
            return res

        #apply the function to the original df:
        outlier_mask = data.apply(outliers, axis=0)
        #filter to only non-outliers:
        return data[~(outlier_mask)]

    def get_best_char(self, measurements):
        data = self.analyze(measurements)
        try:
            decision = self.decide(data)
        except:
            return ""
        if self.decision_metric=="gmm" and data[decision] < self.thresh:
            return ""
        print(decision, data[decision])
        return decision

    def run(self):
        prefix = self.prefix

        while (len(prefix) < self.length):
            measurements = self.make_measurements(prefix)
            measurements = self.sanitize_data(measurements)
            next_char = self.get_best_char(measurements)
            prefix = prefix + next_char
            if next_char == "":
                prefix = prefix[:-1]
            print(prefix)
