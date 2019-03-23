"""
    This utility file is meant to implement timing attacks on a generic
    level.
    A timing attack consist of a user-implemented query function that
    takes a candidate (f.e. password) and returns a timing (numeric).
    Additionally the user has to provide an ITERABLE and a LENGTH from
    which a candidate is generated.

    We attempt to use the following mechanism:
        - Variable composition: Declare how many items are used to compose
            a new timing query
            (i.e. 2 char password composition: AAAA..., ABAA..., ACAA...,
            BAAA..., BBAA...,)
            A drawback is that the amount of queries is increased.
        - Decision fallback: If a poor item has been chosen in the
            iteration before, we can fall back to the
            second best decision. Poorly chosen items are identified by
            measuring if the timings of all queries
            in the current iteration have significantly changed compared
            to the iteration before.
        - Different analysis methods: To analyze the timings and make a
            decision about the next iteration,
            we can select different methods, for example Mean, Median,
            Variance, ith Percentile
        - Parallel execution: Have the possibility to perform timing
            measurements of candidates in parallel.
        - Plotting: Optionally plot the timing analysis results.

    Terminology of this code explained by example (term : example):
        - candidate : password
        - item : character in password
        - item_collection : all possible characters in a pw (iterable)
        - comp : composition of items
        - query : try password and measure time (user implemented)

"""
import string
import itertools
import numpy as np
from multiprocessing.dummy import Pool as ThreadPool

def example_queryf(candidate):
    return 0.35

class Timea:

    # Default configuration
    def __init__(self,
                query_func,
                length,
                num_queries = 1,
                item_collection = string.ascii_letters + string.digits,
                comp_size = 3,
                comp_func = lambda items: ''.join(items),
                num_threads = 4
                ):

        self.query_func = query_func
        self.length = length
        self.num_queries = num_queries
        self.item_collection = item_collection
        self.comp_size = comp_size
        self.comp_func = comp_func
        self.num_threads = num_threads

        self.item_combis = self.build_item_combinations(item_collection,
                                                        comp_size,
                                                        comp_func)
        self.thread_pool = ThreadPool(num_threads)

    def build_item_combinations(self,
                                item_collection,
                                comp_size,
                                comp_func):
        assert(comp_size > 0)
        item_combinations = itertools.product(item_collection,
                                              repeat=comp_size)
        return list(map(self.comp_func, item_combinations))

    def compose_candidate(self,
                          item_combi,
                          prefix=""):
        fill_len = self.length - len(prefix) - self.comp_size
        assert(fill_len >= 0)
        fill_comp = self.item_collection[0] * fill_len
        candidate = self.comp_func([prefix, self.comp_func([item_combi, fill_comp])])
        assert(len(candidate) == self.length)
        print(candidate)
        return candidate

    def make_measurements(self, prefix=""):
        pool = self.thread_pool
        make_candidate = lambda x: self.compose_candidate(x, prefix)
        all_candidates = pool.map(make_candidate, self.item_combis)
        all_timings    = pool.map(self.query_func, all_candidates)
        return all_timings


    # TODO next: pandas + metrics -> decision tree



    def make_decision(self, prefix=""):
        all_timings = self.make_measurements(prefix)
        idx = all_timings.index(min(all_timings))
        assert(len(all_timings) == len(self.item_combis))
        return self.item_combis[idx]

    def run(self, prefix=""):
        while (len(prefix) < self.length):
            decision = self.make_decision(prefix)
            prefix = self.comp_func([prefix, decision])
        print(prefix)




