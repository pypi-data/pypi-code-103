#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.

import base
from base import rightdown
import textwrap


class BlockNode(rightdown.Node):
  ''' Parent class for any node that handles a block token. '''

  CONTROLLER_NAMESPACE  = rightdown.BlockTokenTypes



class BlockWithInlineMixin:
  ''' Methods in common for the several blocks that have a single blurb of their own text. '''

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.inline     = None    # an InlineNone instance
    self.text       = None    # the text you want us to generate it from in FinishProcessing()

  def FinishProcessing(self):
    if self.text:
      self.inline   = rightdown.Processor.ProcessInline(self.text)
      self.text     = None
    super().FinishProcessing()

  def Inline(self, methodname, *args, **kwargs):
    return self.inline and getattr(self.inline, methodname)(*args, **kwargs) or ''

  def TextParts(self, *args, **kwargs):
    return [self.Inline('Text')] + super().TextParts(*args, **kwargs)

  def HtmlParts(self, *args, **kwargs):
    return [self.Inline('Html')] + super().HtmlParts(*args, **kwargs)

  def DebugParts(self, rich=False, *args, **kwargs):
    suffix          = rich and self.inline and self.inline.DebugString(*args, **kwargs) or ''
    if self.options.truncate_width and len(suffix) > self.options.truncate_width:
      suffix        = suffix[:self.options.truncate_width-1] + '…'
    return super().DebugParts(rich=rich, suffix=suffix, *args, **kwargs)



class Fragment(BlockNode):
  ''' Usually the top-level node in a rightdown tree. '''

  CONTROLLER_NAME   = rightdown.BLOCK_FRAGMENT

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.first      = False   # set True by the Processor if this is the first Fragment in the file
    self.finished   = False   # used by RightDownData to not bother calling our finish method repeatedly

  def FinishProcessing(self):
    self.finished   = True
    if self.token:
      self.children = [x.MakeNode() for x in self.token.data]
    super().FinishProcessing()

  def TextParts(self, space_out_blocks=True, *args, **kwargs):
    results         = []
    if self.options.text_include_formatting and not self.first:
      if not self.children or self.children[0].type != rightdown.BLOCK_PSEUDO_YAML:
        if space_out_blocks:
          results.append('')
        results.append('---')
    almost          = super().TextParts(indent=False, space_out_blocks=space_out_blocks, *args, **kwargs)
    if almost:
      if not self.first and space_out_blocks:
        results.append('')
      results.extend(almost)
    return results

  def WrapHtml(self, indent=False, collapse_empty=True, *args, **kwargs):
    return super().WrapHtml(indent=False, collapse_empty=True, *args, **kwargs)

  def HtmlParts(self, indent=False, *args, **kwargs):
    section         = not self.first and ['<hr>'] or []
    section.extend(super().HtmlParts(indent=False, *args, **kwargs))
    return section



###
## Trivial Blocks
#


class TrivialNode(BlockNode):
  ''' A node in a rightdown tree that's a single static line of one uninteresting token. '''

  TRIVIAL_DEFAULT   = None

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.text       = None

  def FinishProcessing(self):
    if self.token:
      self.text     = self.token.data and self.token.data[0].data or None
    super().FinishProcessing()

  def TextParts(self, *args, **kwargs):
    if not self.options.text_include_formatting:
      return []
    if self.text:
      return [self.text]
    return self.TRIVIAL_DEFAULT

  # HtmlParts() is handled by our parent class, which just pulls the token from our .html pattern

base.registry.UnRegister(TrivialNode)


class HardBreak(TrivialNode):
  CONTROLLER_NAME   = rightdown.BLOCK_HARD_BREAK
  TRIVIAL_DEFAULT   = '---'


class SoftBreak(TrivialNode):
  CONTROLLER_NAME   = rightdown.BLOCK_SOFT_BREAK
  TRIVIAL_DEFAULT   = '...'


class Blank(TrivialNode):
  CONTROLLER_NAME   = rightdown.BLOCK_BLANK
  TRIVIAL_DEFAULT   = '.'



