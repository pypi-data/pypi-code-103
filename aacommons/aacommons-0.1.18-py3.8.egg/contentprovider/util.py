from logging import getLogger

from munch import DefaultMunch

import jstyleson
from yaml import load, FullLoader
from yaml.parser import ParserError


log = getLogger(__name__)


def convertToDict(s: str):
    ''' Attempt to decode a string and returns a dictionary or a list.
    Will attempt to decode the string as JSON or YAML

    Parameter
    ---------
    s : str

    Returns
    -------
    dict or list :
        A dictionary if able to convert content as dict or list. None if unsuccessful
    '''

    try:
        d = jstyleson.loads(s)
        log.debug("Found JSON")
        return DefaultMunch(None).fromDict(d)
    except ValueError as e:
        try:
            log.debug(f"Not JSON format ({e})")
            d = load(s, Loader=FullLoader)
            log.debug("Found YAML")
            return DefaultMunch(None).fromDict(d)
        except ParserError:
            log.debug("Did not find JSON or YAML str")
            return None
