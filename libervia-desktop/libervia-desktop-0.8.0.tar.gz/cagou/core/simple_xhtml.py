#!/usr/bin/env python3


# Cagou: desktop/mobile frontend for Salut à Toi XMPP client
# Copyright (C) 2016-2021 Jérôme Poisson (goffi@goffi.org)

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.

# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


from xml.etree import ElementTree as ET
from kivy.uix.stacklayout import StackLayout
from kivy.uix.label import Label
from kivy.utils import escape_markup
from kivy.metrics import sp
from kivy import properties
from sat.core import log as logging
from sat_frontends.tools import css_color, strings as sat_strings
from cagou import G
from cagou.core.common  import SizedImage


log = logging.getLogger(__name__)


class Escape(str):
    """Class used to mark that a message need to be escaped"""


class SimpleXHTMLWidgetEscapedText(Label):

    def on_parent(self, instance, parent):
        if parent is not None:
            self.font_size = parent.font_size

    def _addUrlMarkup(self, text):
        text_elts = []
        idx = 0
        links = 0
        while True:
            m = sat_strings.RE_URL.search(text[idx:])
            if m is not None:
                text_elts.append(escape_markup(m.string[0:m.start()]))
                link_key = 'link_' + str(links)
                url = m.group()
                escaped_url = escape_markup(url)
                text_elts.append(
                    f'[color=5500ff][ref={link_key}]{escaped_url}[/ref][/color]')
                if not links:
                    self.ref_urls = {link_key: url}
                else:
                    self.ref_urls[link_key] = url
                links += 1
                idx += m.end()
            else:
                if links:
                    text_elts.append(escape_markup(text[idx:]))
                    self.markup = True
                    self.text = ''.join(text_elts)
                break

    def on_text(self, instance, text):
        # do NOT call the method if self.markup is set
        # this would result in infinite loop (because self.text
        # is changed if an URL is found, and in this case markup too)
        if text and not self.markup:
            self._addUrlMarkup(text)

    def on_ref_press(self, ref):
        url = self.ref_urls[ref]
        G.local_platform.open_url(url, self)


class SimpleXHTMLWidgetText(Label):

    def on_parent(self, instance, parent):
        if parent is not None:
            self.font_size = parent.font_size


