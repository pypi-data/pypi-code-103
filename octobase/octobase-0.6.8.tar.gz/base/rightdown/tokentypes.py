#!/usr/bin/env python3
# Copyright 2020, Octoboxy LLC.  All Rights Reserved.
'''
  All patterns -- line, inline, and block -- are defined in this module.
'''

import base
from base import rightdown

from . import patterns
base.utils.ImportCapitalizedNamesFrom(patterns)


###
## Stage 1
#   Line patterns match against entire lines of text


base.Enum.Define(('LINE', 'LineTokenTypes'), (
    { 'name': 'Empty',              'tag': 'empty',       'pattern': ExactPattern('') },
    { 'name': 'Hard Break',         'tag': 'break0',      'pattern': ExactPattern('---') },
    { 'name': 'Soft Break',         'tag': 'break1',      'pattern': RegExPattern(r'\.\s?\.\s?\.') },
    { 'name': 'Blank',              'tag': 'blank',       'pattern': ExactPattern('.') },

    { 'name': 'Slug',               'tag': 'slug',        'pattern': RegExPattern(r'[a-z0-9_]+') },
    { 'name': 'Field',              'tag': 'field',       'pattern': RegExPattern(r'\w+:.*') },
    { 'name': 'Value',              'tag': 'value',       'pattern': PrefixPattern(':') },

    { 'name': 'Heading',            'tag': 'heading',     'pattern': PrefixPattern('#') },
    { 'name': 'Quote',              'tag': 'quote',       'pattern': PrefixPattern('>') },
    { 'name': 'Fence',              'tag': 'fence',       'pattern': PrefixPattern('```') },
    { 'name': 'Table',              'tag': 'table',       'pattern': RegExPattern(r'\|.+\|') },
    { 'name': 'Bullet List',        'tag': 'bullet',      'pattern': RegExPattern(r'[-\*]\s.+') },
    { 'name': 'Number List',        'tag': 'number',      'pattern': RegExPattern(r'\d\.\s.+') },
    { 'name': 'Alpha List',         'tag': 'alpha',       'pattern': RegExPattern(r'[a-zA-Z]\.\s.+') },

    # These are special matches that are defined in code
    { 'name': 'Indented',           'tag': 'indent',      'pattern': IndentedTextPattern() },
    { 'name': 'Almost Indented',    'tag': 'ndent',       'pattern': AlmostIndentedTextPattern() },
    { 'name': 'Paragraph',          'tag': 'paragraph',   'pattern': True },
    { 'name': 'Undefined',          'tag': None },
))

LINE_BREAK_TYPES        = (LINE_HARD_BREAK, LINE_SOFT_BREAK, LINE_BLANK)
LINE_LIST_TYPES         = (LINE_BULLET_LIST, LINE_NUMBER_LIST, LINE_ALPHA_LIST)



###
## Stage 2
#   Block patterns match against sequences of LineToken type tags
#   ONLY TagPatterns should be used in this stage


# Our most sophisticated TagPattern uses long-form syntax to specify a pseudo-YAML block
YAML_TAG_PATTERN    = '''
    break0
    *
      |
        field
          *
            |
              indent
              ndent
        slug
          +
            value
    break1
'''

# As a safety catch, this is what we expect the above to look like if converted to a regular expression
YAML_TAG_PATTERN_REGEXP = '_break0((_field((_indent)|(_ndent))*)|(_slug(_value)+))*_break1'

