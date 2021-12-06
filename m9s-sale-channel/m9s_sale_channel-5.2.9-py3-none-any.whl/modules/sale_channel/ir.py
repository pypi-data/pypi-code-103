# This file is part of Tryton.  The COPYRIGHT file at the top level of
# this repository contains the full copyright notices and license terms.
from trytond.pool import PoolMeta


class Cron(metaclass=PoolMeta):
    __name__ = 'ir.cron'

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.method.selection.extend([
                ('sale.channel|import_products_using_cron',
                    'Import products'),
                ('sale.channel|import_orders_using_cron',
                    'Import orders'),
                ('sale.channel|update_order_status_using_cron',
                    'Update order status'),
                ('sale.channel|export_order_status_using_cron',
                    'Export order status'),
                ('sale.channel|export_product_prices_using_cron',
                    'Export product prices'),
                ('sale.channel|export_inventory_from_cron',
                    'Export inventory'),
                ])
