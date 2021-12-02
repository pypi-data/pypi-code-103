from finjet.dependency import Dependency, get_indentification
from finjet.injecter import Notset, create_injecter
from typing import Any, Callable, NamedTuple, Optional


class Container:
    current: "Container" = None

    def __init__(self) -> None:
        """Container object contains attributes and injecting attributes.
        """
        self.last_current = None
        self.singletons = {}
        self.configuration = None

    def configure(self, configuration: NamedTuple):
        """Configure container object

        Parameters
        ----------
        configuration : NamedTuple
            Solving named dependency from this variable
        """
        self.configuration = configuration
        self.current = self

    def __enter__(self):
        """Set global containers to this container.
        """
        self.last_current = self.__class__.current
        self.__class__.current = self

    def __exit__(self, *args, **kwargs):
        self.__class__.current = self.last_current

    def inject(self, obj: type) -> Callable[[Any], Any]:
        """Injecting dependecies to arguments of input object.

        Parameters
        ----------
        obj : type
            target object

        Returns
        -------
        Callable[[Any], Any]
            Injection result
        """
        injecter = create_injecter(obj)
        inject_fields = {}
        for name, value in injecter.iter_field():
            if isinstance(value, Dependency):
                if hasattr(self.configuration, name):
                    inject_fields[name] = getattr(self.configuration, name)
                else:
                    inject_fields[name] = self.solve_dependency(
                        name, value
                    )
            elif value is Notset:
                pass  # Ignore if notset
            else:
                inject_fields[name] = value

        return injecter.replace_field_values(inject_fields)

    def solve_dependency(self, name: str, value: Dependency) -> Any:
        """Solve hierarchy of depedencies.

        Parameters
        ----------
        name : str
            field name.
        value : Dependency
            value

        Returns
        -------
        Any
            Solved value
        """
        if value.klass_or_func is None:
            # TODO: Add more information if exception
            return getattr(self.configuration, name)

        # Solve dependency
        injecter = create_injecter(value.klass_or_func)

        def _solve_dependency(key: str, value: Any) -> Any:
            if isinstance(value, Dependency):
                return self.solve_dependency(key, value)
            elif callable(value):
                return value()
            elif value is None:
                if hasattr(self.configuration, key):
                    return getattr(self.configuration, key)
                else:
                    raise ValueError(f'Not configurated value: {key}')
            else:
                return value

        # Check positional args from config
        positional_args = []
        keyword_args = {}
        for field_name, field_value in injecter.iter_field():
            if field_value is None:
                positional_args.append(
                    _solve_dependency(field_name, field_value)
                )
            elif field_value is Notset:
                pass
            else:
                keyword_args[field_name] = _solve_dependency(
                    field_name, field_value
                )

        if value.is_singleton:
            cache = self.solve_singleton_cache(
                value, *positional_args, **keyword_args
            )
            if cache is not None:
                return cache
            else:
                result = value.klass_or_func(*positional_args, **keyword_args)
                self.add_singleton(
                    value,
                    result,
                    *positional_args, **keyword_args
                )
        else:
            result = value.klass_or_func(*positional_args, **keyword_args)

        return result

    def solve_singleton_cache(self, dependency: Dependency, *args, **kwargs) -> Optional[Any]:
        """Get singleton cache if exists

        Parameters
        ----------
        dependency : Dependency
            depedency object

        Returns
        -------
        Optional[Any]
            singleton object
        """
        return self.singletons.get(
            get_indentification(dependency, *args, **kwargs)
        )

    def add_singleton(self, dependency: Dependency, result: Any, *args, **kwargs):
        """Add singleton object"""
        self.singletons[
            get_indentification(dependency, *args, **kwargs)
        ] = result
