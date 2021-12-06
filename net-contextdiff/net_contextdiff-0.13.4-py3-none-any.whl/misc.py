# misc
#
# Copyright (C) Robert Franklin <rcf34@cam.ac.uk>



def get_all_subclasses(c):
    """Return all subclasses of the specified class.

    The returned list will be in depth-first then name order (e.g.
    A, then X(A), then Y(X) then Z(A) then B).
    """

    l = []
    for s in sorted(c.__subclasses__(), key=lambda i: i.__name__):
        l.append(s)
        l.extend(get_all_subclasses(s))
    return l
