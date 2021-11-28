#!/opt/local/bin/python
# Copyright 2015, Octoboxy LLC.  All Rights Reserved.

import base
import json
import string


class Enum:
  ''' ** At a Glance **

      Use the staticmethod Define() to make an enum, like so:

          base.Enum.Define(('MyEnum', 'MyEnums'), (
              'Bare String',                        #  Name
              ('1-Tuple', ),                        # (Name, )
              ('2-Tuple', 'two'),                   # (Name, Tag) -- tag need not be a string
              ('3-Tuple', 'three', 'THREE'),        # (Name, Tag, CodeName)
              ('cat', '4-Tuple', 'four', 'FOUR')    # (Icon, Name, Tag, CodeName)
          ))

      This results in the caller's module getting the following definitions:

          MYENUM_BARE_STRING    = 'B'
          MYENUM_1_TUPLE        = '1'
          MYENUM_2_TUPLE        = 'two'
          MYENUM_THREE          = 'three'
          MYENUM_FOUR           = 'four'            # MyEnum.Definition(MYENUM_FOUR).icon = 'cat'

          MyEnums     = an instance of this class, exposing several useful methods:

              .Definition(value)  Given a tag, name, shortname, or codename, returns an object with
                                        all of those set as properties.
              .Tag(value)           equivalent to MyEnums.Definition(value).tag
              .Name(value)          equivalent to MyEnums.Definition(value).name
              .Icon(value)          equivalent to MyEnums.Definition(value).icon

              .Index(value)         returns the position of the item in the enum
              .Rank(value)          returns a float [0, 1] for the position of the item in the enum

              .Choices()        Returns a list of [(name, tag), ...] as needed for a Django choices= argument
              .MaxTagLength()   Returns an integer of how many chars are needed to hold each tag

              .Definitions()    Returns a dictionary to look OptionDefinition objects up by name
              .Names()          Returns a list of names
              .Tags()           Returns a list of tags

              .__contains__     Enables use of:   'if tag in MyEnums'

              .__iter__         Enables use of:   'for tag in MyEnums'

              .__len__          Enables use of:   'len(MyEnums)'


      ** Use in templates **

        If you pass MyEnums into your template, we're useful even there.  Assuming
        your enum name has no non-Name characters, then in template context:

            MyEnums.name  ==  tag

        If you need more, you can access the full definition as such:

            MyEnums.Definitions.name

      ** Adding to Existing Enums **

            somemodule.MyEnum.Add('5th Option', 5, '5th')
            assert(somemodule.MYENUM_5TH == 5)


      ** Extra Attributes **

        In either Define() or Add(), replace the tuple definition of your option with a dict:

            ('5th Option', 5, '5th')

        is replaced with

            {'name': '5th Option', 'tag': 5, 'codename': '5th', 'my_extra_attr': some_instance}

        Your attribute can be found via Definition():

            assert(MyEnum.Definition(MYENUM_5TH).my_extra_attr == some_instance)


      ** Nested enums **

        Please see filestores.py for a live example.

  '''

  @classmethod
  def Define(klass, name, options, parent=None):
    if isinstance(name, klass.OptionDefinition):
      definition    = name
    else:
      if isinstance(name, str):
        codename    = base.utils.Slugify(name, case=string.ascii_uppercase)
      else:
        codename    = base.utils.Slugify(name[0], case=string.ascii_uppercase)
        name        = name[len(name) > 1 and 1 or 0]
      definition    = klass.OptionDefinition({'name': name, 'tag': None, 'codename': codename}, parent=parent)
    globs           = parent and parent.globs or base.utils.GetGlobalsOfCaller()
    enum            = klass(globs, definition, parent)
    enum.objname    = '.'.join([x for x in (globs.get('__package__'), enum.objname) if x])
    globs[definition.objname] = enum
    for item in options:
      if isinstance(item, dict) or isinstance(item, str):
        enum.Add(item)
      else:
        enum.Add(*item)
    return enum

  def Definition(self, name):
    return self.Definitions()[name]

  def Name(self, name):
    return self.Definition(name).name

  def Tag(self, name):
    return self.Definition(name).tag

  def Icon(self, name):
    return self.Definition(name).icon

  def Index(self, name):
    definition      = self.Definition(name)
    return list(self.by_tag).index(definition.tag)

  def Rank(self, name):
    index           = self.Index(name)
    denom           = self.by_tag and len(self.by_tag) or 1
    if denom > 1:
      denom         -= 1
    return index / denom

  def Definitions(self):
    if not self.resolver:
      self.resolver = self.Resolver(self)
    return self.resolver

  def Names(self):
    return list(self.by_name)

  def Tags(self):
    return list(self.by_tag)

  def Choices(self, filter=None):
    self.choiced    = True
    # We once did a nice thing here to return the whole hierarchy, but it turns out
    # Django filters can't handle a hierarchy and Django form widgets can only handle
    # a hierarchy to a depth of 2, so ultimately we'll just return a flat list here...
    filter          = filter or (lambda x: True)
    return [(x.tag, x.name) for x in self.by_tag.values() if filter(x.tag)]

  def MaxTagLength(self):
    absolute        = max((isinstance(x, str) and len(x) or 1) for x in self.by_tag)
    rounded         = 1
    while rounded < absolute:
      rounded       *= 2
    return rounded

  def SortByName(self):
    ''' Re-sorts our iteration order to be by the name of each item. '''
    items           = list(self.by_name.values())
    items.sort(key=lambda x: x.name)
    self.by_name    = {x.name: x for x in items}
    self.by_tag     = {x.tag:  x for x in items}
    self.resorted   = True

  def SortByTag(self):
    ''' Re-sorts our iteration order to be by the tag of each item. '''
    items           = list(self.by_name.values())
    items.sort(key=lambda x: x.tag)
    self.by_name    = {x.name: x for x in items}
    self.by_tag     = {x.tag:  x for x in items}
    self.resorted   = True


  ###
  ## Nested Enums
  #

  def DefineNested(self, definition, options):
    definition      = self.Add(*definition)
    self.Define(definition, options, parent=self)

  def Expand(self, value):
    ''' Returns a list of all the nested enums that contain the item requested. '''
    tag             = self.Tag(value)
    rets            = []
    def Layer(enum):
      if tag in enum.by_tag:
        rets.append(enum)
        for child in enum.children:
          Layer(child)
    Layer(self)
    return rets

  def Parents(self, value):
    ''' Returns the tags for enum values that are parents of the item requested. '''
    return [x.tag for x in self.Expand(value) if x.tag]


  ###
  ## Mechanics
  #

  class OptionDefinition:
    ''' Class that holds all the metadata for one option in an Enum collection. '''

    def __init__(self, *config, parent=None, **kwargs):
      undefined       = 'undefined'
      self.name       = None
      self.iname      = None
      self.shortname  = None

      self.objname    = None
      self.shortobj   = None

      self.tag        = undefined
      self.shorttag   = undefined

      self.codename   = None
      self.shortcode  = None

      self.icon       = None

      if len(config) == 1:
        if isinstance(config[0], dict):
          for key, val in config[0].items():
            setattr(self, key, val)
        else:
          self.name = config[0]
      elif len(config) == 2:
        self.name, self.tag = config
      elif len(config) == 3:
        self.name, self.tag, self.shortcode = config
      elif len(config) == 4:
        self.icon, self.name, self.tag, self.shortcode = config
      elif not kwargs:
        raise base.errors.EnumDefinitionError('Enum option doesn\'t make sense.', config)

      for arg, val in kwargs.items():
        setattr(self, arg, val)

      if self.name and not self.shortname:
        self.shortname  = self.name
      if self.tag is not undefined and self.shorttag is undefined:
        self.shorttag   = self.tag
      if self.codename and not self.shortcode:
        self.shortcode  = self.codename

      if not self.shortname:
        raise base.errors.EnumDefinitionError('Enum option is underdefined.', config)
      if self.shorttag is undefined:
        self.shorttag   = self.shortname[0]
      if not self.shortcode:
        self.shortcode  = self.shortname

      self.shortcode  = base.utils.Slugify(self.shortcode, case=string.ascii_uppercase)
      shortnames    = self._Collect('shortname', parent, False)
      self.name     = (' • ' * (len(shortnames) - 1)) + ' '.join(shortnames)
      self.iname    = self.shortname.lower()
      self.shortobj = self.shortname.replace(' ', '')
      self.objname  = ''.join(self._Collect('shortobj', parent, True))
      if isinstance(self.tag, str):
        self.tag  = ''.join(self._Collect('shorttag', parent, True))
      self.codename = '_'.join(self._Collect('shortcode', parent, True))

    @property
    def config(self):
      ''' Returns a copy of our property dictionary. '''
      config        = {}
      for key, val in self.__dict__.items():
        if not key.startswith('_'):
          config[key] = val
      return config

    def Copy(self):
      ''' Returns a copy of ourselves. '''
      return type(self)(self.config)

    def _Collect(self, *args):
      return Enum._Collect(self, *args)

  class Resolver:
    ''' Used to look up an OptionDefinition by name. '''

    def __init__(self, enum):
      self.combined = {}
      self.combined.update(enum.by_tag)
      self.combined.update(enum.by_iname)
      self.combined.update(enum.by_codename)
      self.enumname = enum.objname

    def __getitem__(self, item):
      item          = isinstance(item, EnumOption) and item.tag or item
      definition    = self.combined.get(item)
      definition    = definition or isinstance(item, str) and self.combined.get(item.lower())
      if not definition:
        raise base.errors.EnumValueNotPresent('"{!s}" is not a valid option in enum {}'.format(item, self.enumname))
      return definition

  def __init__(self, globs, definition, parent):
    self.globs      = globs
    self.shortname  = parent and definition.shortname or None
    self.shortobj   = definition.shortobj
    self.shorttag   = definition.shorttag
    self.shortcode  = definition.shortcode
    self.tag        = ''.join(self._Collect(self, 'shorttag', parent, True))
    self.objname    = definition.objname
    self.parent     = parent
    self.by_name    = {}
    self.by_iname   = {}
    self.by_tag     = {}
    self.by_codename  = {}
    self.children   = []
    self.resorted   = False
    self.resolver   = None
    self.choiced    = False
    if parent:
      parent.children.append(self)

  def Add(self, *args, **kwargs):
    definition      = self.OptionDefinition(*args, parent=self, **kwargs)
    if definition.iname in self.by_iname:
      raise base.errors.EnumDefinitionError('Enum name is not unique.', self.shortname, definition.name)
    if definition.tag in self.by_tag:
      raise base.errors.EnumDefinitionError('Enum tag is not unique.', self.shortname, definition.tag)
    if definition.codename in self.by_codename:
      raise base.errors.EnumDefinitionError('Enum codename is not unique.', self.shortname, definition.codename)
    if self.choiced:
      raise base.errors.EnumAddAfterChoices(self.objname, definition.codename)
    self.AddDefinition(definition)
    self.globs[definition.codename] = definition.tag
    return definition

  def AddDefinition(self, definition):
    self.by_name[definition.name]           = definition
    self.by_iname[definition.iname]         = definition
    self.by_tag[definition.tag]             = definition
    self.by_codename[definition.codename]   = definition
    if self.parent:
      self.parent.AddDefinition(definition)
    self.resolver   = None

  def __contains__(self, tag):
    try:
      definition    = self.Definition(tag)
      return True
    except base.errors.EnumValueNotPresent:
      return False

  def __getitem__(self, tag):
    # Our __getitem__ kicks in in templates and shadows every method on this
    # class.  We need to un-shadow one of them.
    if tag == 'Definitions':
      return self.Definitions()
    return self.Definition(tag).tag

  def __len__(self):
    return len(self.by_tag)

  def __iter__(self):
    return iter(self.by_tag.keys())

  def __repr__(self):
    return self.objname

  @staticmethod
  def _Collect(zelf, attr, parent, reverse):
    collection    = [getattr(zelf, attr)]
    while parent is not None:
      collection.append(getattr(parent, attr))
      parent      = parent.parent
    collection    = [x for x in collection if x]
    if reverse:
      collection.reverse()
    return collection