class VerbatimNode(BlockNode):
  ''' A block of lines that are rendered exactly as we saw them with no inline processing. '''

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.verbatim   = None

  def FinishProcessing(self):
    if self.token and self.token.data:
      self.verbatim = [x.longtext for x in self.token.data]
      self.htmlized = self.PrepareHtml(self.token.data)
    super().FinishProcessing()

  def PrepareHtml(self, linetokens):
    return [x.longtext for x in linetokens]

  def TextParts(self, *args, **kwargs):
    if self.verbatim is not None:
      return self.verbatim

  def HtmlParts(self, *args, **kwargs):
    if self.htmlized is not None:
      return self.htmlized
    return []

  def WrapHtml(self, indent=False, collapse_empty=False, *args, **kwargs):
    # our parent wraps our results in <pre> tags, that's nice, but we need to remove one newline
    results         = super().WrapHtml(indent=False, collapse_empty=False, *args, **kwargs)
    if results and len(results) > 1:
      results       = [results[0] + results[1]] + results[2:]
    return results

base.registry.UnRegister(VerbatimNode)


class IndentedCode(VerbatimNode):
  CONTROLLER_NAME   = rightdown.BLOCK_INDENTED_CODE

  def PrepareHtml(self, linetokens):
    strip           = min([0] + [x.white0 for x in linetokens])
    return [x.longtext[strip:] for x in linetokens]


class FencedCode(IndentedCode):
  CONTROLLER_NAME   = rightdown.BLOCK_FENCED_CODE

  def PrepareHtml(self, linetokens):
    if not self.options.html_include_formatting:
      if linetokens and linetokens[0].type == rightdown.LINE_FENCE:
        linetokens    = linetokens[1:]
      if linetokens and linetokens[-1].type == rightdown.LINE_FENCE:
        linetokens    = linetokens[:-1]

    if self.options.fenced_code_strip_space:
      return super().PrepareHtml(linetokens)

    return [x.longtext for x in linetokens]




class TablePlaceholder(VerbatimNode):
  ''' XYZZY:  this class is a placeholder until we do something smarter with tables. '''
  CONTROLLER_NAME   = rightdown.BLOCK_TABLE



###
## Recursive Blocks
#


class PseudoYaml(BlockNode):
  ''' A node that represents invisible metadata written as a YAML-like prefix. '''

  CONTROLLER_NAME   = rightdown.BLOCK_PSEUDO_YAML

  def FinishProcessing(self):
    if self.token:
      if (not self.token.data or
          self.token.data[0].type != rightdown.LINE_HARD_BREAK or
          self.token.data[-1].type != rightdown.LINE_SOFT_BREAK):
        raise base.errors.RightDownProcessingError('YAML pattern did not start and end with breaks.')
      linetokens    = self.token.data[1:-1]
      blocktokens   = rightdown.BlockTokenizer().Tokenize(linetokens)
      self.children = [x.MakeNode() for x in blocktokens]
    super().FinishProcessing()

  def TextParts(self, space_out_blocks=True, *args, **kwargs):
    if not self.options.text_include_formatting:
      return []
    results         = self._AccumulateLists('WrapText', indent=False, space_out_blocks=False, *args, **kwargs)
    if results:
      results       = ['---'] + results + ['...']
    else:
      results       = ['---']
    return results

  def WrapHtml(self, *args, **kwargs):
    return []

  def Metadata(self, html=False, strip=False):
    return super().Fields(html=html, strip=strip)

  def Fields(self, html=False, strip=False):
    return {}



class Quote(BlockNode):
  ''' A node that represents invisible metadata written as a YAML-like prefix. '''

  CONTROLLER_NAME   = rightdown.BLOCK_QUOTE

  def FinishProcessing(self):
    if not self.token or not self.token.data:
      return super().FinishProcessing()

    lines           = []
    for linetoken in (self.token.data or []):
      if linetoken.data.startswith('>'):
        line        = linetoken.data[1:]
        if line.startswith(' '):
          line      = line[1:]
        lines.append(line)
    content         = '\n'.join(lines)

    linetokens      = rightdown.LineTokenizer().Tokenize(content)
    blocktokens     = rightdown.BlockTokenizer().Tokenize(linetokens)
    self.children   = [x.MakeNode() for x in blocktokens]
    super().FinishProcessing()

  def TextParts(self, indent=False, space_out_blocks=True, *args, **kwargs):
    innertext       = super().TextParts(indent=False, space_out_blocks=True, *args, **kwargs)
    if self.options.text_include_formatting:
      innertext     = [(x and ('> '+x) or '>') for x in innertext]
    return innertext

  def HtmlParts(self, indent=False, *args, **kwargs):
    innerhtml       = super().HtmlParts(indent=False, *args, **kwargs)
    if self.options.html_include_formatting:
      innerhtml     = [(x and ('&gt; '+x) or '&gt;') for x in innerhtml]
    return innerhtml



