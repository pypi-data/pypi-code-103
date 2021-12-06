# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.model import fields, ModelView
from trytond.pool import Pool
from trytond.pyson import Eval, Or, Bool
from trytond.transaction import Transaction
from trytond.modules.stock_package.stock import PackageMixin
#from trytond.modules.product import price_digits

from trytond.i18n import gettext
from trytond.exceptions import UserError


class ShipmentCarrierMixin(PackageMixin):
    """
    Mixin class which implements all the fields and methods required for
    getting shipping rates and generating labels
    """
    weight = fields.Function(fields.Float(
            "Weight", digits=(16, Eval('weight_digits', 2)),
            depends=['weight_digits']), 'get_weight')
    weight_uom = fields.Function(fields.Many2One('product.uom',
            'Weight UOM'), 'get_weight_uom')
    weight_digits = fields.Function(fields.Integer('Weight Digits'),
        'on_change_with_weight_digits')
    shipping_instructions = fields.Text(
        'Shipping Instructions', states={
            'readonly': Eval('state').in_(['cancel', 'done']),
        }, depends=['state'])
    carrier_cost_method = fields.Function(
        fields.Char('Carrier Cost Method'),
        "get_carrier_cost_method")

    @classmethod
    def __setup__(cls):
        super().__setup__()
        cls.packages.context = {'carrier': Eval('carrier')}
        cls.packages.depends = ['carrier']
        cls._buttons.update({
                'get_rate': {},
                })
        # Following fields are already there in customer shipment, have
        # them in mixin so other shipment model can also use it.

        #cls.carrier = fields.Many2One('carrier', 'Carrier', states={
        #        'readonly': ~Eval('state').in_(['draft', 'waiting', 'assigned',
        #                'packed']),
        #        },
        #    depends=['state'])
        #cls.cost_currency = fields.Many2One('currency.currency',
        #    'Cost Currency', states={
        #        'invisible': ~Eval('carrier'),
        #        'required': Bool(Eval('carrier')),
        #        'readonly': ~Eval('state').in_(['draft', 'waiting', 'assigned',
        #                'packed']),
        #        }, depends=['carrier', 'state'])
        #cls.cost = fields.Numeric('Cost',
        #    digits=price_digits, states={
        #        'invisible': ~Eval('carrier'),
        #        'readonly': ~Eval('state').in_(['draft', 'waiting', 'assigned',
        #                'packed']),
        #        }, depends=['carrier', 'state'])

    @classmethod
    def get_weight(cls, records, name=None):
        """
        Returns sum of weight associated with each package or
        move line otherwise
        """
        Uom = Pool().get('product.uom')

        res = {}
        for record in records:
            weight_uom = record.weight_uom
            if record.packages:
                res[record.id] = sum([
                    Uom.compute_qty(p.weight_uom, p.weight, weight_uom)
                    for p in record.packages if p.weight
                ])
            else:
                res[record.id] = sum([
                    move.get_weight(weight_uom, silent=True)
                    for move in record.carrier_cost_moves
                ])
        return res

    @fields.depends('weight_uom')
    def on_change_with_weight_digits(self, name=None):
        if self.weight_uom:
            return self.weight_uom.digits
        return 2

    def get_weight_uom(self, name):
        """
        Returns weight uom for the shipment
        """
        ModelData = Pool().get('ir.model.data')
        return ModelData.get_id('product', 'uom_kilogram')

    @classmethod
    def get_carrier_cost_method(cls, records, name):
        res = {}
        for record in records:
            res[record.id] = record.carrier.carrier_cost_method \
                if record.carrier else None
        return res

    @fields.depends("carrier")
    def on_change_with_carrier_cost_method(self, name=None):
        Model = Pool().get(self.__name__)
        return Model.get_carrier_cost_method([self], name)[self.id]

    @property
    def carrier_cost_moves(self):
        "Moves to use for carrier cost calculation"
        return []

    @classmethod
    @ModelView.button_action(
        'stock_package_rate.act_get_rate_wizard')
    def get_rate(cls, shipments):
        pass

    def _create_default_package(self, package_type=None):
        """
        Create a single stock package for the whole shipment
        """
        pool = Pool()
        Package = pool.get('stock.package')
        ModelData = pool.get('ir.model.data')

        values = {
            'shipment': '%s,%d' % (self.__name__, self.id),
            'moves': [('add', self.carrier_cost_moves)],
            }
        if package_type is not None:
            values['type'] = package_type.id
        else:
            default_type = ModelData.get_id(
                'stock_package_rate', 'shipment_package_type')
            values['type'] = default_type
        package, = Package.create([values])
        return package

    def get_shipping_rates(self, carriers=None):
        """
        Gives a list of rates from carriers provided. If no carriers provided,
        return rates from all the carriers.

        List contains dictionary with following minimum keys:
            [
                {
                    'display_name': Name to display,
                    'cost': cost,
                    'cost_currency': currency.currency active repord,
                    'carrier': carrier active record,
                }..
            ]
        """
        Carrier = Pool().get('carrier')

        if carriers is None:
            carriers = Carrier.search([])

        rates = []
        for carrier in carriers:
            rates.extend(
                self.get_shipping_rate(carrier=carrier))
        return rates

    def get_shipping_rate(self, carrier):
        """
        Gives a list of rates from provided carrier and carrier service.

        List contains dictionary with following minimum keys:
            [
                {
                    'display_name': Name to display,
                    'cost': cost,
                    'cost_currency': currency.currency active repord,
                    'carrier': carrier active record,
                }..
            ]
        """
        Company = Pool().get('company.company')

        if carrier.carrier_cost_method == 'product':
            currency = Company(Transaction().context['company']).currency
            rate_dict = {
                'display_name': carrier.rec_name,
                'cost': carrier.carrier_product.list_price,
                'cost_currency': currency,
                'carrier': carrier,
            }
            return [rate_dict]

        return []

    def apply_shipping_rate(self, rate):
        """
        This method applies shipping rate. Rate is a dictionary with
        following minimum keys:

            {
                'display_name': Name to display,
                'cost': cost,
                'cost_currency': currency.currency active repord,
                'carrier': carrier active record,
            }
        """
        Currency = Pool().get('currency.currency')

        shipment_cost = rate['cost_currency'].round(rate['cost'])
        if self.cost_currency != rate['cost_currency']:
            shipment_cost = Currency.compute(
                rate['cost_currency'], shipment_cost, self.cost_currency
            )

        self.cost = shipment_cost
        self.cost_currency = rate['cost_currency']
        self.carrier = rate['carrier']
        self.save()

    @staticmethod
    def default_cost_currency():
        Company = Pool().get('company.company')

        company_id = Transaction().context.get('company')

        return company_id and Company(company_id).currency.id or None

    @property
    def ship_from_address(self):
        return None

    @property
    def ship_to_address(self):
        return None
