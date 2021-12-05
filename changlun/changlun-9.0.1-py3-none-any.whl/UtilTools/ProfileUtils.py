
def runProfile(functionName):
    import cProfile
    cProfile.run(functionName + "()", "result")
    import pstats
    p = pstats.Stats("result")
    p.strip_dirs().sort_stats("cumulative").print_stats()