from ...open_state import OpenState


def is_open(session):
    return session.open_state is OpenState.Open


def is_closed(session):
    return session.open_state is OpenState.Closed