class List(BlockNode):
  ''' A bullet, number, or alpha list. '''

  CONTROLLER_NAME   = rightdown.BLOCK_LIST

  def __init__(self, *args, linetokens=[], **kwargs):
    super().__init__(*args, **kwargs)
    self.linetokens = linetokens

  @property
  def html(self):
    if self.children and self.children[0].linetype == rightdown.LINE_BULLET_LIST:
      return 'ul'
    return 'ol'

  def FinishProcessing(self):
    ''' Breaks our line tokens -- from token.data or an outer List -- into Items '''
    linetokens      = self.linetokens or (self.token and self.token.data) or None
    if not linetokens:
      return super().FinishProcessing()

    current         = None
    for linetoken in (linetokens or []):
      if linetoken.type in rightdown.LINE_LIST_TYPES and (not current or linetoken.white0 <= current.white0):
        current     = self.Item().SetupForLine(linetoken)
        self.children.append(current)
      elif current:
        current.contains.append(linetoken)

    self.linetokens = None
    return super().FinishProcessing()

  def TextParts(self, space_out_blocks=True, *args, **kwargs):
    return super().TextParts(space_out_blocks=False, *args, **kwargs)

  class Item(BlockWithInlineMixin, BlockNode):
    ''' A single bullet, number, or alpha in a list of them. '''

    CONTROLLER_NAME = rightdown.BLOCK_LIST_ITEM

    def __init__(self, **kwargs):
      super().__init__(**kwargs)
      self.linetype = None    # one of the line types that maps to a list block type
      self.inline   = None    # tree of inline nodes that represent our own text

      self.white0   = 0       # whitespace before our symbol
      self.symbol   = None    # leading character on the line that we came from
      self.symbolen = 0       # character count of our symbol (usually 1 or 2)
      self.white1   = 0       # whitespace after our symbol before our text

      # these are wiped when FinishProcessing is called
      self.contains = []
      self.text     = None

    def SetupForLine(self, linetoken):
      ''' Injests a line token into ourselves. '''
      self.linetype = linetoken.type
      self.inline   = None

      self.white0   = linetoken.white0
      self.symbol   = None
      self.symbolen = 1
      self.white1   = 0

      self.contains = []
      self.text     = linetoken.data

      if self.linetype == rightdown.LINE_BULLET_LIST:
        self.StripSymbol('-*', ' ')
      elif self.linetype == rightdown.LINE_NUMBER_LIST:
        self.StripSymbol('0123456789', '.', ' ')
      elif self.linetype == rightdown.LINE_ALPHA_LIST:
        self.StripSymbol('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ', '.', ' ')

      return self

    def StripSymbol(self, *symbolsets):
      ''' Removes the leading characters from our text that match a pattern of symbols. '''
      for symbolset in symbolsets:
        if self.text and self.text[0] in symbolset:
          if self.symbol is None:
            self.symbol   = self.text[0]
          if self.symbol.isspace():
            self.white1   = self.white1 + 1
          else:
            self.symbolen = self.symbolen + 1
          self.text = self.text[1:]

    def Symbol(self, format):
      ''' Returns the formatting symbol if appropriate to the format being rendered. '''
      include       = getattr(self.options, format + '_include_formatting')
      if not include:
        return format == 'text' and ' '*self.options.tab_width or ''
      aftersymbol   = self.linetype == rightdown.LINE_BULLET_LIST and ' ' or '. '
      return self.symbol + aftersymbol

    def Inline(self, methodname, *args, **kwargs):
      return self.Symbol(methodname.lower()) + super().Inline(methodname, *args, **kwargs)

    def FinishProcessing(self):
      ''' Breaks our list of contained linetokens into three parts: Paragraph, List, Paragraph. '''
      if not self.contains:
        return super().FinishProcessing()

      mindent       = self.white0 + self.symbolen
      before        = []
      childlines    = []
      after         = []
      for linetoken in self.contains:
        if linetoken.type in rightdown.LINE_LIST_TYPES:
          childlines.append(linetoken)
        elif linetoken.white0 >= mindent and childlines:
          childlines.append(linetoken)
        elif childlines:
          after.append(linetoken)
        else:
          before.append(linetoken)

      if before:
        self.children.append(Paragraph(linetokens=before))

      if childlines:
        self.children.append(List(linetokens=childlines))

      if after:
        self.children.append(Paragraph(linetokens=after))

      super().FinishProcessing()

    def WrapText(self, indent=True, *args, **kwargs):
      ''' Subsumes the function of TextParts() too, all so we can fix indenting. '''
      inlined         = self.Inline('Text')
      childparts      = rightdown.Node.TextParts(self, *args, **kwargs)
      if indent:
        indent        = ' '*self.options.tab_width
        childparts    = [indent + x for x in childparts]
      return [inlined] + childparts



