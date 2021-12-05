import argparse
from datetime import datetime
import logging
import sys
from functools import wraps

from .adman import ADManager
from .assign import PosixIdAssigner, AssignmentError, UpnAssigner
from .config import Config, ConfigError
from .paths import default_confpath
from .state import DomainState
from .staleacct import find_and_process_stale_accounts
from .kerberos import setup_kerberos_environ, KerberosError
from .version import __version__


logger = logging.getLogger(__name__)


class AppError(Exception):
    pass

class NotConfiguredError(AppError):
    def __init__(self, cfgsec):
        super().__init__("Section not configured: " + cfgsec)


def confirm(question="Are you sure?"):
    while True:
        try:
            reply = input(question + " (yes/no): ").lower().strip()
        except (EOFError, KeyboardInterrupt):
            return False

        if reply[:1] == 'y':
            return True
        if reply[:1] == 'n':
            return False


def get_state(ad):
    s = DomainState.get(ad)
    logger.debug("DomainState: {}".format(s._data))
    if not s.complete:
        raise AppError("Domain ID number state not initialized. (Try 'state init')")
    return s


class ChangeHandler:
    def __init__(self, logfile):
        self.logfile = logfile

    def __call__(self, message):
        self.logfile.write("{:%Y-%m-%d %H:%M:%S} {}\n"
                           .format(datetime.now(), message))


def get_change_handler(config):
    path = config.changelog_path
    f = open(path, 'a') if path else sys.stderr
    return ChangeHandler(f)


def get_posix_assigner(args, ad):
    ia = args.config.id_assign
    if ia is None:
        raise NotConfiguredError("id_assign")

    return PosixIdAssigner(
            ad = ad,
            state = get_state(ad),
            uid_range = ia.uid_range,
            gid_range = ia.gid_range,
            replace_invalid = args.force,
            onchange = get_change_handler(args.config),
            )


def posix_assign(func):
    @wraps(func)
    @connect_ad
    def wrapper(args, ad):
        pa = get_posix_assigner(args, ad)
        return func(args, ad, pa)
    return wrapper


def connect_ad(func):
    @wraps(func)
    def wrapper(args):

        domain = args.config.domain
        lc = args.config.ldap_auth

        if lc.mode != 'gssapi':
            raise NotImplementedError("Only gssapi mode is supported")

        # TODO: Does this belong in ADManager?
        if lc.username:
            setup_kerberos_environ(
                    username = lc.username,
                    realm = domain,
                    keytab = lc.keytab,
                    cache = lc.cache,
                )

        ad = ADManager.connect(domain)
        return func(args, ad)
    return wrapper


@connect_ad
def cmd_allmaint(args, ad):
    tasks = [
        cmd_assignids,
        cmd_user_setupns,
        cmd_user_checkexpire,
        cmd_user_mkdirs,
    ]

    for cmd in tasks:
        try:
            cmd.__wrapped__(args, ad)
        except NotConfiguredError as e:
            logger.info(str(e))



@connect_ad
def cmd_assignids(args, ad):
    pa = get_posix_assigner(args, ad)

    logger.info("Assigning POSIX IDs")
    cmd_group_assign.__wrapped__(args, ad, pa)
    cmd_user_assign.__wrapped__(args, ad, pa)
    if args.config.id_assign.computers:
        cmd_computer_assign.__wrapped__(args, ad, pa)
    else:
        logger.info("Not assigning computer IDs")


@posix_assign
def cmd_clearids(args, ad, pa):
    if not args.force:
        print("This command will clear *all* uidNumber/gidNumber attributes!")
        if not confirm():
            return

    pa.clear_all_ids()


@connect_ad
def cmd_exec(args, ad):
    if not args.args:
        raise AppError("No command given")
    import subprocess
    rc = subprocess.call(args.args)
    sys.exit(rc)


@connect_ad
def cmd_findstale(args, ad):
    sc = args.config.stale_accounts
    if sc is None:
        raise NotConfiguredError("stale_accounts")

    find_and_process_stale_accounts(ad, args.config,
            onchange = get_change_handler(args.config),
        )


@posix_assign
def cmd_computer_assign(args, ad, pa):
    ia = args.config.id_assign
    for container, cfg in ia.only.iterate_containers():
        pa.computer_assign(container=container, scope=cfg.scope)


@connect_ad
def cmd_computer_list(args, ad):
    common_list(ad.get_computers(), args.verbose)


@posix_assign
def cmd_group_assign(args, ad, pa):
    ia = args.config.id_assign
    for container, cfg in ia.only.iterate_containers():
        pa.assign_group_gidNumbers(
                container = container,
                scope = cfg.scope,
                include_computer_groups = ia.computers,
            )


@connect_ad
def cmd_group_list(args, ad):
    common_list(ad.get_groups(), args.verbose)


