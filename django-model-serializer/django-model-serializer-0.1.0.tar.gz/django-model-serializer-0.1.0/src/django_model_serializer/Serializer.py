import difflib
import inspect
from typing import Tuple
from types import FunctionType
from django.db.models.query import QuerySet
from inflect import engine
from django.core.validators import EMPTY_VALUES


class WarningHandler:
    """
    Showing warnings in console/terminal
    """

    # set color and reset color code
    WARNING = '\033[93m'  # YELLOW
    RESET = '\033[0m'  # RESET COLOR

    def __init__(self):
        # A list for store messages
        self.warning_list = list()

    def add_warning(self, message: str) -> None:
        """Adding warnings to warning_list

        Args:
            message (str)
        """

        # Checking for duplicates
        if message not in self.warning_list:
            self.warning_list.append(message)

    def show_warnings(self) -> None:
        """showing warnings"""
        # printing all messages
        for warning in self.warning_list:
            print(self.WARNING + warning + self.RESET)


# instance of WarningHandler for global use 
warning = WarningHandler()


class DataObject:
    def add_to_obj(self, data: dict):
        for key, value in data.items():
            setattr(self, key, value)


class SerializerObject:
    pass


class Serializer:

    def __init__(
            self,
            instance=None,
            many: bool = False,
            key: str = 'data',
            separate: list = None,
            deep_separate: dict = None,
            transform_functions=None,
            filters=None,
    ):
        """Initialize Serializer 

        Args:
            instance (QuerySet, optional): Instances of Model. Defaults to None.
            many (bool, optional): Defaults to False.
            key (str, optional): Returns data key. Defaults to 'data'.
        """
        pass

    def __new__(cls, *args, **kwargs) -> dict:

        # inflect engine
        __p = engine()

        if cls.__get_attrs(cls, 'Meta') is None:
            raise Exception('Serializer must have a meta class ')

        # get model
        __model = cls.__get_attrs(cls.Meta, 'model')

        # get instances (type:QuerySet)
        __instances = kwargs.get('instance') or None

        # get list of fields 
        __fields = cls.__get_attrs(cls.Meta, 'fields')

        # excepted fields (These fields will be separated from the returned data)
        __except_fields = cls.__get_attrs(cls.Meta, 'except_fields') or []  # this fields not show in data

        # get filters
        __filters = kwargs.get('filters') or cls.__get_attrs(cls.Meta, 'filters')

        # get separate keys
        __separate = kwargs.get('separate')

        # get deep_separate keys
        __deep_separate = kwargs.get('deep_separate')

        # get relations and custom fields
        __relation_fields, __custom_fields = cls.__get_custom_and_relation_fields()

        # get transform functions
        __transform_functions = kwargs.get('transform_functions')

        # get many mode (If it's True, data will be returned in a list, Otherwise data will be a dict)
        __many = kwargs.get('many')

        if type(__many) != bool:
            __many = False

        __key = kwargs.get('key')
        if type(__key) != str:
            __key = 'data'

        # get plural option
        __plural = cls.__get_attrs(cls.Meta, 'plural')

        if type(__plural) != bool:
            __plural = True

        # if instance is one object append to list
        if isinstance(__instances, __model):
            __instances = [__instances]

        # if instance is a QuerySet list, cast to normal list
        if isinstance(__instances, QuerySet):
            __instances = list(__instances)

            # if there is no model, or instance not a normal list
        if __model is None or not isinstance(__instances, list):
            # return empty list
            if not __many:
                return {__key: {}}
            return {__key: []}

        # create all data list
        __all_data = list()

        for instance in __instances:

            # apply filters ----
            skip = cls.__filter_instances(instance, __filters)
            if skip:
                continue

            # all data
            data_obj = DataObject()

            # all Serializer local variable store in serializer_obj
            # for use in custom fields # custom_function(self, data_obj, instance, * serializer_obj *)
            serializer_obj = SerializerObject()

            instance_data = cls.__get_data(instance)
            data_obj.add_to_obj(data=instance_data)

            # Set Related data
            for field in __relation_fields:
                __except_fields.append("%s_id" % field.name)

                relation_field_name = field.field_name or field.name
                if hasattr(instance, field.name):
                    related_field = getattr(instance, field.name)
                    if hasattr(related_field, 'all') and type(
                            getattr(related_field, 'all')() == QuerySet):  # check relation is many to many

                        if __plural:  # plural field name
                            relation_field_name = __p.plural(relation_field_name)
                        related_list = related_field.all()
                        related_data = cls.__get_multi_data(related_list, fields=field.fields,
                                                            excepted_fields=field.except_fields)

                        # set related object to serializer_obj
                        setattr(serializer_obj, field.name, related_list)
                    else:
                        related_data = cls.__get_data(related_field, fields=field.fields,
                                                      excepted_fields=field.except_fields)

                        # set related object to serializer_obj
                        setattr(serializer_obj, field.name, related_field)

                    data_obj.add_to_obj(data={relation_field_name: related_data})

                elif hasattr(instance, '%s_set' % field.name):  # one to many relations
                    if __plural:  # plural field name
                        relation_field_name = __p.plural(relation_field_name)
                    related_field = getattr(instance, '%s_set' % field.name)
                    related_list = related_field.all()
                    setattr(serializer_obj, field.name, related_list)
                    related_data = cls.__get_multi_data(related_list, fields=field.fields,
                                                        excepted_fields=field.except_fields)
                    data_obj.add_to_obj(data={relation_field_name: related_data})

                else:
                    warning.add_warning("The instance does not have a field called '%s'" % field.name)

            # Set Custom Field Data
            for field in __custom_fields:
                custom_field_name = field.field_name or field.name
                if hasattr(cls, field.func_name):

                    # get function from cls
                    func = getattr(cls, field.func_name)

                    try:
                        # add returned value from func to data_obj
                        data_obj.add_to_obj({custom_field_name: func(cls, data_obj, instance, serializer_obj)})
                    except AttributeError as e:
                        warning.add_warning(str(e).replace('DataObject', inspect.getfullargspec(func).args[1]))
                    except Exception as e:
                        warning.add_warning(str(e))
                else:
                    # get all cls function names
                    func_list = [getattr(cls, item).__name__ for item in cls.__dict__ if
                                 isinstance(getattr(cls, item), FunctionType)]

                    # finding closer name with func_name
                    close_match = ' | '.join(difflib.get_close_matches(field.func_name, func_list))

                    warning.add_warning(
                        "%s does not have a function called '%s'. %s"
                        % (
                            cls.__name__,
                            field.func_name,
                            "Do you mean '%s'?" % close_match if len(close_match) > 0 else ''
                        )
                    )

            # run transform functions
            if type(__transform_functions) is list:
                for f in __transform_functions:
                    result = f(data_obj, instance)
                    if type(result) != dict:
                        raise TypeError(
                            "transform functions returns data must be 'dict', but it's '%s'" % type(result).__name__)

                    data_obj.add_to_obj(result)

            instance_data = cls.__get_data(data_obj, fields=__fields, excepted_fields=__except_fields)

            # if instance data is not empty, adding data to __all_data
            if bool(instance_data):

                # separate __separate keys from instance_data
                if __separate is not None:

                    if type(__separate) is not list:  # __separate only can a list
                        raise TypeError('Separates must be a list')

                    for key in __separate:
                        if instance_data.get(key) is not None:
                            instance_data.pop(key)
                        else:
                            warning.add_warning("No data with key '%s' in %s" % (key, cls.__name__))

                # separate __deep_separate keys from instance_data
                if __deep_separate is not None:
                    for key, value in __deep_separate.items():
                        if instance_data.get(key) is not None:
                            for k in value:
                                instance_data.get(key).pop(k)

                __all_data.append(instance_data)

        warning.show_warnings()

        if not __many:
            return {__key: __all_data[-1]}

        return {__key: __all_data}

    @classmethod
    def __get_custom_and_relation_fields(cls) -> Tuple[list, list]:
        """extract custom fields and related fields from class"""
        cls_dict = cls.__dict__
        custom_fields = list()
        relation_fields = list()

        for key, value in cls_dict.items():

            if type(value) == cls.RelationField:
                # update relation field
                setattr(value, 'name', key.lower())
                relation_fields.append(value)

            elif type(value) == cls.CustomField:
                # update custom fields
                setattr(value, 'name', key.lower())
                custom_fields.append(value)

            else:
                # do nothing
                pass

        return relation_fields, custom_fields

    @classmethod
    def __filter_instances(cls, instance, filters):
        """filter instances

        Args:
            instance (object of Model)
            filters (list)

        Returns:
            bool
        """
        result = False
        if filters is None:
            return False

        if type(filters) != list:
            warning.add_warning("filter must be a list")
            return False

        for f in filters:
            f = str(f)
            status = False if f.startswith('!') else True
            name = f if status else f[1:]
            if hasattr(instance, name):
                value = not getattr(instance, name) in EMPTY_VALUES + (False,)
                # print(f"{name}:{value}", f'{f}:{status}')
                if value is not status:
                    result = True

            else:
                # get all cls field names
                fields_list = instance.__dict__.keys()

                # finding closer name with f
                close_match = ' | '.join(difflib.get_close_matches(f, fields_list))
                warning.add_warning(
                    "%s does not have a field called '%s'. %s"
                    % (
                        instance,
                        f,
                        "Do you mean '%s'?" % close_match if len(close_match) > 0 else ''
                    )
                )

        return result

    @classmethod
    def __get_attrs(cls, obj, name) -> any:
        """get attrs from objects

        Args:
            obj (class)
            name (str)

        Returns:
            [attr, None]
        """
        if hasattr(obj, name):
            return getattr(obj, name)
        else:
            return None

    @classmethod
    def __get_multi_data(cls, data_list, fields=[], excepted_fields: list = []) -> list:
        """get multi instance data

        Args:
            data_list (list)
            fields (list, optional): Defaults to [].
            excepted_fields (list, optional): Defaults to [].

        Returns:
            list: list of data
        """
        data = []
        for item in data_list:
            data.append(cls.__get_data(item, fields, excepted_fields))

        return data

    @classmethod
    def __get_data(cls, instance, fields: list = [], excepted_fields: list = []) -> dict:
        """get instance data

        Args:
            instance (instance of Model)
            fields (list, optional): Defaults to [].
            excepted_fields (list, optional): Defaults to [].

        Returns:
            dict: instance data
        """

        if not isinstance(excepted_fields, list):
            if excepted_fields is not None:
                warning.add_warning("excepted_fields only can a list")
            excepted_fields = list()

        excepted_fields.append('_state')
        data = dict()

        for key, value in instance.__dict__.items():
            if key not in excepted_fields:
                if fields == '__all__' or len(fields) == 0:
                    data.update({key: value})
                else:
                    if key in fields:
                        data.update({key: value})

        return data

    class CustomField:
        """Serializer Custom Field"""

        def __init__(self, func_name, field_name=None):
            self.field_name = field_name
            self.func_name = func_name

    class RelationField:
        """Instance Relation Field"""

        def __init__(self, fields='__all__', except_fields: list = [], field_name: str = None):
            self.fields = fields
            self.except_fields = except_fields
            self.field_name = field_name