###
## Structured Data Blocks
#


class Field(BlockNode):
  ''' A node that's "key: [ value, ... ]" for zero or more values. '''

  CONTROLLER_NAME   = rightdown.BLOCK_FIELD

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.key        = None    # InlineNode
    self.vals       = []      # [InlineNone, ...]

  def FinishProcessing(self):
    if self.token and self.token.data:
      if ':' in self.token.data[0].data:
        key, val0   = [x.strip() for x in (self.token.data[0].data or ':').split(':', 1)]
      else:
        key         = self.token.data[0].data
        val0        = ''
      self.key      = key and rightdown.Processor.ProcessInline(key) or None

      vals          = [val0]
      for linetoken in self.token.data[1:]:
        text        = linetoken.data
        if text.startswith(':'):
          text      = text[1:].lstrip()
          vals.append(text)
        elif text and vals[-1]:
          vals[-1]  = ' '.join((vals[-1], text))
        else:
          vals[-1]  = text

      vals          = [x for x in vals if x]
      self.vals     = vals and [rightdown.Processor.ProcessInline(x) for x in vals] or []
    super().FinishProcessing()

  def DebugParts(self, rich=False, *args, **kwargs):
    suffix          = ''
    if rich:
      key           = self.key and self.key.DebugString(*args, **kwargs) or ''
      vals          = ', '.join([x.DebugString(*args, **kwargs) for x in self.vals])
      suffix        = ': '.join((key, vals))
      if self.options.truncate_width and len(suffix) > self.options.truncate_width:
        suffix      = suffix[:self.options.truncate_width-1] + '…'
    return super().DebugParts(suffix=suffix, rich=rich, *args, **kwargs)

  def TextParts(self, *args, **kwargs):
    key             = self.key and self.key.Text(*args, **kwargs) or ''
    vals            = [x.Text(*args, **kwargs) for x in self.vals]

    if len(vals) > 1:
      return self.TextPartsForMultiField(key, vals)

    key             = self.options.text_include_formatting and (key + ':') or key
    val             = vals and vals[0] or ''

    if self.options.wrap_width:
      wrapped0      = textwrap.wrap(key + ' ' + val, width=(self.options.wrap_width - self.options.tab_width))
      wrapped1      = [key] + textwrap.wrap(val, width=(self.options.wrap_width - self.options.tab_width))
      if len(wrapped0) == 1:
        return wrapped0
      wrapped1      = [wrapped1[0]] + [' '*self.options.tab_width + x for x in wrapped1[1:]]
      return wrapped1

    return [key + ' ' + val]

  def TextPartsForMultiField(self, key, vals):
    ''' Fields and MultiFields differ only by number of values we have, not by token type. '''
    if self.options.text_include_formatting:
      vals          = [': '+x for x in vals]
    else:
      vals          = [(' '*self.options.tab_width + x) for x in vals]

    # building this now to emit wrapped lines in multifield values, though it's
    # not allowed in markdown and currently not possible in our own system until
    # we give TagPattern a ? operator.
    if self.options.wrap_width:
      newvals       = []
      for val in vals:
        wrapped     = textwrap.wrap(val, width=(self.options.wrap_width - self.options.tab_width))
        wrapped     = '\n'.join([wrapped[0]] + [' '*self.options.tab_width for x in wrapped[1:]])
        newvals.append(wrapped)
      vals          = newvals

    return [key] + vals

  def HtmlParts(self, indent=True, *args, **kwargs):
    if not self.key and not self.vals:
      return []
    indent          = ' '*self.options.tab_width
    classname       = base.utils.ClassName(self).lower()
    if classname != 'field':
      classname     = 'field ' + classname

    key             = self.key and self.key.Html(*args, **kwargs) or ''
    vals            = [x.Html(*args, **kwargs) for x in self.vals]

    if self.options.html_include_formatting:
      vals          = [': '+x for x in vals]

    if not self.options.definition_list_as_field:
      key           = indent + '<dt>' + key + '</dt>'
      vals          = [indent + '<dd>' + x + '</dd>' for x in vals]
      return ['<dl>', key] + vals + ['</dl>']

    if len(vals) == 1:
      vals          = [indent + '<span class="value">{}</span>'.format(vals[0])]
    elif vals:
      vals          = [indent + '<ul>'] + [2*indent + '<li class="value">{}</span>'.format(x) for x in vals] + [indent + '</ul>']

    results         = []
    results.append('<div class="{}">'.format(classname))
    results.append(indent + '<span class="key">{}</span>'.format(key))
    results.extend(vals)
    results.append('</div>')
    return results



