# SPDX-License-Identifier: Apache-2.0

import logging
import re
import typing as t

import click

import wataash_utils as wu

# HACK: terminal_width=999: to avoid wrapping in epilog
ctx_settings = dict(help_option_names=['-h', '--help'], terminal_width=999)
opt_defaults = {'show_envvar': True}


def opts_exclusive(ctx: click.Context, *args: t.Tuple[str, bool]):
    args = [x[0] for x in args if x[1]]
    if len(args) in [0, 1]:
        return
    msg = f'{wu.str.cat_and(args)} are mutually exclusive'
    raise click.UsageError(msg, ctx=ctx)


def opts_need_any(ctx: click.Context, *args: t.Tuple[str, bool]):
    if len(args) in [0, 1]:
        raise ValueError(f'len(args):{len(args)} must be >= 2')
    if len([True for x in args if x[1]]) != 0:
        return
    msg = f'one of following options needed: {wu.str.cat_or([x[0] for x in args])}'
    raise click.UsageError(msg, ctx=ctx)


def opts_need_one(ctx: click.Context, *args: t.Tuple[str, bool]):
    opts_exclusive(ctx, *args)
    opts_need_any(ctx, *args)


def parse_date_ym_slash(ctx: click.Context, ym, opt: t.Optional[str] = None) -> t.Tuple[int, int]:
    """'2006/01/02' -> (2006, 1)"""
    match = re.search(r'^(\d{4})/(\d\d)$', ym)
    if match is not None:
        return tuple(map(int, match.groups()))
    if opt is None:
        opt = 'argument'
    msg = f'invalid {opt}: {ym} (must be form of YYYY/MM)'
    raise click.UsageError(msg, ctx=ctx)


def parse_date_ymd_slash(ctx: click.Context, ymd: str, opt: t.Optional[str] = None) -> t.Tuple[int, int, int]:
    """'2006/01/02' -> (2006, 1, 2)"""
    match = re.search(r'^(\d{4})/(\d\d)/(\d\d)$', ymd)
    if match is not None:
        return tuple(map(int, match.groups()))
    if opt is None:
        opt = 'argument'
    msg = f'invalid {opt}: {ymd} (must be form of "YYYY/MM/DD")'
    raise click.UsageError(msg, ctx=ctx)


def parse_quiet_verbose(ctx: click.Context, quiet: bool, verbose: int) -> int:
    if quiet and verbose:
        msg = '--quiet and --verbose are mutually exclusive'
        raise click.UsageError(msg, ctx=ctx)
    if quiet:
        return logging.ERROR
    elif verbose == 0:
        return logging.WARNING
    elif verbose == 1:
        return logging.INFO
    elif verbose >= 2:
        return logging.DEBUG
