"""manages registry of class instances across the package"""
import uuid
import logging
from typing import MutableMapping, List


logger = logging.getLogger(__name__)


class ClassProperty(object):
    def __init__(self, f):
        """
        Decorator for indicating a class property. Only works for getters
        lovingly pilfered from https://stackoverflow.com/a/5192374

        :param f: class function to decorate
        """
        self.f = f

    def __get__(self, obj, owner):
        return self.f(owner)


class InstanceRegistry:
    # registry dictionary for all instances of all subclasses
    _registry: MutableMapping[str, List['InstanceRegistry']] = {}

    # prefix for UUID access
    UUID_PREFIX: str = ''

    def __init__(self):
        """A class for tracking class instances and retrieving them by UUID"""
        # todo create unittests
        self._uuid: str = str(uuid.uuid4())   # create uuid
        # append instance to registry
        # logger.debug(f'appending instance with uuid {self._uuid}')
        if len(self.class_registry) == 0 or not any([self is inst for inst in self.class_registry]):
            self.class_registry.append(self)
            # self._registry[f'{self.__class__.__name__}'].append(self)

    @property
    def uuid(self) -> str:
        """unique identifier for the instance"""
        return self.UUID_PREFIX + self._uuid

    @ClassProperty
    def class_registry(cls):
        """a list of registered instances of the current class"""
        # create if undefined
        if cls.__name__ not in cls._registry:
            logger.debug(f'creating new registry list for {cls.__name__}')
            cls._registry[cls.__name__] = []
        return cls._registry[cls.__name__]

    @staticmethod
    def _match_instance_key(inst: "InstanceRegistry", identifier: str) -> bool:
        """
        Checks the provided identifier key against the instance provided, returning True if matching and False if not

        :param inst: InstanceRegistry instance
        :param identifier: string identifier
        :return: match
        """
        if inst._uuid == identifier:
            return True
        elif inst.uuid == identifier:
            return True
        # todo consider validating against concatenated versions of the uuid
        # todo consider breaking out into a matching class (to add matches easily without overwriting this function)
        return False

    @classmethod
    def class_instance_by_id(cls, identifier: str):
        """
        Retrieves the instance of the current class by UUID

        :param identifier: unique identifier
        :raises NameError: if no matching instance could be found
        :return: registered class instance
        """
        try:
            for inst in cls._registry[cls.__name__]:
                if cls._match_instance_key(inst, identifier) is True:
                    return inst
        except KeyError:  # if there are no registered instances of the class, raise a consistent error
            pass
        raise NameError(f'the uuid "{identifier}" could not be found in the registry of {cls.__name__}')

    @classmethod
    def search_class_for_id(cls, identifier: str, class_name: str):
        """
        Searches the defined class for the uuid provided

        :param identifier: string identifier
        :param class_name: class name to search
        :return: instance
        """
        try:
            for inst in cls._registry[class_name]:
                if cls._match_instance_key(inst, identifier) is True:
                    return inst
        except KeyError:  # if there are no registered instances of the class, raise a consistent error
            pass
        except AttributeError:  # if the match instance searches for undefined attributes, raise a consistent error
            pass
        raise NameError(f'the uuid "{identifier}" could not be found in the registry of {class_name}')

    @classmethod
    def get_instance_by_uuid(cls, identifier: str):
        """
        General retrieval of any registered instance by its uuid.

        :param identifier: string identifier
        :return: instance
        """
        for cls_name in cls._registry:
            try:
                return cls.search_class_for_id(identifier, cls_name)
            except NameError:
                continue
        raise NameError(f'the uuid "{identifier}" could not be matched to any instances in the registry')