class MultiField(Field):
  ''' MultiField comes out of processing as a different node type, but shares implementation with Field. '''

  CONTROLLER_NAME   = rightdown.BLOCK_MULTI_FIELD



###
## General Purpose Blocks
#



class Paragraph(BlockWithInlineMixin, BlockNode):
  ''' A node that's a simple "key: value" pair. '''

  CONTROLLER_NAME   = rightdown.BLOCK_PARAGRAPH

  def __init__(self, *args, linetokens=[], **kwargs):
    super().__init__(*args, **kwargs)
    self.linetokens = linetokens
    self.text       = None

  def FinishProcessing(self):
    linetokens      = self.linetokens or (self.token and self.token.data) or None
    self.text       = self.text or '\n'.join([(x.data or '') for x in linetokens])
    self.linetokens = None
    super().FinishProcessing()

  def TextParts(self, *args, **kwargs):
    textparts       = super().TextParts(*args, **kwargs)
    if not textparts or '\\\n' in textparts[0]:
      return textparts
    return textwrap.wrap(textparts[0], width=self.options.wrap_width)



class Heading(BlockWithInlineMixin, BlockNode):
  ''' Some level of title text. '''

  CONTROLLER_NAME   = rightdown.BLOCK_HEADING

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.count      = 0
    self.text       = None

  @property
  def html(self):
    return 'h' + str(self.count)

  def FinishProcessing(self):
    if self.token and self.token.data:
      unstripped    = self.token.data[0].data
      stripped      = unstripped.lstrip('#')
      self.count    = len(unstripped) - len(stripped)
      self.text     = stripped.lstrip()
    super().FinishProcessing()

  def TextParts(self, *args, **kwargs):
    textparts       = super().TextParts(*args, **kwargs)
    inlined         = self.Inline('Text')
    if self.options.text_include_formatting:
      return ['#'*self.count + ' ' + inlined]
    return [inlined]

  def HtmlParts(self, *args, **kwargs):
    htmlparts       = super().HtmlParts(*args, **kwargs)
    inlined         = self.Inline('Html')
    if self.options.html_include_formatting:
      return ['#'*self.count + ' ' + inlined]
    return [inlined]

#   def Fields(self, html=False):
#     if self.inline and self.count and self.count <= self.options.title_metadata_levels:
#       return { ('title' + str(self.count-1)): ''.join([x.Text(*args, **kwargs) for x in self.inlines]) }
