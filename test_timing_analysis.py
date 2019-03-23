import timing_analysis


def example_queryf(candidate):
    if "asd" in candidate:
        return 0.3
    if "niklas" in candidate:
        return 0.04
    if "nik" in candidate:
        return 0.1
    return .4


timea = timing_analysis.Timea(example_queryf, 21)

#meas = timea.make_measurements()
#print(list(meas))

timea.run()
