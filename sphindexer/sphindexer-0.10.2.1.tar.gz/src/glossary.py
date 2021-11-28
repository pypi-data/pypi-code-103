import re
import unicodedata
from typing import List, Tuple

from docutils import nodes
from docutils.nodes import Node, system_message
from docutils.parsers.rst import directives
from docutils.statemachine import StringList

from sphinx import addnodes
from sphinx.domains.std import split_term_classifiers, make_glossary_term
from sphinx.locale import _
from sphinx.util import docname_join, logging
from sphinx.util.docutils import SphinxDirective
from sphinx.util.typing import OptionSpec


logger = logging.getLogger(__name__)


class BaseGlossary(SphinxDirective):

    has_content = True
    required_arguments = 0
    optional_arguments = 0
    final_argument_whitespace = False
    option_spec: OptionSpec = {
        'classifier': directives.unchanged,
        'sorted': directives.flag,
    }

    def run(self) -> List[Node]:
        # first, collect single entries
        entries: List[Tuple[List[Tuple[str, str, int]], StringList]] = []
        in_definition = True
        in_comment = False
        was_empty = True
        messages: List[Node] = []
        for line, (source, lineno) in zip(self.content, self.content.items):
            # empty line -> add to last definition
            if not line:
                if in_definition and entries:
                    entries[-1][1].append('', source, lineno)
                was_empty = True
                continue
            # unindented line -> a term
            if line and not line[0].isspace():
                # enable comments
                if line.startswith('.. '):
                    in_comment = True
                    continue
                else:
                    in_comment = False

                # first term of definition
                if in_definition:
                    if not was_empty:
                        messages.append(self.state.reporter.warning(
                            _('glossary term must be preceded by empty line'),
                            source=source, line=lineno))
                    entries.append(([(line, source, lineno)], StringList()))
                    in_definition = False
                # second term and following
                else:
                    if was_empty:
                        messages.append(self.state.reporter.warning(
                            _('glossary terms must not be separated by empty lines'),
                            source=source, line=lineno))
                    if entries:
                        entries[-1][0].append((line, source, lineno))
                    else:
                        messages.append(self.state.reporter.warning(
                            _('glossary seems to be misformatted, check indentation'),
                            source=source, line=lineno))
            elif in_comment:
                pass
            else:
                if not in_definition:
                    # first line of definition, determines indentation
                    in_definition = True
                    indent_len = len(line) - len(line.lstrip())
                if entries:
                    entries[-1][1].append(line[indent_len:], source, lineno)
                else:
                    messages.append(self.state.reporter.warning(
                        _('glossary seems to be misformatted, check indentation'),
                        source=source, line=lineno))
            was_empty = False

        # now, parse all the entries into a big definition list
        return messages + self.make_glossary(entries)

    def inline_text(self, text, lineno):
        return self.state.inline_text(text, lineno)

    def make_glossary_term(self, textnodes, index_key, source, lineno, node_id, document):
        return make_glossary_term(self.env, textnodes, index_key, source, lineno,
                                  node_id=node_id, document=document)

    def make_glossary(self, entries):
        node = addnodes.glossary()
        node.document = self.state.document
        classifier = self.options.get('classifier')

        items = []
        for terms, definition in entries:
            termtexts: List[str] = []
            termnodes: List[Node] = []
            system_messages: List[Node] = []
            for line, source, lineno in terms:
                parts = split_term_classifiers(line)
                # parse the term with inline markup
                # classifiers (parts[1:]) will not be shown on doctree
                textnodes, sysmsg = self.inline_text(parts[0], lineno)

                # use first classifier as a index key
                if classifier and not parts[1]:
                    parts[1] = classifier
                term = self.make_glossary_term(textnodes, parts[1], source, lineno,
                                               node_id=None, document=self.state.document)
                term.rawsource = line
                system_messages.extend(sysmsg)
                termtexts.append(term.astext())
                termnodes.append(term)

            termnodes.extend(system_messages)

            defnode = nodes.definition()
            if definition:
                self.state.nested_parse(definition, definition.items[0][1],
                                        defnode)
            termnodes.append(defnode)
            items.append((termtexts,
                          nodes.definition_list_item('', *termnodes)))

        if 'sorted' in self.options:
            items.sort(key=lambda x:
                       unicodedata.normalize('NFD', x[0][0].lower()))

        dlist = nodes.definition_list()
        dlist['classes'].append('glossary')
        dlist.extend(item[1] for item in items)
        node += dlist
        return [node]
