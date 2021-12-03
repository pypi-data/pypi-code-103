from abc import ABC, abstractmethod
from datetime import datetime

from .constants import SELECT_QUERY, UPDATE_QUERY, INSERT_QUERY, DELETE_QUERY
from .exceptions import RequiredArgException, ManyPrimaryKeysException, \
    ExtraArgException, NoPrimaryKeysException
from .loader import conn


class Model(ABC):
    @property
    @abstractmethod
    def table_name(self):
        pass

    def _get_class_property_fields(self):
        self._class_property_fields: dict[str, Field] = dict(filter(
            lambda name_and_obj: isinstance(name_and_obj[1], Field),
            self.__class__.__dict__.items()
        ))

    def _get_p_key_name_from_fields(self):
        count_of_primary_keys = 0
        for class_property_field in self._class_property_fields.values():
            if class_property_field._is_primary_key:
                count_of_primary_keys += 1
                if count_of_primary_keys == 2:
                    raise ManyPrimaryKeysException
                self._p_key_name = class_property_field._name
        if count_of_primary_keys == 0:
            raise NoPrimaryKeysException

    def _insert_row(self, **kwargs):
        column_names: list[str] = []
        column_values: list[str] = []
        for kwarg_name, kwarg_value in kwargs.items():
            column_names.append(self._class_property_fields[kwarg_name]._name)
            column_values.append(kwarg_value)
        column_values_wildcards = ['?' for _ in range(len(column_names))]
        insert_query = INSERT_QUERY.format(table=self.table_name,
                                           keys=', '.join(column_names),
                                           values=', '.join(column_values_wildcards))
        conn.execute(insert_query, column_values)

    def _get_last_auto_increment_p_key_value(self) -> int:
        query = f"SELECT {self._p_key_name} FROM {self.table_name} " \
                f"ORDER BY {self._p_key_name} DESC LIMIT 1"
        if value_list := conn.execute(query, []).fetchone():
            return value_list[0]
        return 1

    def _get_p_key_value_from_fields(self, **kwargs):
        for kwarg_name, kwarg_value in kwargs.items():
            if kwarg_name == self._p_key_name:
                self._p_key_value = kwarg_value
                return
        self._p_key_value = self._get_last_auto_increment_p_key_value()

    def __init__(self, **kwargs):
        self._get_class_property_fields()
        self._get_p_key_name_from_fields()
        for class_property_field in self._class_property_fields.values():
            format_kwargs = dict(name=class_property_field._name,
                                 table=self.table_name, p_key=self._p_key_name)
            class_property_field.fetch = SELECT_QUERY.format(**format_kwargs)
            class_property_field.store = UPDATE_QUERY.format(**format_kwargs)
        self._insert_row(**kwargs)
        self.save()
        self._get_p_key_value_from_fields()

    def delete(self):
        delete_query = DELETE_QUERY.format(table=self.table_name,
                                           p_key=self._p_key_name)
        conn.execute(delete_query, [self._p_key_value])

    @staticmethod
    def save():
        conn.commit()


class Field(ABC):
    required_max_length = False
    allowed_auto_increment = False

    def __set_name__(self, owner, name):
        if not hasattr(self, '_name'):
            self._name = name

    def __init__(self, primary_key=False, auto_increment=False,
                 nullable: bool = None, unique: bool = None,
                 max_length: int = None, name_in_db: str = None):
        """
        Create a column for table

        :param primary_key: If equals to True, then
        nullable is False and unique is True automatically
        """
        if max_length is None and self.required_max_length:
            raise RequiredArgException(arg_name='max_length',
                                       class_name=self.__class__.__name__)
        if max_length is not None and not self.required_max_length:
            raise ExtraArgException(arg_name='max_length',
                                    class_name=self.__class__.__name__)
        if name_in_db is not None:
            self._name = name_in_db
        if auto_increment and not self.allowed_auto_increment:
            raise ExtraArgException(arg_name='auto_increment',
                                    class_name=self.__class__.__name__)
        self._max_length = max_length
        self._is_primary_key = primary_key
        if primary_key:
            nullable, unique = False, True
        self._is_nullable: bool = nullable if nullable is not None else True
        self._is_unique: bool = unique if unique is not None else False
        self._auto_increment = auto_increment

    def __get__(self, instance: Model, owner):
        return conn.execute(self.fetch, [instance._p_key_value]).fetchone()[0]

    def __set__(self, instance: Model, value):
        conn.execute(self.store, [value, instance._p_key_value])
        if instance._p_key_name == self._name:
            instance._p_key_value = value


class StringField(Field):
    required_max_length = True


class BooleanField(Field):
    def __get__(self, instance: Model, owner):
        return bool(super().__get__(instance, owner))


class IntegerField(Field):
    allowed_auto_increment = True

    def __get__(self, instance: Model, owner):
        return int(super().__get__(instance, owner))


class DateTimeField(Field):
    def __get__(self, instance: Model, owner):
        return datetime.fromisoformat(super().__get__(instance, owner))
