# vi:et:ts=4 sw=4 sts=4
#
# hgwebplus
# Copyright (c) 2020 Gary Kramlich <grim@reaperworld.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with hgwebplus.  If not, see <https://www.gnu.org/licenses/>.

import re

from hashlib import md5 as hashlib_md5

from mercurial import (
    extensions,
    match,
    mdiff,
    patch,
    registrar,
    templateutil
)
from mercurial.hgweb import webutil, hgweb_mod, hgwebdir_mod
from mercurial.hgweb.common import paritygen

try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import mistune

from mistune.directives import DirectiveToc


filters = {}
templatefilter = registrar.templatefilter(filters)


@templatefilter(b'md5', intype=bytes)
def md5(text):
    """ md5 is a template filter that will return an MD5 hash for whatever text
        was given to it.  This is typically used to generate gravatar URLs.
    """
    return hashlib_md5(text).hexdigest().encode('ascii')


def _diffstattmplgen(orig, context, ctx, statgen, parity):
    """ This is a reimplementation of hgweb.webutil._diffstattmplgen.  It adds
        the number lines add and removed as well as if the file is binary or
        not.

        This allows you to output something like the following instead of just
        having percentages.

            file1.txt +10 -2
            file2.txt +20 -0
    """
    stats, maxname, maxtotal, addtotal, removetotal, binary = next(statgen)
    files = ctx.files()

    def pct(i):
        if maxtotal == 0:
            return 0
        return (float(i) / maxtotal) * 100

    fileno = 0
    for filename, adds, removes, isbinary in stats:
        template = b'diffstatlink' if filename in files else b'diffstatnolink'
        total = adds + removes
        fileno += 1

        data = {
            b'node': ctx.hex(),
            b'file': filename,
            b'fileno': fileno,
            b'total': total,
            b'added': adds,
            b'addpct': pct(adds),
            b'removed': removes,
            b'removepct': pct(removes),
            b'parity': next(parity),
            b'binary': isbinary,
        }

        yield context.process(template, data)


# This regular expression captures the start line numbers from the hunk token
# for a diff.
RE_DIFF = re.compile(r'^@@ -(\d+),\d+ \+(\d+),\d+ @@')


def _prettyprintdifflines(context, lines, blockno, lineidprefix, filea, reva,
                          fileb, revb):
    """ This function is an updated version of
        hgweb.webutil._prettyprintdifflines.  It maintains backwards
        compatibility but adds a lot of new features.  This is not directly
        wrapped, but is instead called from _diffsgen below, which is wrapped.

        This version provides additional details about each file.  The
        filenames are in filea, and fileb; The line number that's being
        displayed for both filea and fileb are in linea and lineb.  And finally
        the revision of each file is available in reva and revb.
    """
    linea = 0
    lineb = 0

    seena = False
    seenb = False

    for lineno, l in enumerate(lines, 1):
        match = RE_DIFF.match(l.decode('utf8'))
        if match is not None:
            ltype = b'difflineat'
            groups = match.groups()
            linea = int(groups[0])
            lineb = int(groups[1])
            seena = False
            seenb = False
        elif l.startswith(b'---'):
            ltype = b'difflineminus'
            linea = 0
        elif l.startswith(b'+++'):
            ltype = b'difflineplus'
            lineb = 0
        elif l.startswith(b'-'):
            # only increment if we've already seen a minus line
            if seena:
                linea += 1
            ltype = b'difflineminus'
            seena = True
        elif l.startswith(b'+'):
            # only increment if we've already seen a plus line
            if seenb:
                lineb += 1
            ltype = b'difflineplus'
            seenb = True
        else:
            # only increment if we've already seen a plus/minus line
            if seena:
                linea += 1
            if seenb:
                lineb += 1
            seena = True
            seenb = True

            ltype = b'diffline'

        difflineno = b"%d.%d" % (blockno, lineno)

        data = {
            b'filea': filea,
            b'fileb': fileb,
            b'line': l,
            b'linea': linea,
            b'lineb': lineb,
            b'lineid': lineidprefix + b"l%s" % difflineno,
            b'lineno': lineno,
            b'linenumber': b"% 8s" % difflineno,
            b'reva': reva,
            b'revb': revb,
        }

        yield context.process(ltype, data)


def _diffsgen(
    orig,
    context,
    repo,
    ctx,
    basectx,
    files,
    style,
    stripecount,
    linerange,
    lineidprefix,
):
    """ this is a updated version of hgweb.webutil._diffsgen.  It maintains
        backwards compatibility but adds some additional values to the template
        context.  They are change type, filea, fileb, reva, revb.

        change type is one of modified, added, removed, or renamed.  filea and
        fileb are the respective file names.  Likewise, reva and revb are the
        respective revisions.
    """
    if files:
        m = match.exact(files)
    else:
        m = match.always()

    diffopts = patch.diffopts(repo.ui, untrusted=True)
    parity = paritygen(stripecount)

    diffhunks = patch.diffhunks(repo, basectx, ctx, m, opts=diffopts)
    for blockno, (fctx1, fctx2, header, hunks) in enumerate(diffhunks, 1):
        filea, fileb = b'/dev/null', b'/dev/null'
        reva, revb = b'', b''

        if fctx1 is not None:
            filea = fctx1.path()
            reva = fctx1.hex()

        if fctx2 is not None:
            fileb = fctx2.path()
            revb = fctx2.hex()

        if style != b'raw':
            header = header[1:]
        lines = [h + b'\n' for h in header]
        for hunkrange, hunklines in hunks:
            if linerange is not None and hunkrange is not None:
                s1, l1, s2, l2 = hunkrange
                if not mdiff.hunkinrange((s2, l2), linerange):
                    continue
            lines.extend(hunklines)

        args = (lines, blockno, lineidprefix, filea, reva, fileb, revb)
        prettylines = templateutil.mappedgenerator(_prettyprintdifflines, args)

        changetype = b'modified'
        if filea == b'/dev/null':
            changetype = b'added'
        elif fileb == b'/dev/null':
            changetype = b'removed'
        elif filea != fileb:
            changetype = b'renamed'

        data = {
            b'blockno': blockno,
            b'changetype': changetype,
            b'filea': filea,
            b'fileb': fileb,
            b'lines': prettylines,
            b'parity': next(parity),
            b'reva': reva,
            b'revb': revb,
        }

        yield data


