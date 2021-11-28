from typing import Union


from MSApi.ObjectMS import ObjectMS, check_init


class Attribute(ObjectMS):

    @check_init
    def get_value(self) -> Union[str]:
        return self._json.get('value')
