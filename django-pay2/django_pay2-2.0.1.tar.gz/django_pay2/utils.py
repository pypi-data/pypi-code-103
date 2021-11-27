def clear_none(a_dict):
    return {key: value for key, value in a_dict.items() if value is not None}


class MappingFieldsMixin:
    mapping_keys = {}

    def to_internal_value(self, data):
        mapped_data = {
            new_key: data.get(old_key) for new_key, old_key in self.mapping_keys.items()
        }
        return super().to_internal_value(
            {
                **data,
                **mapped_data,
            }
        )


def remove_trivial_zeros(num):
    num = str(num)
    return num.rstrip("0").rstrip(".")


class HmacDefault:
    requires_context = True

    def __call__(self, serializer_field):
        return serializer_field.context["hmac"]

    def __repr__(self):
        return "%s()" % self.__class__.__name__
