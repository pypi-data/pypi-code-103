from collections import defaultdict
from datetime import timedelta
from io import StringIO
import logging

from .adman import DISABLED_USER_FILTER
from .email import try_send_email
from .ldapfilter import Filter
from .util import count, datetime_to_FILETIME, utcnow

logger = logging.getLogger(__name__)

DATE_FORMAT = '%Y-%m-%d %H:%M UTC'

def lastlogon_before_filter(date):
    return Filter('lastLogonTimestamp<={}'.format(datetime_to_FILETIME(date)))


class StaleResult:
    def __init__(self, timestamp, user):
        self.timestamp = timestamp
        self.user = user        # user or computer

        # Can be:
        #   None (not cofigured to disable)
        #   True (disabled)
        #   Exception (failed to disable)
        self.disabled_status = None

    @property
    def name(self):
        return self.user.sAMAccountName

    @property
    def lastlogon(self):
        return self.user.lastLogonTimestamp.strftime(DATE_FORMAT)

    @property
    def ago(self):
        return self.timestamp - self.user.lastLogonTimestamp


class FindStaleProcessor:
    def __init__(self, onchange=None):
        self.now = utcnow()
        self.results = defaultdict(dict)    # {what: {container: (cfg, [stale])}}
        self.onchange = onchange

    def find(self, container, scope, getobj_meth, dt):
        # Identify the point in the past, before which the user must have logged on
        filt = lastlogon_before_filter(self.now - dt)
        filt &= ~DISABLED_USER_FILTER

        attrs = ('sAMAccountName', 'lastLogonTimestamp', 'userAccountControl')
        users = getobj_meth(rdn=container, scope=scope, filt=filt, attrs=attrs)

        results = []
        for user in users:
            sr = StaleResult(timestamp=self.now, user=user)
            assert sr.ago >= dt

            results.append(sr)

        return results


    def process(self, what, ucconfig, getobj_meth):
        total = 0
        for container, cfg in ucconfig.iterate_containers():
            stale = self.find(container=container, scope=cfg.scope,
                         getobj_meth=getobj_meth, dt=cfg.older_than.dt)
            if not stale:
                continue

            self.results[what][container] = (cfg, stale)
            total += len(stale)

            for sr in stale:
                if cfg.disable:
                    try:
                        sr.user.disabled = True
                        sr.user.commit()
                    # TODO: Tighten this up to include ldap.error and anything from .ldapobj
                    except Exception as e:
                        logger.exception(e)
                        sr.disabled_status = e
                    else:
                        sr.disabled_status = True

                        message = "Disabled stale account {}".format(sr.user.dn)
                        logger.info(message)
                        if self.onchange:
                            self.onchange(message=message)

        return total

    @property
    def disabled(self):
        for sr in self.flat_results():
            if sr.disabled_status is True:
                yield sr

    @property
    def disable_errors(self):
        for sr in self.flat_results():
            if isinstance(sr.disabled_status, Exception):
                yield sr, sr.disabled_status

    @property
    def total_stale(self):
        return count(self.flat_results())

    def flat_results(self):
        for what, containers in self.results.items():
            for container, (cfg, stale) in containers.items():
                for sr in stale:
                    yield sr


