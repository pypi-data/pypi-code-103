# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from decimal import Decimal

from trytond.pool import PoolMeta, Pool
from trytond.transaction import Transaction


class Carrier(metaclass=PoolMeta):
    __name__ = 'carrier'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        selection = ('api_ups', 'UPS API')
        if selection not in cls.carrier_cost_method.selection:
            cls.carrier_cost_method.selection.append(selection)

    def get_sale_price(self):
        pool = Pool()
        Sale = pool.get('sale.sale')

        if self.carrier_cost_method == 'api_ups':
            sale = Sale(Transaction().context['active_id'])
            return Decimal('0.0'), sale.currency.id
        price, currency_id = super().get_sale_price()

    def get_purchase_price(self):
        pool = Pool()
        Purchase = pool.get('purchase.purchase')

        if self.carrier_cost_method == 'api_ups':
            purchase = Purchase(Transaction().context['active_id'])
            return Decimal('0.0'), purchase.currency.id
        price, currency_id = super().get_purchase_price()