class SimpleXHTMLWidget(StackLayout):
    """widget handling simple XHTML parsing"""
    xhtml = properties.StringProperty()
    color = properties.ListProperty([1, 1, 1, 1])
    # XXX: bold is only used for escaped text
    bold = properties.BooleanProperty(False)
    font_size = properties.NumericProperty(sp(14))

    # text/XHTML input

    def on_xhtml(self, instance, xhtml):
        """parse xhtml and set content accordingly

        if xhtml is an instance of Escape, a Label with no markup will be used
        """
        self.clear_widgets()
        if isinstance(xhtml, Escape):
            label = SimpleXHTMLWidgetEscapedText(
                text=xhtml, color=self.color, bold=self.bold)
            self.bind(font_size=label.setter('font_size'))
            self.bind(color=label.setter('color'))
            self.bind(bold=label.setter('bold'))
            self.add_widget(label)
        else:
            xhtml = ET.fromstring(xhtml.encode())
            self.current_wid = None
            self.styles = []
            self._callParseMethod(xhtml)
        if len(self.children) > 1:
            self._do_split_labels()

    def escape(self, text):
        """mark that a text need to be escaped (i.e. no markup)"""
        return Escape(text)

    def _do_split_labels(self):
        """Split labels so their content can flow with images"""
        # XXX: to make things easier, we split labels in words
        log.debug("labels splitting start")
        children = self.children[::-1]
        self.clear_widgets()
        for child in children:
            if isinstance(child, Label):
                log.debug("label before split: {}".format(child.text))
                styles = []
                tag = False
                new_text = []
                current_tag = []
                current_value = []
                current_wid = self._createText()
                value = False
                close = False
                # we will parse the text and create a new widget
                # on each new word (actually each space)
                # FIXME: handle '\n' and other white chars
                for c in child.text:
                    if tag:
                        # we are parsing a markup tag
                        if c == ']':
                            current_tag_s = ''.join(current_tag)
                            current_style = (current_tag_s, ''.join(current_value))
                            if close:
                                for idx, s in enumerate(reversed(styles)):
                                    if s[0] == current_tag_s:
                                        del styles[len(styles) - idx - 1]
                                        break
                            else:
                                styles.append(current_style)
                            current_tag = []
                            current_value = []
                            tag = False
                            value = False
                            close = False
                        elif c == '/':
                            close = True
                        elif c == '=':
                            value = True
                        elif value:
                            current_value.append(c)
                        else:
                            current_tag.append(c)
                        new_text.append(c)
                    else:
                        # we are parsing regular text
                        if c == '[':
                            new_text.append(c)
                            tag = True
                        elif c == ' ':
                            # new word, we do a new widget
                            new_text.append(' ')
                            for t, v in reversed(styles):
                                new_text.append('[/{}]'.format(t))
                            current_wid.text = ''.join(new_text)
                            new_text = []
                            self.add_widget(current_wid)
                            log.debug("new widget: {}".format(current_wid.text))
                            current_wid = self._createText()
                            for t, v in styles:
                                new_text.append('[{tag}{value}]'.format(
                                    tag = t,
                                    value = '={}'.format(v) if v else ''))
                        else:
                            new_text.append(c)
                if current_wid.text:
                    # we may have a remaining widget after the parsing
                    close_styles = []
                    for t, v in reversed(styles):
                        close_styles.append('[/{}]'.format(t))
                    current_wid.text = ''.join(close_styles)
                    self.add_widget(current_wid)
                    log.debug("new widget: {}".format(current_wid.text))
            else:
                # non Label widgets, we just add them
                self.add_widget(child)
        self.splitted = True
        log.debug("split OK")

    # XHTML parsing methods

    def _callParseMethod(self, e):
        """Call the suitable method to parse the element

        self.xhtml_[tag] will be called if it exists, else
        self.xhtml_generic will be used
        @param e(ET.Element): element to parse
        """
        try:
            method = getattr(self, f"xhtml_{e.tag}")
        except AttributeError:
            log.warning(f"Unhandled XHTML tag: {e.tag}")
            method = self.xhtml_generic
        method(e)

    def _addStyle(self, tag, value=None, append_to_list=True):
        """add a markup style to label

        @param tag(unicode): markup tag
        @param value(unicode): markup value if suitable
        @param append_to_list(bool): if True style we be added to self.styles
            self.styles is needed to keep track of styles to remove
            should most probably be set to True
        """
        label = self._getLabel()
        label.text += '[{tag}{value}]'.format(
            tag = tag,
            value = '={}'.format(value) if value else ''
            )
        if append_to_list:
            self.styles.append((tag, value))

    def _removeStyle(self, tag, remove_from_list=True):
        """remove a markup style from the label

        @param tag(unicode): markup tag to remove
        @param remove_from_list(bool): if True, remove from self.styles too
            should most probably be set to True
        """
        label = self._getLabel()
        label.text += '[/{tag}]'.format(
            tag = tag
            )
        if remove_from_list:
            for rev_idx, style in enumerate(reversed(self.styles)):
                if style[0] == tag:
                    tag_idx = len(self.styles) - 1 - rev_idx
                    del self.styles[tag_idx]
                    break

    def _getLabel(self):
        """get current Label if it exists, or create a new one"""
        if not isinstance(self.current_wid, Label):
            self._addLabel()
        return self.current_wid

    def _addLabel(self):
        """add a new Label

        current styles will be closed and reopened if needed
        """
        self._closeLabel()
        self.current_wid = self._createText()
        for tag, value in self.styles:
            self._addStyle(tag, value, append_to_list=False)
        self.add_widget(self.current_wid)

    def _createText(self):
        label = SimpleXHTMLWidgetText(color=self.color, markup=True)
        self.bind(color=label.setter('color'))
        label.bind(texture_size=label.setter('size'))
        return label

    def _closeLabel(self):
        """close current style tags in current label

        needed when you change label to keep style between
        different widgets
        """
        if isinstance(self.current_wid, Label):
            for tag, value in reversed(self.styles):
                self._removeStyle(tag, remove_from_list=False)

    def _parseCSS(self, e):
        """parse CSS found in "style" attribute of element

        self._css_styles will be created and contained markup styles added by this method
        @param e(ET.Element): element which may have a "style" attribute
        """
        styles_limit = len(self.styles)
        styles = e.attrib['style'].split(';')
        for style in styles:
            try:
                prop, value = style.split(':')
            except ValueError:
                log.warning(f"can't parse style: {style}")
                continue
            prop = prop.strip().replace('-', '_')
            value = value.strip()
            try:
                method = getattr(self, f"css_{prop}")
            except AttributeError:
                log.warning(f"Unhandled CSS: {prop}")
            else:
                method(e, value)
        self._css_styles = self.styles[styles_limit:]

    def _closeCSS(self):
        """removed CSS styles

        styles in self._css_styles will be removed
        and the attribute will be deleted
        """
        for tag, __ in reversed(self._css_styles):
            self._removeStyle(tag)
        del self._css_styles

    def xhtml_generic(self, elem, style=True, markup=None):
        """Generic method for adding HTML elements

        this method handle content, style and children parsing
        @param elem(ET.Element): element to add
        @param style(bool): if True handle style attribute (CSS)
        @param markup(tuple[unicode, (unicode, None)], None): kivy markup to use
        """
        # we first add markup and CSS style
        if markup is not None:
            if isinstance(markup, str):
                tag, value = markup, None
            else:
                tag, value = markup
            self._addStyle(tag, value)
        style_ = 'style' in elem.attrib and style
        if style_:
            self._parseCSS(elem)

        # then content
        if elem.text:
            self._getLabel().text += escape_markup(elem.text)

        # we parse the children
        for child in elem:
            self._callParseMethod(child)

        # closing CSS style and markup
        if style_:
            self._closeCSS()
        if markup is not None:
            self._removeStyle(tag)

        # and the tail, which is regular text
        if elem.tail:
            self._getLabel().text += escape_markup(elem.tail)

    # method handling XHTML elements

    def xhtml_br(self, elem):
        label = self._getLabel()
        label.text+='\n'
        self.xhtml_generic(elem, style=False)

    def xhtml_em(self, elem):
        self.xhtml_generic(elem, markup='i')

    def xhtml_img(self, elem):
        try:
            src = elem.attrib['src']
        except KeyError:
            log.warning("<img> element without src: {}".format(ET.tostring(elem)))
            return
        try:
            target_height = int(elem.get('height', 0))
        except ValueError:
            log.warning(f"Can't parse image height: {elem.get('height')}")
            target_height = None
        try:
            target_width = int(elem.get('width', 0))
        except ValueError:
            log.warning(f"Can't parse image width: {elem.get('width')}")
            target_width = None

        img = SizedImage(
            source=src, target_height=target_height, target_width=target_width)
        self.current_wid = img
        self.add_widget(img)

    def xhtml_p(self, elem):
        if isinstance(self.current_wid, Label):
            self.current_wid.text+="\n\n"
        self.xhtml_generic(elem)

    def xhtml_span(self, elem):
        self.xhtml_generic(elem)

    def xhtml_strong(self, elem):
        self.xhtml_generic(elem, markup='b')

    # methods handling CSS properties

    def css_color(self, elem, value):
        self._addStyle("color", css_color.parse(value))

    def css_text_decoration(self, elem, value):
        if value == 'underline':
            self._addStyle('u')
        elif value == 'line-through':
            self._addStyle('s')
        else:
            log.warning("unhandled text decoration: {}".format(value))
