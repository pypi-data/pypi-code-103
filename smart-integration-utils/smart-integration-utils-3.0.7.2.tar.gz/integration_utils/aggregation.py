from json import loads
from django.conf import settings
from rest_framework.exceptions import NotAcceptable, PermissionDenied

from .tools import decode, get_integration_info


def _decode_data(post_data: dict, access_token: str):
    try:
        execute_token = f'{access_token}:{settings.EXECUTE_TOKEN}'
        data = decode(post_data['data'], execute_token)
        return loads(data)
    except:
        raise PermissionDenied('invalid secure params')


class BaseAggregationManager(object):
    def __init__(self, post_data: dict, access_token: str, platform_id: str = 'prod'):
        self.post_data = post_data
        self.access_token = access_token
        self.platform_id = platform_id
        self._data = self._validate_data()

    def _validate_data(self) -> dict:
        data = _decode_data(self.post_data, self.access_token)
        if (
            'integration_id' not in data
            or 'date_from' not in data
            or 'date_to' not in data
        ):
            raise NotAcceptable(
                'invalid params, miss integration_id or date_from or date_to'
            )
        return data

    def _get_calc_step(self) -> str:
        integration_data = get_integration_info(
            self.platform_id, self._data['integration_id'], self.access_token
        )
        calc_step = integration_data.get('calculation', {})
        cost = calc_step['cost'] if calc_step else None
        if cost:
            return cost.replace('{{', '').replace('}}', '')
        return ''

    def _calculate(self, calc_step: str, cost: dict, field: str):
        if calc_step:
            calc_value = eval(calc_step.replace(field, str(cost[f'{field}__sum'])))
            return {'cost__sum': round(calc_value, 2)}
        return {'cost__sum': round(cost[f'{field}__sum'], 2)}

    def aggegation_data(self) -> list:
        raise NotImplementedError('aggregation_data must be implemented')
