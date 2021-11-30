from datek_jaipur.domain.compound_types.coin import CoinSet, Coin
from datek_jaipur.domain.constants import COIN_COLLECTION
from datek_jaipur.utils import BaseEvent


class AllCoinSetsCreated(BaseEvent[None, CoinSet]):
    async def _create_result(self) -> CoinSet:
        type_value_tuples = (
            (type_, value)
            for type_, values in COIN_COLLECTION.items()
            for value in values
        )

        i = 0
        result = []
        for type_, value in type_value_tuples:
            result.append(Coin(type_, value, i))
            i += 1

        return CoinSet(result)
