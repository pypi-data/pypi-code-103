# Resources:
# https://ldapwiki.com/wiki/AD%20Determining%20Password%20Expiration
# https://docs.microsoft.com/en-us/windows/win32/adschema/a-useraccountcontrol
# https://github.com/sttts/ldap-notify (eDirectory, not Active Directory)

from datetime import datetime, timedelta, timezone
import json
import logging
from string import Template

from .email import try_send_email
from .ldapfilter import Filter, BitAndFilter, UserAccountControl
from .util import single, utcnow
from .paths import default_datadir

logger = logging.getLogger(__name__)


def check_pw_expiry(ad, config):
    now = utcnow()
    nlog = UserNotifyLog.load()

    # Exclude users whose password:
    # - Can't expire
    # - Must be set at next login
    filt = ~BitAndFilter('userAccountControl', UserAccountControl.DONT_EXPIRE_PASSWD) \
            & ~Filter('pwdLastSet=0')

    for user in ad.get_users(filt=filt):
        last_notify = nlog.get(user.dn)
        pw_expires_in = user.PasswordExpiryTime - now

        if _should_notify(now, user.PasswordExpiryTime, config, last_notify):
            logger.info("Notifying user {} of password expiry in {} (last notified {})"
                    .format(user.dn, pw_expires_in, last_notify))
            _do_notify(now, user, config)

            nlog.set(user.dn, now)
            nlog.save()


def _do_notify(now, user, config):
    if not user.mail:
        logger.warning("User {} mail attribute not set".format(user.dn))
        return

    expires_in = user.PasswordExpiryTime - now

    tmpl = Template(config.pwexp.template)
    body = tmpl.substitute(
        cn = user.cn,
        upn = user.userPrincipalName,
        expire_days = "{} {}".format(expires_in.days,
            "day" if expires_in.days==1 else "days"),
        expire_time = user.PasswordExpiryTime.strftime('%Y-%m-%d %H:%M:%S'),
        # TODO: Remind in how many days?
    )

    try_send_email(
            config = config,
            mailto = user.mail,
            subject = 'Password expiring',
            body = body,
        )


def _should_notify(now, expiry, config, last_notify):
    # Determine if a user should be notified, based on:
    # - Their password expiry time
    # - The configured notification points
    # - The last time they were notified
    for d in config.pwexp.days:
        notify_at = expiry - timedelta(days=d)
        if now < notify_at:
            # Not time yet
            continue
        if  last_notify > notify_at:
            # (should have) already sent this notification
            continue
        return True

    return False



class UserNotifyLog:
    """Records the last time a given user was notified of password expiration

    TODO: For large numbers of users, it may be better to use e.g. sqlite
    """
    def __init__(self, path, data):
        self.path = path
        self.data = data

    @classmethod
    def load(cls):
        path = default_datadir() / "pwnotify.json"
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        return cls(path, data)

    def save(self):
        with open(self.path, 'w') as f:
            return json.dump(self.data, f, indent=4, sort_keys=True)

    def get(self, username):
        """Gets the last notified time for a user"""
        ts = self.data.get(username, 0)
        return datetime.utcfromtimestamp(ts).replace(tzinfo=timezone.utc)

    def set(self, username, dt):
        """Saves the last notified time for a user"""
        v = dt.timestamp()
        self.data[username] = v