def _build_html_report(fs):
    buf = StringIO()

    def _pr(*args, **kwargs):
        kwargs['file'] = buf
        print(*args, **kwargs)

    css = """
        body {
            font-family: sans-serif;
        }

        thead, tfoot {
            background-color: #3f87a6;
            color: #fff;
        }

        tbody {
            background-color: #e4f0f5;
        }

        p {
            margin-top: 4px;
        }

        h1, h2 {
            margin-bottom: 4px;
        }

        table {
            border-collapse: collapse;
            border: 2px solid rgb(200, 200, 200);
            width: 90%;
        }

        td, th {
            border: 1px solid rgb(190, 190, 190);
            padding: 5px 10px;
        }
        """

    _pr("<html>")
    _pr("<head>")
    _pr("  <style>")
    _pr(css)
    _pr("  </style>")
    _pr("</head>")

    _pr("<body>")
    _pr("<h1>ADMan stale account report</h1>")
    _pr("<p>Generated {}</p>".format(fs.now.strftime(DATE_FORMAT)))

    _pr("<hr/>")

    for what, containers in fs.results.items():
        _pr("<h2>Stale {} accounts:</h2>".format(what))
        _pr("<table>")


        total = 0
        for container, (cfg, stale) in containers.items():
            head = ""
            if container:
                head = "<strong>{}</strong> <small>({})</small> ".format(container, cfg.scope)
            head += "<small>(&gt;{} ago)</small>".format(cfg.older_than)
            _pr("  <thead><th colspan=3>{}</th></thead>".format(head))

            total += len(stale)
            for sr in stale:
                action = ""
                if sr.disabled_status:
                    action = 'Disabled' if sr.disabled_status is True else 'Failed to disable'

                _pr("  <tr>")
                _pr("    <td><strong><code>{}</code></strong></td>".format(sr.name))
                _pr("    <td>{timestamp}&nbsp;&nbsp;&nbsp;{ago}</td>".format(
                        timestamp = sr.lastlogon,
                        ago = '({} days ago)'.format(sr.ago.days),
                        ))
                _pr("    <td>{}</td>".format(action))
                _pr("  </tr>")

        _pr("</table>")
        if total:
            _pr("<p>(Total: {})</p>".format(total))


    # Add disable results
    if any(fs.disabled) or any(fs.disable_errors):
        _pr("<hr/>")

    if any(fs.disabled):
        disabled = list(fs.disabled)
        _pr("<h2>Disabled:</h2>")
        _pr("<p>The following {} accounts have been <em>disabled</em>:</p>".format(len(disabled)))
        _pr("<ul>")
        for sr in disabled:
            _pr("<li><code>{}</code></li>".format(sr.user.dn))
        _pr("</ul>")

    if any(fs.disable_errors):
        _pr("<h2>Errors while disabling:</h2>")
        _pr("<p>The following ADMan errors were encountered while trying to disable accounts:</p>")

        import traceback
        _pr("<ul>")
        for sr, err in fs.disable_errors:
            _pr("<li><code>{}</code>".format(sr.user.dn))
            lines = traceback.format_exception(type(err), err, err.__traceback__)
            _pr("<pre>")
            _pr("".join("    " + line for line in lines))
            _pr("</pre></li>")
        _pr("</ul>")


    _pr("</body>")
    _pr("</html>")

    return buf.getvalue()


def _build_plaintext_report(fs):
    buf = StringIO()

    def _pr(*args, **kwargs):
        kwargs['file'] = buf
        print(*args, **kwargs)

    _pr("ADMan stale account report (generated {})".format(fs.now.strftime(DATE_FORMAT)))
    _pr("-"*80)

    for what, containers in fs.results.items():
        _pr("\nStale {} accounts:".format(what))
        total = 0
        for container, (cfg, stale) in containers.items():
            head = ""
            if container:
                head = "{} ({}) ".format(container, cfg.scope)
            head += "(>{} ago)".format(cfg.older_than)
            _pr("  {}".format(head))

            total += len(stale)
            for sr in stale:
                line = "    {name:<24} {timestamp}  {ago:<15}".format(
                        name = sr.name,
                        timestamp = sr.lastlogon,
                        ago = '({} days ago)'.format(sr.ago.days),
                    )
                if sr.disabled_status:
                    st = 'DISABLED' if sr.disabled_status is True else 'failed to disable'
                    line += "  [{}]".format(st)
                _pr(line)
        if total:
            _pr("(Total: {})".format(total))


    # Add disable results
    if any(fs.disabled) or any(fs.disable_errors):
        _pr("\n" + "="*72)

    if any(fs.disabled):
        disabled = list(fs.disabled)
        _pr("\nDisabled ({}):".format(len(disabled)))
        for sr in disabled:
            _pr("  {}".format(sr.user.dn))

    if any(fs.disable_errors):
        _pr("\nErrors while disabling:")
        import traceback
        for sr, err in fs.disable_errors:
            _pr("  {}:".format(sr.user.dn))
            lines = traceback.format_exception(type(err), err, err.__traceback__)
            _pr("".join("    " + line for line in lines))

    return buf.getvalue()


def find_and_process_stale_accounts(ad, config, onchange=None):
    sacfg = config.stale_accounts

    # Find and disable (if configured)
    fs = FindStaleProcessor(onchange=onchange)

    fs.process('user', sacfg.users, ad.get_users)
    fs.process('computer', sacfg.computers, ad.get_computers)

    if not any(fs.flat_results()):
        return

    plaintext = _build_plaintext_report(fs)

    if sacfg.email_to:
        subject = 'ADMan stale account report: {} stale'.format(fs.total_stale)
        ndis = count(fs.disabled)
        if ndis:
            subject += ', {} disabled'.format(ndis)
        ndiserr = count(fs.disable_errors)
        if ndiserr:
            subject += ', {} ERRORS'.format(ndiserr)

        try_send_email(config,
            mailto = sacfg.email_to,
            subject = subject,
            body = plaintext,
            html = _build_html_report(fs),
            )
    else:
        print(plaintext)