@posix_assign
def cmd_user_assign(args, ad, pa):
    ia = args.config.id_assign
    for container, cfg in ia.only.iterate_containers():
        pa.user_assign(container=container, scope=cfg.scope)


@connect_ad
def cmd_user_checkexpire(args, ad):
    cfg = args.config
    if not cfg.pwexp:
        raise NotConfiguredError("password_expiry_notification")

    # Lazy import to avoid unnecessary imports
    from .pwexpire import check_pw_expiry

    check_pw_expiry(ad, cfg)


@connect_ad
def cmd_user_setupns(args, ad):
    if not args.config.upn_suffixes:
        raise NotConfiguredError("upn_suffixes")

    a = UpnAssigner(
        ad = ad,
        onchange = get_change_handler(args.config),
    )

    logger.info("Settings UPNs")
    for container, cfg in args.config.upn_suffixes.items():
        a.set_user_upn_suffixes(container, cfg.suffix, cfg.scope)


@connect_ad
def cmd_user_mkdirs(args, ad):
    if not args.config.userdirs:
        raise NotConfiguredError("userdirs")

    # Lazy import to avoid unnecessary smbc import
    from .userdir import UserdirCreator, TemplatedSecurityDescriptor

    creator = UserdirCreator(
        ad = ad,
        onchange = get_change_handler(args.config),
    )

    for ud in args.config.userdirs:
        tsd = TemplatedSecurityDescriptor(
                owner = ud.owner,
                group = ud.group,
                acl = ud.acl,
            )

        for container, cfg in ud.only.iterate_containers():
            creator.create_userdirs(
                basepath = ud.basepath,
                tsd = tsd,
                container = container,
                scope = cfg.scope,
                subdirs = [
                    (
                        sd.name,
                        TemplatedSecurityDescriptor(
                            owner = ud.owner,   # inherit
                            group = ud.group,   # inherit
                            acl = sd.acl,
                            )
                    )
                    for sd in ud.subdirs
                ],
            )


def common_list(things, verbose):
    for x in things:
        if verbose:
            print(x)
        else:
            print(x.cn)

@connect_ad
def cmd_user_list(args, ad):
    common_list(ad.get_users(), args.verbose)


@connect_ad
def cmd_state_list(args, ad):
    s = get_state(ad)
    print(s)


@connect_ad
def cmd_state_init(args, ad):
    ds = DomainState.get(ad)

    logger.info("Got DomainState ({}): {}".format(ds.dn, ds))

    def set_next_xid(objs, thing, ldap_attr, ds_attr, valid_range):
        # Try to find the max value within the valid range
        gen = (getattr(x, ldap_attr, None) for x in objs)
        try:
            maxval = max(x for x in gen if x in valid_range)
        except ValueError:
            useval = valid_range.start
            logger.info("No {} {} found in range {}-{}; using default {}".format(
                thing, ldap_attr, valid_range.start, valid_range.stop, useval))
        else:
            # The "correct" value (ignoring deletion of top ID's) is max + 1
            useval = maxval + 1
            logger.info("Maximum {} {}: {}; using {}".format(
                thing, ldap_attr, maxval, useval))


        # See if the DomainState already has this attribute set, and compare
        curval = getattr(ds, ds_attr)
        if curval == useval:
            logger.info("Domain state {} already correctly set to {}".format(
                ds_attr, useval))
            return
        elif curval is not None:
            # They don't match
            if args.behavior is None:
                raise AppError("Domain state {} already set to {}, doesn't match expected {}\n"
                               "Use --force or --ignore".format(
                                   ds_attr, curval, useval))
            elif args.behavior == "force":
                # set it anyway
                pass
            elif args.behavior == "ignore":
                return

        logger.info("Setting Domain state {} to {}".format(ds_attr, useval))
        setattr(ds, ds_attr, useval)

    ia = args.config.id_assign

    set_next_xid(ad.get_users(),  'user',  'uidNumber', 'next_uid', ia.uid_range),
    set_next_xid(ad.get_groups(), 'group', 'gidNumber', 'next_gid', ia.gid_range),

    ds.commit()
    print(ds)


def setup_logging(args):
    logging.basicConfig(level=args.loglevel)


