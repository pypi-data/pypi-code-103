"""A Python implementation of the EMuLSion framework.
(Epidemiologic MUlti-Level SImulatiONs).

Tools aimed at handling state variables, either using a special
dictionary (StateVarDict), or using a special descriptor (StateVar) in
association with a decorator (@statevar).

"""

from   enum                       import Enum
from   functools                  import total_ordering


class StateVarDict(dict):
    """A special dictionary aimed at handling the State Variables of a
    model and providing an attribute-like access syntax.

    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self


@total_ordering
class EmulsionEnum(Enum):
    """Enums used in EMuLSion need some special features. First, they
    provide ordering between items. Second, a comparison with None is
    provided. Other features will be developed soon.

    """
    def __lt__(self, other):
        """Return an order for sorting agents. In this simple method
        the order is defined by sorting classes, then agents IDs.

        """
        return False if other is None or other.__class__ != self.__class__\
          else self.value < other.value

    def __eq__(self, other):
        """Return an order for sorting agents. In this simple method
        the order is defined by sorting classes, then agents IDs.

        """
        return False if other is None or other.__class__ != self.__class__\
          else self.value == other.value

    def __int__(self):
        """Return the int value mapped to this item."""
        return self.value

    def __repr__(self):
        """Return a string representation of the instances of the enumeration,
        hiding associated numerical value.

        """
        return '<%s.%s>' % (self.__class__.__name__, self.name)

    def __hash__(self):
        return self.value



# class StateVar(object):
#     """The StateVar class is aimed at reproducing the same features as
#     the native python properties, in order to provide a generic
#     interface to the state variables of an entity (agent or
#     environment). It is thus recommended that entity classes
#     explicitly define getters with the @statevar decorator (and
#     possibly setters) for all their state variables, and that the
#     computation primitives use those state variables to modify the
#     state of the entity, instead of using instance attributes.

#     It is also highly recommended to put the documentation of the
#     state variable in the getter function. Thus the documentation on
#     the state variable can be obtained through
#     `str(MyAgentClass.myvariable)`.

#     """
#     def __init__(self,
#                  fget=None,
#                  fset=None,
#                  fdel=None,
#                  doc=None,
#                  name=None):
#         """Initialize the state variable with the specified getter,
#         setter and deleter functions, with a documentation if
#         given.

#         """
#         self.fget = fget
#         self.fset = fset
#         self.fdel = fdel
#         self.__doc__ = doc
#         self.__name__ = name

#     def __get__(self, obj, objtype=None):
#         if obj is None:
#             return self
#         if self.fget is None:
#             raise AttributeError("unreadable attribute")
#         return self.fget(obj)

#     def __set__(self, obj, value):
#         if self.fset is None:
#             raise AttributeError("can't set attribute")
#         self.fset(obj, value)

#     ### maybe to suppress for safety reasons ???
#     def __delete__(self, obj):
#         if self.fdel is None:
#             raise AttributeError("can't delete attribute")
#         self.fdel(obj)

#     def getter(self, func):
#         """Used to build a decorator to specify or change the getter
#         function of the state variable.

#         """
#         self.fget = func
#         self.__doc__ = func.__doc__
#         self.__name__ = func.__name__
#         return self

#     def setter(self, func):
#         """Used to build a decorator to specify or change the setter
#         function of the state variable.

#         """
#         self.fset = func
#         return self

#     def deleter(self, func):
#         """Used to build a decorator to specify or change the deleter
#         function of the state variable.

#         """
#         self.fdel = func
#         return self

#     def __str__(self):
#         return "{}.\n\t{}".format(self.__name__, self.__doc__)

#     def __repr__(self):
#         return self.__name__


# # ASSOCIATED DECORATORS
# def statevar(func):
#     """Decorator aimed at declaring a local state variable through its
#     getter.

#     Example:
#     --------
#     ``
#     class Cow(object):
#         def __init__(self):
#             self._age = 0

#         @statevar
#         def age(self):
#             '''The age of the cow (in weeks)'''
#             return self._age
#         @age.setter
#         def age(self, value):
#             self._age = value

#         # then a calculus involving the age
#         def grow(self):
#             self.age += 1
#     ``
#     """
#     return StateVar(fget=func,
#                     doc=func.__doc__,
#                     name=func.__name__)



# def build_accessors(cls, statevar, attribute):
#     """Automatically provide accessors for the specified state
#     variable in the class, based on access to the specified
#     attribute. Useful when no special control is needed for
#     getting/setting state variables.

#     Example:
#     --------
#     ``
#     class Cow(object):
#         def __init__(self):
#             self._age = 0

#     build_accessors(Cow, 'age', '_age')
#     c = Cow()
#     c.age += 10
#     print(c.age)
#     ``
#     > 10

#     """
#     def _var_getter(self):
#         return getattr(self, attribute)

#     def _var_setter(self, value):
#         return setattr(self, attribute, value)

#     svar = StateVar(fget=_var_getter,
#                     fset=_var_setter,
#                     name=statevar,
#                     doc="""State variable {} (with automatic accessors).""".format(statevar))
#     setattr(cls, statevar, svar)
