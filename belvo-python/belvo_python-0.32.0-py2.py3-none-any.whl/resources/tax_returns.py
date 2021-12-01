from datetime import date
from typing import Dict, List, Optional, Union

from belvo.enums import TaxReturnType
from belvo.resources.base import Resource


class TaxReturns(Resource):
    endpoint = "/api/tax-returns/"

    def create(
        self,
        link: str,
        year_from: str = None,
        year_to: str = None,
        *,
        attach_pdf: bool = False,
        save_data: bool = True,
        raise_exception: bool = False,
        type_: Optional[TaxReturnType] = None,
        date_from: str = None,
        date_to: str = None,
        **kwargs: Dict,
    ) -> Union[List[Dict], Dict]:

        type_ = type_ if type_ else TaxReturnType.YEARLY

        data = {"link": link, "attach_pdf": attach_pdf, "save_data": save_data, "type": type_.value}

        if data["type"] == "yearly":
            year_to = year_to or str(date.today().year)
            data.update(year_to=year_to, year_from=year_from)
        else:
            data.update(date_to=date_to, date_from=date_from)

        return self.session.post(
            self.endpoint, data=data, raise_exception=raise_exception, **kwargs
        )

    def resume(
        self,
        session: str,
        token: str,
        *,
        link: str = None,
        raise_exception: bool = False,
        **kwargs: Dict,
    ) -> Dict:
        raise NotImplementedError()
