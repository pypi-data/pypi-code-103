import numpy as np
from scipy.linalg import expm, solve


def ss_response(gen):
    """Calculate state space response for a given Component.

    Positional arguments:
    gen - (Component) Component for which the response is to be
        calculated.
    """
    # Get timestep.
    t_peak = (gen['size_kw'] - gen['lower_bound']) / gen['ramp_rate'] * 3600
    if t_peak > 4 * 60:
        dt = 60
    elif t_peak > 3.6e4:
        dt = 3600
    else:
        dt = 1
    # Convert continuous state-space to discrete time state-space.
    a = expm(np.array(gen['state_space']['a']) * dt)
    b = (
        solve(np.array(gen['state_space']['a']), (a - np.eye(2)))
        @ np.array(gen['state_space']['b'])
    ).reshape((-1, 1))
    c = np.array(gen['state_space']['c']).reshape((1, -1))
    d = np.array(gen['state_space']['d'])

    time = 5 * t_peak
    ramp_rate = False
    count = 0
    while isinstance(ramp_rate, bool):
        n_s = int(np.round(time / dt)) + 1
        u = gen['size_kw'] * np.ones(n_s)
        x_0 = np.zeros(c.shape[::-1])
        x_0[np.nonzero(c[0, :])] = gen['lower_bound']
        y, t = ss_sim(a, b, c, d, x_0, u, dt)
        if (
            np.any((y[:, 0] - y[0, 0]) > (0.95 * (u[0] - y[0, 0])))
            and not any(np.abs((y[:-9:-2, 0] - y[-1, 0]) / y[-1, 0]) > 1e-3)
        ):
            n_r = np.min(np.nonzero((y[:, 0] - y[0, 0]) > (0.95 * (u[0] - y[0, 0]))))
            # Rise time (hours).
            t_rise = (
                np.interp(
                    0.95 * (u[0] - y[0, 0]),
                    np.array([y[n_r - 1, 0], y[n_r, 0]]) - y[0, 0],
                    np.array([t[n_r - 1], t[n_r]]),
                )
                / 3600
            )
            ramp_rate = (gen['size_kw'] - gen['lower_bound']) * 0.95 / t_rise

        else:
            time *= 5
        count += 1
        if count > 10:
            ramp_rate = gen['ramp_rate']
    return ramp_rate


def ss_sim(a, b, c, d, x_0, u, dt):
    n = len(u)
    time = np.linspace(0, n * dt, n + 1)
    x = np.zeros((len(x_0), n + 1))
    x[:, 0] = x_0.T
    y = np.zeros((n + 1, len(c)))
    y[0] = c @ x_0
    for t in range(n):
        x[:, t + 1 : t + 2] = a @ x[:, t : t + 1] + b * u[t]
        y[t + 1] = c @ x[:, t + 1 : t + 2] + d * u[t]
    return y, time
