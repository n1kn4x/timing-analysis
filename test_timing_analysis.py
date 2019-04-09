import password_timing_analysis
import time
from time import sleep

def str_compare1(str1, str2):
    counter = 0
    while counter < len(str1) and counter < len(str2):
        if str1[counter] == str2[counter]:
            counter = counter + 1
        else:
            return counter

def str_compare2(str1, str2):
    if (len(str1) != len(str2)):
        return False
    for i in range(len(str1)):
        if (str1[i] != str2[i]):
            return False
    return True

def str_compare3(str1, str2):
    return str1 == str2

PW = "SuPerDupeRStrongPassw0rd"
def example_queryf(candidate):
    t1 = time.process_time()
    str_compare3(candidate, PW)
    t2 = time.process_time()
    return (t2 - t1) * 10**9

timea = password_timing_analysis.Timea(example_queryf, len(PW), decision_metric="gmm", decision_rule="max", queries=600)

#meas = timea.make_measurements()
#print(list(meas))

timea.run()