class EnumOption:
  ''' Smart object that acts like an enum value but remembers which enum it came from.

      There is nothing in the Enum class itself that ever generates these, but you are
      welcome to instantiate them for your own reasons.  For example, you might define
      a custom Django field that persists enums by tag but returns EnumOptions at runtime.

      EnumOption is defined here, next to Enum, and not in the hypothetical place where
      the custom Django field would exist, because Enum.Resolver has to know what an
      EnumOption is or it can't answer __contains__ tests.
  '''

  def __init__(self, **kwargs):
    self.enum       = None
    self.tag        = None
    base.utils.SetAttrs(self, **kwargs)
    if self.enum:
      self.tag      = self.enum.Tag(self.tag)

  def __eq__(self, other):
    if isinstance(other, EnumOption):
      return (self.enum, self.tag) == (other.enum, other.tag)
    if self.enum and isinstance(other, type(self.tag)):
      return self.tag == other
    return False

  def __lt__(self, other):
    if isinstance(other, EnumOption):
      if self.enum == other.enum:
        return self.index < other.index
    if self.enum and isinstance(other, type(self.tag)):
      return self.index < self.enum.Index(other)
    return False

  def __hash__(self):
    return hash((self.enum and self.enum.objname or '') + '/' + str(self.tag))

  def __str__(self):
    return self.tag

  def __repr__(self):
    a, b            = self.appname, self.codename
    if a and b:
      return '.'.join((a,b))
    if b:
      return b
    return super().__repr__()

  def __len__(self):
    return self.tag and len(self.tag) or 0

  @property
  def definition(self):
    return self.enum and self.enum.Definition(self.tag) or None

  @property
  def name(self):
    return self.enum and self.enum.Name(self.tag) or ''

  @property
  def icon(self):
    return self.enum and self.enum.Icon(self.tag) or ''

  @property
  def index(self):
    return self.enum and self.enum.Index(self.tag) or 0

  @property
  def rank(self):
    return self.enum and self.enum.Rank(self.tag) or 0

  @property
  def appname(self):
    return self.enum and self.enum.objname.split('.')[0] or ''

  @property
  def codename(self):
    return self.enum and self.enum.Definition(self.tag).codename or ''