def parse_args():
    # <top-level>
    ap = argparse.ArgumentParser()
    ap.add_argument('--version', action='version', version='adman ' + __version__)
    ap.add_argument('--loglevel', type=str.upper, default="warning",
            choices=("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"),
            help="Log level")
    ap.add_argument('-c', '--config', default=default_confpath(),
            help="Path to config file")
    ap.add_argument('-v', '--verbose', action='store_true',
            help="Show verbose output")

    sub = ap.add_subparsers(dest='command_name', metavar='COMMAND')
    sub.required = True     # https://stackoverflow.com/a/18283730/119527


    def add_assign_opts(parser):
        parser.add_argument('--force', action='store_true',
                help="Forcefully replace out-of-range uidNumber/gidNumber attributes")

    # allmaint
    p = sub.add_parser('allmaint',
            help="Perform all automated maintenance (assign IDs, UPNs)")
    p.set_defaults(func=cmd_allmaint)
    add_assign_opts(p)

    # assignids
    p = sub.add_parser('assignids',
            help="Assign all missing uidNumber / gidNumber attributes")
    p.set_defaults(func=cmd_assignids)
    add_assign_opts(p)

    # clearids
    p = sub.add_parser('clearids',
            help="Clear all uidNumber / gidNumber attributes")
    p.set_defaults(func=cmd_clearids)
    p.add_argument('--force', action='store_true',
            help="Forcefully clear uidNumber/gidNumber attributes")

    # exec
    p = sub.add_parser('exec',
            help="Execute a command in Kerberos context")
    p.set_defaults(func=cmd_exec)
    p.add_argument('args', nargs=argparse.REMAINDER,
            help="Command/args to exectue")

    # findstale
    p = sub.add_parser('findstale',
            help="Find stale accounts and report/disable per config")
    p.set_defaults(func=cmd_findstale)


    ######
    # computer
    p_computer = sub.add_parser('computer',
            help="Computer sub-commands")
    sp_computer = p_computer.add_subparsers(metavar='SUBCOMMAND')
    sp_computer.required = True

    # computer assign
    p = sp_computer.add_parser('assign',
            help="Assign missing uidNumber attributes")
    p.set_defaults(func=cmd_computer_assign)
    add_assign_opts(p)

    # computer list
    p = sp_computer.add_parser('list',
            help="List computers")
    p.set_defaults(func=cmd_computer_list)


    ######
    # group
    p_group = sub.add_parser('group',
            help="Group sub-commands")
    sp_group = p_group.add_subparsers(metavar='SUBCOMMAND')
    sp_group.required = True

    # group assign
    p = sp_group.add_parser('assign',
            help="Assign missing gidNumber attributes")
    p.set_defaults(func=cmd_group_assign)
    add_assign_opts(p)

    # group list
    p = sp_group.add_parser('list',
            help="List groups")
    p.set_defaults(func=cmd_group_list)


    #######
    # state
    p_state = sub.add_parser('state',
            help="State sub-commands")
    sp_state = p_state.add_subparsers(metavar='SUBCOMMAND')
    sp_state.required = True

    # state list
    p = sp_state.add_parser('list',
            help="List state information")
    p.set_defaults(func=cmd_state_list)

    # state init
    p = sp_state.add_parser('init',
            help="Initialize state information")
    mx = p.add_mutually_exclusive_group()
    mx.add_argument('--force', dest='behavior', action='store_const', const='force',
            help="Force re-initialization; overwrite existing values with max(xidNumber)+1")
    mx.add_argument('--ignore', dest='behavior', action='store_const', const='ignore',
            help="Ignore partially-initialized state and initialize other values")
    p.set_defaults(func=cmd_state_init)


    ######
    # user
    p_user = sub.add_parser('user',
            help="User sub-commands")
    sp_user = p_user.add_subparsers(metavar='SUBCOMMAND')
    sp_user.required = True

    # user assign
    p = sp_user.add_parser('assign',
            help="Assign missing uidNumber attributes")
    p.set_defaults(func=cmd_user_assign)
    add_assign_opts(p)

    # user checkexpire
    p = sp_user.add_parser('checkexpire',
            help="Check for expiring/expired passwords")
    p.set_defaults(func=cmd_user_checkexpire)

    # user setupns
    p = sp_user.add_parser('setupns',
            help="Set userPrincipalName attributes")
    p.set_defaults(func=cmd_user_setupns)

    # user list
    p = sp_user.add_parser('list',
            help="List users")
    p.set_defaults(func=cmd_user_list)

    # user mkdirs
    p = sp_user.add_parser('mkdirs',
            help="Make user directories")
    p.set_defaults(func=cmd_user_mkdirs)


    return ap.parse_args()


def run_app(args):
    try:
        args.func(args)
    except AssignmentError as e:
        raise AppError(e)
    except KerberosError as e:
        raise AppError(e)


def main():
    args = parse_args()

    setup_logging(args)

    # Load config
    try:
        args.config = Config.load(args.config)
    except ConfigError as e:
        print("Config file error:", e, file=sys.stderr)
        sys.exit(1)

    # Run command
    try:
        run_app(args)
    except AppError as e:
        # TODO: Just raise or show backtrace if --debug is given
        print("Error:", e, file=sys.stderr)
        sys.exit(1)