# All block types, and where possible, the block pattern we match them against
base.Enum.Define(('BLOCK', 'BlockTokenTypes'), (
    # Most important blocks to catch first
    { 'name': 'Fenced Code',        'tag': 'fence',       'pattern': TagPattern('fence,*!fence,fence'), 'html': 'pre' },
    { 'name': 'Pseudo-YAML',        'tag': 'yaml',        'pattern': TagPattern(YAML_TAG_PATTERN) },
    { 'name': 'Hard Break',         'tag': 'break0',      'pattern': TagPattern('break0'),              'html': '<hr>' },

    # General structured blocks
    { 'name': 'Quote',              'tag': 'quote',       'pattern': TagPattern('+quote'),              'html': 'blockquote' },
    { 'name': 'List',               'tag': 'list',        'pattern': TagPattern('bullet|number|alpha,*bullet|number|alpha|indent|ndent') },
    { 'name': 'List Item',          'tag': 'listitem',                                                  'html': 'li' },
    { 'name': 'Field',              'tag': 'field0',      'pattern': TagPattern('field,*indent|ndent') },
    { 'name': 'Multi Field',        'tag': 'field1',      'pattern': TagPattern('paragraph|slug,+value') },
    { 'name': 'Heading',            'tag': 'heading',     'pattern': TagPattern('heading') },

    # Simple blocks
    { 'name': 'Soft Break',         'tag': 'break1',      'pattern': TagPattern('break1'),              'html': '<glyph></glyph>' },
    { 'name': 'Blank',              'tag': 'blank',       'pattern': TagPattern('blank'),               'html': '<p>&nbsp;</p>' },

    # Placeholders we haven't really implemented yet
    { 'name': 'Table',              'tag': 'table',       'pattern': TagPattern('+table') },

    # Patterns to match last
    { 'name': 'Indented Code',      'tag': 'indent',      'pattern': TagPattern('+indent'),             'html': 'pre' },

    # No (meaningful) patterns
    { 'name': 'Paragraph',          'tag': 'paragraph',   'pattern': True,                              'html': 'p' },
    { 'name': 'Fragment',           'tag': 'fragment',                                                  'html': 'section' },
    { 'name': 'Undefined',          'tag': None },
))



###
## Stage 3
#   Inline patterns match against parts of text within a small group of related lines


# These are the actual enums
rightdown.InlineTokenTypesEnum.Define(('INLINE', 'InlineTokenTypes'), (
    { 'name': 'Undefined',          'tag': None },
    { 'name': 'Text',               'tag': 'text',      'pattern': True },
    { 'name': 'Space',              'tag': 'space',     'pattern': InlineWhitespacePattern() },
    # ... populated more below ...
))

base.Enum.Define(('PAIR', 'PairedTokenTypes'), (
    # ... populated automatically ...
))

# We tie them together so that InlineTokenTypes.AddPositions() can populate both enums
InlineTokenTypes.SetPairedTokenTypes(PairedTokenTypes)


# Special types
InlineTokenTypes.AddPositions('Backslash',          'whack',        anywhere='\\')
InlineTokenTypes.AddPositions('Non-Breaking Space', 'nbsp',         anywhere='\\ ',         html='&nbsp;')
InlineTokenTypes.AddPositions('Escaped EoL',        'eol1',         anywhere='\\\n',        html='<br/>')
InlineTokenTypes.AddPositions('Spaced EoL',         'eol2',         anywhere='  \n',        html='<br/>')

# Formatting token pairs
InlineTokenTypes.AddPositions('Star1',              'star1',            open='*',           close='*',        pairhtml='i')
InlineTokenTypes.AddPositions('Star2',              'star2',            open='**',          close='**',       pairhtml='b')
InlineTokenTypes.AddPositions('Star3',              'star3',            open='***',         close='***',      pairhtml=('b', 'i'))
InlineTokenTypes.AddPositions('Underline',          'under',            open='_',           close='_',        pairhtml='u')
InlineTokenTypes.AddPositions('Strikethrough',      'tilde',            open='~',           close='~',        pairhtml='s')
InlineTokenTypes.AddPositions('Hilight',            'equal',            open='=',           close='=',        pairhtml='mark')
InlineTokenTypes.AddPositions('Backtick',           'btick',            open='`',           close='`',        pairhtml='tt')

InlineTokenTypes.AddPositions('Tilde',              'tilde',          middle='~')
InlineTokenTypes.AddPositions('Carrot',             'carrot',         middle='^')

# Link tokens
InlineTokenTypes.AddPositions('Paren',              'paren',            open='(',           close=')')
InlineTokenTypes.AddPositions('Paren2',             'paren2',           open='((',          close='))')
InlineTokenTypes.AddPositions('Square',             'square',           open='[',           close=']')
InlineTokenTypes.AddPositions('Square2',            'square2',          open='[[',          close=']]')
InlineTokenTypes.AddPositions('Exclaim',            'exclaim',          open='!')

InlineTokenTypes.AddPositions('Http Link',          'http',             open='http:')
InlineTokenTypes.AddPositions('Https Link',         'https',            open='https:')
InlineTokenTypes.AddPositions('MailTo Link',        'mailto',           open='mailto:')

# Simple substitutions
InlineTokenTypes.AddPositions('Ellipsis',           'ellipsis',     anywhere='...',         html='…')
InlineTokenTypes.AddPositions('Endash',             'ndash',        anywhere='--',          html='–')   # <-- not an ascii dash
InlineTokenTypes.AddPositions('Emdash',             'mdash',        anywhere='---',         html='—')   # <-- not an ascii dash

