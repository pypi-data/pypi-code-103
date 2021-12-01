from typing import Dict, List, Union

from belvo.resources.base import Resource


class Incomes(Resource):
    endpoint = "/api/incomes/"

    def create(
        self,
        link: str,
        *,
        token: str = None,
        save_data: bool = True,
        date_from: str = None,
        date_to: str = None,
        raise_exception: bool = False,
        **kwargs: Dict,
    ) -> Union[List[Dict], Dict]:

        data = {"link": link, "save_data": save_data}

        if date_from:
            data.update(date_from=date_from)
        if date_to:
            data.update(date_to=date_to)
        if token:
            data.update(token=token)

        return self.session.post(
            self.endpoint, data=data, raise_exception=raise_exception, **kwargs
        )
