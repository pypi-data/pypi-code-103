from datetime import timedelta

def build_time_vector(d1,options, to_timedelta=False):
    """Build time vector assuming constant timesteps.
    """
    n_steps = int(options['horizon'] / options['resolution'])
    time = [options['resolution']*t for t in range(n_steps+1)]
    if to_timedelta:
        time = [d1+timedelta(hours=x) for x in time]
    return time
