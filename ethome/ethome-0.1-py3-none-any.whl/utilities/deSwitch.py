import numpy as np

    """Legacy functions for when suit needed de-switching to deal with drift
       problems.
    """
def deSwitch(data, units="rad", tresh=0.9):

    _, D = data.shape
    out = data
    if units == "deg":
        tresh *= 180
        add = 180
    elif units == "rad":
        tresh *= np.pi
        add = np.pi
    else:
        raise ValueError("Unknown units type")

    for k in range(D):
        while 1:
            t = np.argwhere(abs(np.diff(out[:, k])) > tresh)
            if t.size == 0:
                break
            off = np.sign(out[t + 1, k] - out[t, k])
            if units == "deg":
                out[t + 1:, k] = out[t + 1:, k] - off * 180
            elif units == "rad":
                out[t + 1:, k] = out[t + 1:, k] - off * np.pi

    return out
