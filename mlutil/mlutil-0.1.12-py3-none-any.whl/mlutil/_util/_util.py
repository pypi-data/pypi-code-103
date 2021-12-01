import inspect


class SimpleRepr:
    """A mixin implementing a simple __repr__."""

    def __repr__(self):
        sig = inspect.signature(self.__init__)
        default_attrs = {k: v.default for k, v in sig.parameters.items()}
        actual_attrs = self.__dict__
        selected_attrs = {
            k: actual_attrs[k]
            for k, v in default_attrs.items()
            if (k in actual_attrs) and (actual_attrs[k] != v)
        }

        return "{klass}({attrs})".format(
            klass=self.__class__.__name__,
            attrs=", ".join("{}={!r}".format(k, v) for k, v in selected_attrs.items()),
        )
