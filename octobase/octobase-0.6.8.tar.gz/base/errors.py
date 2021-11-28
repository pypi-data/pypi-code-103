#!/opt/local/bin/python
# Copyright 2014, Octoboxy LLC.  All Rights Reserved.


class Error(Exception):
  ''' Useful base class to help explain an exception with its docstring. '''

  def __str__(self):
    prefix      = self.__doc__
    postfix     = super().__str__()
    if postfix:
      return prefix + '\n  ' + postfix
    return prefix



####
## Errors specific to "base"
#

class BaseError(Error):
  ''' Parent class for all exceptions specific to the "base" module. '''


class ControllerNameNotInNamespace(BaseError):
  ''' An item identified with a name not in the Controller namespace. '''

class ControllerNamespaceEmpty(BaseError):
  ''' An object needs to set CONTROLLER_NAMESPACE. '''

class ControllerNonUnity(BaseError):
  ''' More than one Controller claims domain over the same item. '''

class ControllerNotFound(BaseError):
  ''' No Controller wants to respond for the requested item. '''

class ControllerPropertyNotFound(BaseError):
  ''' A Controller can only be instantiated from something that implements ControllerMixin. '''



class EnumAddAfterChoices(BaseError):
  ''' Adding options to an enum after it has provided choices for a model field can lead to loss of data. '''

class EnumDefinitionError(BaseError):
  ''' An Enum definition didn't make sense. '''

class EnumValueNotPresent(BaseError):
  ''' A value could not be found in the enum. '''



class RegisteredObjectNameDuplication(BaseError):
  ''' We can not register the same object more than once. '''

class RegisteredObjectNotAllowedType(BaseError):
  ''' We can not register an object of the type given. '''

class RegisteredObjectNotPresent(BaseError):
  ''' The expected object was not in the registry. '''



class RightDownCantAccumulate(BaseError):
  ''' Can not use option `accumulate_data=True` if a filter fragment was specified during processing. '''

class RightDownFragmentOutOfRange(BaseError):
  ''' The requested fragment was not present in the underlying content. '''

class RightDownFragmentMismatch(BaseError):
  ''' A different fragment was requested than was specified as a filter during processing. '''

class RightDownProcessingError(BaseError):
  ''' The node could not finish processing. '''

class RightDownRenderingError(BaseError):
  ''' The node could not render as requested. '''

class RightDownTagPatternError(BaseError):
  ''' The tag pattern could not be compiled. '''



class TimezoneParsingNotImpl(BaseError):
  ''' We have not yet added timezone-parsing code to our timestamp stripping code, but need it for a filepath. '''

