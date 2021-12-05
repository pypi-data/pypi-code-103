# https://wiki.samba.org/index.php/Configure_DHCP_to_update_DNS_records_with_BIND9
from datetime import datetime, timedelta
import subprocess
import logging
import locale
import re
import os

DEFAULT_CCACHE_MINTIME = 300    # seconds

logger = logging.getLogger(__name__)

class KerberosError(Exception):
    pass

def request_new_tgt(principal, keytab, cache):
    logger.info("Requesting new ticket")
    args = [
        'kinit',

        # request non-forwardable tickets
        '-F',

        # request a ticket using a key in this local keytab file
        '-k', '-t', str(keytab),

        # store tickets in this cache
        '-c', str(cache),

        principal,
    ]
    logger.debug("Running `{}`".format(' '.join(args)))

    try:
        cp = subprocess.run(args, check=True)
    except subprocess.CalledProcessError:
        raise KerberosError("Failed to request new Kerberos ticket")


def parse_time(s):
    # Python does not set LC_TIME. Ensure this assumption is true.
    # See https://bugs.python.org/issue29457
    assert locale.setlocale(locale.LC_TIME) == 'C'
    assert locale.getlocale(locale.LC_TIME) == (None, None)

    # MIT
    # See krb5_timestamp_to_sfstring()
    # https://github.com/krb5/krb5/blob/krb5-1.17-final/src/lib/krb5/krb/str_conv.c#L217-L254
    sftime_format_table = [
        "%c",                   # Default locale-dependent date and time
        "%d %b %Y %T",          # dd mon yyyy hh:mm:ss
        "%x %X",                # locale-dependent short format
        "%x %T",                # locale-dependent date + hh:mm:ss
        "%x %R",                # locale-dependent date + hh:mm
        "%Y-%m-%dT%H:%M:%S",    # ISO 8601 date + time
        "%Y-%m-%dT%H:%M",       # ISO 8601 date + hh:mm
        "%Y%m%d%H%M%S",         # ISO 8601 date + time, basic
        "%Y%m%d%H%M"            # ISO 8601 date + hh:mm, basic
    ]
    for fmt in sftime_format_table:
        try:
            return datetime.strptime(s, '%x %X')
        except ValueError:
            pass

    # Heimdal
    # See printable_time_internal() which always outputs
    # "Mon dd hh:mm:ss yyyy" e.g. "Dec 30 12:05:58 2019"
    # https://github.com/heimdal/heimdal/blob/heimdal-7.7.0/kuser/klist.c#L40-L58
    try:
        return datetime.strptime(s, '%b %d %H:%M:%S %Y')
    except ValueError:
        pass

    raise ValueError("Unknown time format: {}".format(s))


class CredCache:
    def __init__(self):
        self.tickets = {}    # keyed by principal

class Ticket:
    def __init__(self, issued, expires=None):
        self.issued = issued
        self.expires = expires

    @property
    def remaining(self):
        zero = timedelta(0)
        if self.expires is None:
            return zero
        remain = self.expires - datetime.now()
        if remain < zero:
            return zero
        return remain


def load_cred_cache(ccache):
    """Load a krb5 credential cache
    """
    args = [
        'klist',
        '-c', str(ccache),
    ]
    env = os.environ.copy()
    env['LANG'] = 'C'
    logger.debug("Running `{}`".format(' '.join(args)))
    cp = subprocess.run(args, check=True,
                        env=env,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        universal_newlines=True)
    return parse_klist_output(cp.stdout)


def parse_klist_output(output):
    result = CredCache()

    meta_pat = re.compile(r'([\w\s]+): (.*)')

    def handle_meta(line):
        line = line.strip()
        if not line:
            # This is the blank line
            return handle_header

        # Metadata line?
        m = meta_pat.match(line)
        if not m:
            raise Exception("Unexpected line: " + line)
        k, v = m.groups()
        k = {
            'Credentials cache':    'cache',        # Heimdal
            'Ticket cache':         'cache',        # MIT
            'Principal':            'principal',    # Heimdal
            'Default principal':    'principal',    # MIT
        }.get(k)
        if not k:
            raise Exception("Unexpected line: " + line)
        setattr(result, k, v)
        return handle_meta

    def handle_header(line):
        parts = [x.strip() for x in line.split('  ') if x]
        if not parts[0] in ('Issued', 'Valid starting'):
            raise Exception("Unexpected line: " + line)
        if not parts[1] == 'Expires':
            raise Exception("Unexpected line: " + line)
        if not parts[2] in ('Principal', 'Service principal'):
            raise Exception("Unexpected line: " + line)
        return handle_ticket

    def handle_ticket(line):
        # Ticket/credential line?

        # Ignore extra lines like "renew until" and "Ticket server"
        if line.startswith('\t'):
            return handle_ticket

        parts = line.split('  ')

        issued = parse_time(parts[0])

        if 'expire' in parts[1].lower():
            expires = None
        else:
            expires = parse_time(parts[1])

        principal = parts[2]

        result.tickets[principal] = Ticket(issued, expires)

        return handle_ticket

    state = handle_meta
    for line in output.splitlines():
        state = state(line)
        if not state:
            break

    return result


def check_cred_cache(cache, realm, mintime=None):
    """Checks that a credential cache is valid

    This function ensures that the given credential cache has a ticket-granting
    ticket (TGT) valid for a sufficient amount of time.

    Parameters:
    cache   Kerberos credential cache to check
    realm   Kerberos realm to check for TGT
    mintime Minimum amount of time (in seconds) for which TGT must be valid
    """
    if mintime is None:
        mintime = DEFAULT_CCACHE_MINTIME
    mintime = timedelta(seconds=mintime)

    try:
        cc = load_cred_cache(cache)
    except subprocess.CalledProcessError:
        return False

    spn = make_principal('krbtgt', realm, realm.upper())
    try:
        ticket = cc.tickets[spn]
    except KeyError:
        logger.info("{} not found in {}".format(spn, cache))
        return False

    if ticket.remaining < mintime:
        # Expired
        logger.info("{} expired at {}".format(spn, ticket.expires))
        return False
    else:
        logger.info("{} expires in {} at {}".format(spn, ticket.remaining, ticket.expires))
        return True


def ensure_valid_tgt(username, realm, keytab, cache, mintime=None):
    principal = make_principal(username, realm)
    logger.info("Using kerberos principal {}".format(principal))

    if not check_cred_cache(cache, realm, mintime=mintime):
        request_new_tgt(principal, keytab, cache)


def make_principal(primary, realm, instance=None):
    result = primary
    if instance:
        result += '/' + instance
    result += '@' + realm.upper()
    return result


def setup_kerberos_environ(username, realm, keytab, cache):
    ensure_valid_tgt(
            username = username,
            realm = realm,
            keytab = keytab,
            cache = cache,
        )
    os.environ['KRB5CCNAME'] = str(cache)


if __name__ == '__main__':
    def parse_args():
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument('username')
        ap.add_argument('realm', type=str.upper)
        ap.add_argument('-k', dest='keytab', required=True)
        ap.add_argument('-c', dest='cache', required=True)
        ap.add_argument('-m', dest='mintime', type=int)
        return ap.parse_args()

    def main():
        logging.basicConfig(level=logging.DEBUG)

        args = parse_args()

        ensure_valid_tgt(
                username = args.username,
                realm = args.realm,
                keytab = args.keytab,
                cache = args.cache,
                mintime = args.mintime,
            )

    main()
