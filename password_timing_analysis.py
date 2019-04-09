import string
import itertools
import numpy as np
import pandas as pd

import matplotlib.pyplot as plt


"""
    fill_char must not be in alphabet.
"""

def build_char_combinations(char_collection,
                            combi_size):
    assert(combi_size > 0)
    char_combinations = itertools.product(char_collection,
                                          repeat=combi_size)

    return list(map(lambda chars: ''.join(chars), char_combinations))

class Timea:
    # Default configuration
    def __init__(self,
                query_func,
                length,
                prefix = "",
                fill_char=":",
                queries = 4,
                char_collection = string.digits + string.ascii_letters,
                combi_size = 1,
                decision_metric = "mean",
                decision_rule = "max",
                percentile = 3
                ):

        assert(decision_metric in
                ["mean","median","variance","percentile"])
        assert(decision_rule in
                ["max", "min"])
        assert(len(fill_char) == 1)
        self.query_func = query_func
        self.length = length
        self.prefix = prefix
        self.fill_char = fill_char
        self.queries = queries
        self.char_collection = char_collection
        self.combi_size = combi_size
        self.decision_metric = decision_metric
        self.decision_rule = decision_rule
        self.percentile = percentile

        self.char_collection = fill_char + char_collection
        self.char_combis = build_char_combinations(self.char_collection,
                                                        self.combi_size)

        if (self.decision_rule == "max"):
            self.decide = pd.Series.idxmax
        elif (self.decision_rule == "min"):
            self.decide = pd.Series.idxmin
        if (self.decision_metric == "mean"):
            self.analyze = np.nanmean
        elif (self.decision_metric == "median"):
            self.analyze = np.nanmedian
        elif (self.decision_metric == "variance"):
            self.analyze = np.nanvar
        elif (self.decision_metric == "percentile"):
            self.analyze = lambda x: np.nanpercentile(x, self.percentile)


    def compose_password(self, prefix):
        filler = self.fill_char * (self.length - len(prefix))
        return prefix + filler

    def make_measurements(self, prefix=""):
        all_candidates = [self.compose_password(prefix+char) for char in self.char_combis]
        ref_candidate = self.compose_password(prefix)
        result = pd.DataFrame(columns=self.char_combis)
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
            q1 = col.quantile(.10)
            q3 = col.quantile(.90)
            iq_range = q3 - q1
            res = np.logical_or(col > (median + (1.5* iq_range)), \
                                col < (median - (1.5* iq_range)))
            return res

        #apply the function to the original df:
        outlier_mask = data.apply(outliers, axis=0)
        #filter to only non-outliers:
        return data[~(outlier_mask)]

    def get_best_char(self, measurements):
        if self.combi_size == 1:
            del measurements[self.fill_char]
        #measurements = measurements[measurements >= 0]
        data = measurements.apply(self.analyze, axis=0)
        decision = self.decide(data)
        print(decision)
        print(data[decision])
        """
        # DEBUG
        plt.figure()
        plt.hist(10**6*measurements[decision], 100, color='green',alpha=0.8)#, range=(-1.5, 1.5))
        plt.axvline(x=data[decision]*10**6, linewidth=1, color='r')
        plt.show()
        # DEBUG
        """
        return decision


    def run(self):
        prefix = self.prefix

        while (len(prefix) < self.length):
            measurements = self.make_measurements(prefix)
            measurements = self.sanitize_data(measurements)
            next_char = self.get_best_char(measurements)
            prefix = prefix + next_char
            print(prefix)
