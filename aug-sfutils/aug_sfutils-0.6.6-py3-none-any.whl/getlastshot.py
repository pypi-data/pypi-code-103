import sys, logging

from aug_sfutils import libddc
try:
    import journal
except:
    pass

logger = logging.getLogger('aug_sfutils.getlastshot')
date_fmt = '%Y-%m-%d'
logger.setLevel(logging.INFO)


def parse_url(url, blen=100):
    """
    Read URL content
    """

    try:
        import urllib3
        url_lib = 'urllib3'
    except:
        try:
            import urllib2
            url_lib = 'urllib2'
        except:
            try:
                import urllib
                url_lib = 'urllib'
            except:
                logger.error('No urllib(2, 3) found')
                return None

    url_not_found = 'URLs %s not found' %url
    if url_lib == 'urllib3':
        http = urllib3.PoolManager()
        try:
            tmp = http.request('GET', url)
        except:
            logger.error(url_not_found)
            return None
        bshot = tmp.data[:blen]
    elif url_lib == 'urllib2':
        try:
            bshot = urllib2.urlopen(url).read(blen)
        except:
            logger.error(url_not_found)
            return None
    elif url_lib == 'urllib':
        try:
            bshot = request.urlopen(url).read()
        except:
            logger.error(url_not_found)
            return None

    return bshot


def getlastshot():
    """
    Gets last shot number from the AUG webpage(s)
    """

    nshot = libddc.previousshot('JOU', 99999)
    if nshot is not None:
        return nshot

    if 'journal' in sys.modules:
       nshot = journal.getLastShot()
       if nshot is not None:
           return nshot

    url1 = 'http://ssr-mir.aug.ipp.mpg.de:9090/Diag/ShotNumber.dta'
    nshot = parse_url(url1, blen=5)

    if nshot is None:
        logger.error('Cannot convert None to integer')
    else:
        nshot = int(nshot)
 
    return nshot
