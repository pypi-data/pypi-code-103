"""Integrate templating system using nunjucks"""

from js_modules.nunjucks import nunjucks
from browser import window, document
import javascript


safe = nunjucks.runtime.SafeString.new
env = nunjucks.configure(
    window.templates_root_url,
    {
        'autoescape': True,
        'trimBlocks': True,
        'lstripBlocks': True,
        'web': {'useCache': True},
    })

nunjucks.installJinjaCompat()
env.addGlobal("profile", window.profile)
env.addGlobal("csrf_token", window.csrf_token)
# FIXME: integrate gettext or equivalent here
env.addGlobal("_", lambda txt: txt)


class Indexer:
    """Index global to a page"""

    def __init__(self):
        self._indexes = {}

    def next(self, value):
        if value not in self._indexes:
            self._indexes[value] = 0
            return 0
        self._indexes[value] += 1
        return self._indexes[value]

    def current(self, value):
        return self._indexes.get(value)


gidx = Indexer()
# suffix use to avoid collision with IDs generated in static page
SCRIPT_SUFF = "__script__"

def escape_html(txt):
    return (
        txt
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
    )


def get_args(n_args, *sig_args, **sig_kwargs):
    """Retrieve function args when they are transmitted using nunjucks convention

    cf. https://mozilla.github.io/nunjucks/templating.html#keyword-arguments
    @param n_args: argument from nunjucks call
    @param sig_args: expected positional arguments
    @param sig_kwargs: expected keyword arguments
    @return: all expected arguments, with default value if not specified in nunjucks
    """
    # nunjucks set kwargs in last argument
    given_args = list(n_args)
    try:
        given_kwargs = given_args.pop().to_dict()
    except (AttributeError, IndexError):
        # we don't have a dict as last argument
        # that happens when there is no keyword argument
        given_args = list(n_args)
        given_kwargs = {}
    ret = given_args[:len(sig_args)]
    # we check if we have remaining positional arguments
    # in which case they may be specified in keyword arguments
    for name in sig_args[len(given_args):]:
        try:
            value = given_kwargs.pop(name)
        except KeyError:
            raise ValueError(f"missing positional arguments {name!r}")
        ret.append(value)

    extra_pos_args = given_args[len(sig_args):]
    # and now the keyword arguments
    for name, default in sig_kwargs.items():
        if extra_pos_args:
            # kw args has been specified with a positional argument
            ret.append(extra_pos_args.pop(0))
            continue
        value = given_kwargs.get(name, default)
        ret.append(value)

    return ret


def _next_gidx(value):
    """Use next current global index as suffix"""
    next_ = gidx.next(value)
    return f"{value}{SCRIPT_SUFF}" if next_ == 0 else f"{value}_{SCRIPT_SUFF}{next_}"

env.addFilter("next_gidx", _next_gidx)


def _cur_gidx(value):
    """Use current current global index as suffix"""
    current = gidx.current(value)
    return f"{value}{SCRIPT_SUFF}" if not current else f"{value}_{SCRIPT_SUFF}{current}"

env.addFilter("cur_gidx", _cur_gidx)


def _xmlattr(d, autospace=True):
    if not d:
        return
    d = d.to_dict()
    ret = [''] if autospace else []
    for key, value in d.items():
        if value is not None:
            ret.append(f'{escape_html(key)}="{escape_html(str(value))}"')

    return safe(' '.join(ret))

env.addFilter("xmlattr", _xmlattr)


def _tojson(value):
    return safe(escape_html(window.JSON.stringify(value)))

env.addFilter("tojson", _tojson)


def _icon_use(name, cls=""):
    kwargs = cls.to_dict()
    cls = kwargs.get('cls')
    return safe(
        '<svg class="svg-icon{cls}" xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 100 100">\n'
        '    <use href="#{name}"/>'
        '</svg>\n'.format(name=name, cls=(" " + cls) if cls else "")
    )

env.addGlobal("icon", _icon_use)


def _date_fmt(
    timestamp, *args
):
    """Date formatting

    cf. sat.tools.common.date_utils for arguments details
    """
    fmt, date_only, auto_limit, auto_old_fmt, auto_new_fmt = get_args(
        args, fmt="short", date_only=False, auto_limit=7, auto_old_fmt="short",
        auto_new_fmt="relative",
    )
    from js_modules.moment import moment
    date = moment.unix(timestamp)

    if fmt == "auto_day":
        fmt, auto_limit, auto_old_fmt, auto_new_fmt = "auto", 0, "short", "HH:mm"
    if fmt == "auto":
        limit = moment().startOf('day').subtract(auto_limit, 'days')
        m_fmt = auto_old_fmt if date < limit else auto_new_fmt

    if fmt == "short":
        m_fmt = "DD/MM/YY" if date_only else "DD/MM/YY HH:mm"
    elif fmt == "medium":
        m_fmt = "ll" if date_only else "lll"
    elif fmt == "long":
        m_fmt = "LL" if date_only else "LLL"
    elif fmt == "full":
        m_fmt = "dddd, LL" if date_only else "LLLL"
    elif fmt == "relative":
        return date.fromNow()
    elif fmt == "iso":
        if date_only:
            m_fmt == "YYYY-MM-DD"
        else:
            return date.toISOString()
    else:
        raise NotImplementedError("free format is not implemented yet")

    return date.format(m_fmt)

env.addFilter("date_fmt", _date_fmt)


class I18nExtension:
    """Extension to handle the {% trans %}{% endtrans %} statement"""
    # FIXME: for now there is no translation, this extension only returns the string
    #        unmodified
    tags = ['trans']

    def parse(self, parser, nodes, lexer):
        tok = parser.nextToken()
        args = parser.parseSignature(None, True)
        parser.advanceAfterBlockEnd(tok.value)
        body = parser.parseUntilBlocks('endtrans')
        parser.advanceAfterBlockEnd()
        return nodes.CallExtension.new(self._js_ext, 'run', args, [body])

    def run(self, context, *args):
        body = args[-1]
        return body()

    @classmethod
    def install(cls, env):
        ext = cls()
        ext_dict = {
            "tags": ext.tags,
            "parse": ext.parse,
            "run": ext.run
        }
        ext._js_ext = javascript.pyobj2jsobj(ext_dict)
        env.addExtension(cls.__name__, ext._js_ext)

I18nExtension.install(env)


class Template:

    def __init__(self, tpl_name):
        self._tpl = env.getTemplate(tpl_name, True)

    def render(self, context):
        return self._tpl.render(context)

    def get_elt(self, context=None):
        if context is None:
            context = {}
        raw_html = self.render(context)
        template_elt = document.createElement('template')
        template_elt.innerHTML = raw_html
        return template_elt.content.firstElementChild