InlineTokenTypes.AddPositions('Left Tick',          'ltick',            open="'",           html='‘')
InlineTokenTypes.AddPositions('Right Tick',         'rtick',           close="'",           html='’',         middle="'")
InlineTokenTypes.AddPositions('Left Quote',         'lquote',           open='"',           html='“')
InlineTokenTypes.AddPositions('Right Quote',        'rquote',          close='"',           html='”',         middle='"')

InlineTokenTypes.AddPositions('Copyright',          'copy',          selfish='(c)',         html='©')
InlineTokenTypes.AddPositions('Trademark',          'trade',         selfish='(tm)',        html='™')
InlineTokenTypes.AddPositions('Registered',         'reged',         selfish='(r)',         html='®')
InlineTokenTypes.AddPositions('Plus Minus',         'plusminus',     selfish='+/-',         html='±')
InlineTokenTypes.AddPositions('Not Equal',          'notequal',      selfish='=/=',         html='≠')
InlineTokenTypes.AddPositions('Almost Equal',       'nearequal',     selfish='~=',          html='≈')
InlineTokenTypes.AddPositions('Right Arrow',        'arrowr',        selfish='-->',         html='→')
InlineTokenTypes.AddPositions('Left Arrow',         'arrowl',        selfish='<--',         html='←')
InlineTokenTypes.AddPositions('Bi Arrow',           'arrowrl',       selfish='<-->',        html='↔')
InlineTokenTypes.AddPositions('One Half',           'half',          selfish='1/2',         html='½')
InlineTokenTypes.AddPositions('One Third',          'third',         selfish='1/3',         html='⅓')
InlineTokenTypes.AddPositions('Two Thirds',         '2third',        selfish='2/3',         html='⅔')
InlineTokenTypes.AddPositions('One Quarter',        'quarter',       selfish='1/4',         html='¼')
InlineTokenTypes.AddPositions('Three Quarters',     '3quarter',      selfish='3/4',         html='¾')
InlineTokenTypes.AddPositions('One Fifth',          'fifth',         selfish='1/5',         html='⅕')
InlineTokenTypes.AddPositions('Two Fifths',         '2fifth',        selfish='2/5',         html='⅖')
InlineTokenTypes.AddPositions('Three Fifths',       '3fifth',        selfish='3/5',         html='⅗')
InlineTokenTypes.AddPositions('Four Fifths',        '4fifth',        selfish='4/5',         html='⅘')
InlineTokenTypes.AddPositions('One Sixth',          'sixth',         selfish='1/6',         html='⅙')
InlineTokenTypes.AddPositions('Five Sixths',        '5sixth',        selfish='5/6',         html='⅚')
InlineTokenTypes.AddPositions('One Eighth',         'eighth',        selfish='1/8',         html='⅛')
InlineTokenTypes.AddPositions('Three Eighths',      '3eighth',       selfish='3/8',         html='⅜')
InlineTokenTypes.AddPositions('Five Eigths',        '5eighth',       selfish='5/8',         html='⅝')
InlineTokenTypes.AddPositions('Seven Eights',       '7eighth',       selfish='7/8',         html='⅞')

InlineTokenTypes.AddPositions('First',              'First',        closeish='1st',         html='1<sup><u>st</u></sup>')
InlineTokenTypes.AddPositions('Second',             'Second',       closeish='2nd',         html='2<sup><u>nd</u></sup>')
InlineTokenTypes.AddPositions('Third',              'Third',        closeish='3rd',         html='3<sup><u>rd</u></sup>')
InlineTokenTypes.AddPositions('Fourth',             'Fourth',       closeish='4th',         html='4<sup><u>th</u></sup>')
InlineTokenTypes.AddPositions('Fifth',              'Fifth',        closeish='5th',         html='5<sup><u>th</u></sup>')
InlineTokenTypes.AddPositions('Sixth',              'Sixth',        closeish='6th',         html='6<sup><u>th</u></sup>')
InlineTokenTypes.AddPositions('Seveth',             'Seveth',       closeish='7th',         html='7<sup><u>th</u></sup>')
InlineTokenTypes.AddPositions('Eighth',             'Eighth',       closeish='8th',         html='8<sup><u>th</u></sup>')
InlineTokenTypes.AddPositions('Ninth',              'Ninth',        closeish='9th',         html='9<sup><u>th</u></sup>')
InlineTokenTypes.AddPositions('Tenth',              'Tenth',        closeish='0th',         html='0<sup><u>th</u></sup>')
