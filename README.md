# timing-analysis

An API to make sophistacted timing analysis using Gaussian Mixture Models, among others.
Blog entry: https://parzelsec.de/static/timing-attacks-with-machine-learning/index.html

Example usage script:
```
import password_timing_analysis
import time

PW = "SuPerDupeRStrongPassw0rd"

# Dummy string compare function
def str_compare(str1, str2):
    return str1 == str2

# This query function must be implemented by the user and provided to Timea constructor.
def example_queryf(candidate):
    t1 = time.process_time()
    str_compare(candidate, PW)
    t2 = time.process_time()
    return (t2 - t1) * 10**9

# Create Timea object - provide timing query function and length of password (when to stop).
timea = password_timing_analysis.Timea(example_queryf, len(PW), decision_metric="gmm", decision_rule="max", queries=500)

timea.run()
```

- Metrics that can be used: "gmm", "mean", "median", "variance" or "percentile"
- Decision rules based on metric: "max", "min"

For more options, just look in the code - it's not much :P