def http_clone_url(context, mapping):
    """ http_clone_url is a template keyword that outputs the configuration
        value of `web.http_clone_url`.  It can be used in themes to make it
        easier for users to clone repositories.
    """

    urlbase = context.symbol(mapping, b'urlbase')
    if urlbase.endswith(b'/'):
        urlbase = urlbase[:-1]

    path = context.symbol(mapping, b'url')
    if path.startswith(b'/'):
        path = path[1:]

    return urlbase + b'/' + path


def http_base_url(context, mapping):
    """ http_base_url is a template keyword that outputs the configuration
        value of `web.http_base_url`.  It can be used in themes to make it
        easier for users to clone repositories.
    """

    ui = context.resource(mapping, b'ui')

    return ui.config(b'web', b'http_base_url', b'')


def readme(context, mapping):
    """ readme is a template keyword that will attempt to render a readme file
        that is available in the repository.  It currently supports github
        flavored markdown and plain text.
    """

    ctx = context.resource(mapping, b'ctx')

    class Renderer(mistune.HTMLRenderer):
        def image(self, src, alt, title):
            if urlparse(src).netloc == '':
                src = 'rawfile/%s/%s' % (ctx.rev(), src)

            return super().image(src, alt, title)

    # we iterate the files instead of a fileset, because we want to
    # deterministically render readmes in the same order if there are more
    # than one in a repository.  With the fileset, we'd have to run through
    # the generator and call .lower on each item again, and then we'd lose
    # the ability to fallback if the prioritized one failed to render.
    for filename in ctx:
        lower = filename.lower()
        if lower in [b'readme.txt', b'readme', b'readme.md']:
            raw_utf8 = ctx[filename].data().decode('utf-8')

            plugins = [
                DirectiveToc(),
                'footnotes',
                'strikethrough',
                'table',
                'url',
            ]

            markdown = mistune.create_markdown(
                renderer=Renderer(),
                plugins=plugins,
            )

            return markdown(raw_utf8).encode('utf-8')

    return ""


def ssh_clone_url(context, mapping):
    """ ssh_clone_url is a template keyword that outputs the configuration
        value of `web.ssh_clone_url`.  It can be used in themes to make it
        easier for users to clone repositories.
    """

    ui = context.resource(mapping, b'ui')

    return ui.config(b'web', b'ssh_clone_url', b'')


def dir_custom_templater(orig, self, req, nonce):
    templater = orig(self, req, nonce)

    templatekeyword = registrar.templatekeyword(templater._proc._defaults)

    sub_title = lambda c, m: self.ui.config(b'web', b'sub_title', b'')
    templatekeyword(b'sub_title', requires=())(sub_title)

    title = lambda c, m: self.ui.config(b'web', b'title', b'')
    templatekeyword(b'title', requires=())(title)

    return templater


def repo_custom_templater(orig, self, req):
    """ this function is a wrapper of hgweb_mod.requestcontext.templater.  This
        is done to be able to add custom keywords into hgweb.  This is not an
        ideal solution, and in fact feels very hacky.  However, at the time of
        this writing, it appears to be the only way to do this.
    """
    templater = orig(self, req)

    templatekeyword = registrar.templatekeyword(templater._proc._defaults)

    templatekeyword(b'http_clone_url', requires=())(http_clone_url)
    templatekeyword(b'readme', requires={b'ctx', b'repo'})(readme)
    templatekeyword(b'ssh_clone_url', requires={b'ui', b'repo'})(ssh_clone_url)

    sub_title = lambda c, m: self.config(b'web', b'sub_title', b'')
    templatekeyword(b'sub_title', requires=())(sub_title)

    title = lambda c, m: self.config(b'web', b'title', b'')
    templatekeyword(b'title', requires=())(title)

    return templater


def extsetup(ui):
    extensions.wrapfunction(webutil, '_diffstattmplgen', _diffstattmplgen)
    extensions.wrapfunction(webutil, '_diffsgen', _diffsgen)

    # these nasty but amazingly working hacks are from av6
    extensions.wrapfunction(
        hgwebdir_mod.hgwebdir,
        'templater',
        dir_custom_templater,
    )
    extensions.wrapfunction(
        hgweb_mod.requestcontext,
        'templater',
        repo_custom_templater,
    )
