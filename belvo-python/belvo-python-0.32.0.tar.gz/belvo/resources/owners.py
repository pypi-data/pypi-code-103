from typing import Dict, List, Union

from belvo.resources.base import Resource


class Owners(Resource):
    endpoint = "/api/owners/"

    def create(
        self,
        link: str,
        *,
        token: str = None,
        save_data: bool = True,
        raise_exception: bool = False,
        **kwargs: Dict,
    ) -> Union[List[Dict], Dict]:

        data = {"link": link, "save_data": save_data}

        if token:
            data.update(token=token)

        return self.session.post(
            self.endpoint, data=data, raise_exception=raise_exception, **kwargs
        )
