# The COPYRIGHT file at the top level of this repository contains the full
# copyright notices and license terms.
from trytond.model import fields, Exclude
from trytond.transaction import Transaction
from trytond.pool import Pool, PoolMeta
from trytond.pyson import Eval, Or, Bool, If
from trytond import backend
from sql.operators import Equal

from trytond.i18n import gettext
from trytond.exceptions import UserError


class Sale(metaclass=PoolMeta):
    __name__ = 'sale.sale'

    #: A many2one field decides to which channel this sale
    #: belongs to. This helps filling lot of default values on sale.
    channel = fields.Many2One(
        'sale.channel', 'Channel', required=True, select=True,
        domain=[
            ('company', '=', Eval('company', -1)),
            ],
        states={
            'readonly': Or(
                (Eval('id', 0) > 0),
                Bool(Eval('lines', [])),
            )
        }, depends=['id', 'company']
    )

    #: Function field which return source of the channel this sale belongs
    #: to.
    channel_type = fields.Function(
        fields.Char('Channel Type'), 'on_change_with_channel_type'
    )

    #: Boolean function field returns true if sale has any exception.
    has_channel_exception = fields.Function(
        fields.Boolean('Has Channel Exception ?'), 'get_has_channel_exception',
        searcher='search_has_channel_exception'
    )

    #: One2Many to channel exception, lists all the exceptions.
    exceptions = fields.One2Many(
        "channel.exception", "origin", "Exceptions"
    )

    # XXX: to identify sale order in external channel
    channel_identifier = fields.Char(
        'Channel Identifier', readonly=True, select=True
    )

    @classmethod
    def __register__(cls, module_name):
        TableHandler = backend.get('TableHandler')
        super().__register__(module_name)
        table = TableHandler(cls, module_name)

        # Migration from 5.2.8: Drop uniq constraint origin_channel_identifier
        table.drop_constraint('origin_channel_identifier')

    @classmethod
    def __setup__(cls):
        super(Sale, cls).__setup__()
        table = cls.__table__()
        cls._sql_constraints += [
            ('channel_identifier_exclude',
                Exclude(table, (table.channel, Equal),
                     (table.channel_identifier, Equal)),
                'sale_channel.msg_channel_identifier_unique'),
            ]

    @classmethod
    def view_attributes(cls):
        return super(Sale, cls).view_attributes() + [
            ('//page[@name="exceptions"]', 'states', {
                    'invisible': Eval('channel_type') == 'manual',
                    })]

    @classmethod
    def search_has_channel_exception(cls, name, clause):
        """
        Returns domain for sale with exceptions
        """
        if clause[2]:
            return [('exceptions.is_resolved', '=', False)]
        else:
            return [
                'OR',
                [('exceptions', '=', None)],
                [('exceptions.is_resolved', '=', True)],
            ]

    def get_channel_exceptions(self, name=None):
        pool = Pool()
        ChannelException = pool.get('channel.exception')

        return list(map(
            int, ChannelException.search([
                ('origin', '=', '%s,%s' % (self.__name__, self.id)),
                ('channel', '=', self.channel.id),
            ], order=[('is_resolved', 'desc')])
        ))

    @classmethod
    def set_channel_exceptions(cls, exceptions, name, value):
        pass

    def get_has_channel_exception(self, name):
        """
        Returs True if sale has exception
        """
        pool = Pool()
        ChannelException = pool.get('channel.exception')

        return bool(
            ChannelException.search([
                ('origin', '=', '%s,%s' % (self.__name__, self.id)),
                ('channel', '=', self.channel.id),
                ('is_resolved', '=', False)
            ])
        )

    @classmethod
    def default_channel(cls):
        pool = Pool()
        User = pool.get('res.user')

        user = User(Transaction().user)
        channel_id = Transaction().context.get('current_channel')
        if channel_id:
            return channel_id
        return user.current_channel and \
            user.current_channel.id  # pragma: nocover

    @staticmethod
    def default_invoice_method():
        pool = Pool()
        Sale = pool.get('sale.sale')
        Channel = pool.get('sale.channel')
        Config = pool.get('sale.configuration')

        channel_id = Sale.default_channel()
        if not channel_id:  # pragma: nocover
            config = Config(1)
            return config.sale_invoice_method

        return Channel(channel_id).invoice_method

    @staticmethod
    def default_shipment_method():
        pool = Pool()
        Sale = pool.get('sale.sale')
        Channel = pool.get('sale.channel')
        Config = pool.get('sale.configuration')

        channel_id = Sale.default_channel()
        if not channel_id:  # pragma: nocover
            config = Config(1)
            return config.sale_invoice_method

        return Channel(channel_id).shipment_method

    @classmethod
    def default_warehouse(cls):
        pool = Pool()
        Sale = pool.get('sale.sale')
        Channel = pool.get('sale.channel')

        warehouse = None
        channel_id = Sale.default_channel()
        if channel_id:
            warehouse = Channel(channel_id).warehouse.id
        if not warehouse:
            warehouse = super().default_warehouse()
        return warehouse

    @classmethod
    def default_payment_term(cls):
        pool = Pool()
        Channel = pool.get('sale.channel')

        payment_term = super(Sale, cls).default_payment_term()
        channel_id = cls.default_channel()
        if channel_id is not None:
            return Channel(channel_id).payment_term.id
        return payment_term

    @fields.depends(
        'channel', 'party', 'currency', 'payment_term', 'warehouse'
    )
    def on_change_channel(self):
        if not self.channel:
            return
        for fname in ('warehouse', 'currency', 'payment_term'):
            setattr(self, fname, getattr(self.channel, fname))

        if self.channel.invoice_method:
            self.invoice_method = self.channel.invoice_method
        if self.channel.shipment_method:
            self.shipment_method = self.channel.shipment_method

    @fields.depends('channel', 'invoice_address', 'payment_term')
    def on_change_party(self):
        super(Sale, self).on_change_party()
        if self.channel:
            if not self.payment_term and self.invoice_address:
                self.payment_term = self.channel.payment_term.id

    @fields.depends('channel')
    def on_change_with_channel_type(self, name=None):
        """
        Returns the source of the channel
        """
        if self.channel:
            return self.channel.source

    @classmethod
    def validate(cls, sales):
        super(Sale, cls).validate(sales)
        for sale in sales:
            sale.check_user_channel()

    def check_user_channel(self):
        '''
        Check if the user has set a channel in preferences
        '''
        pool = Pool()
        User = pool.get('res.user')
        user = User(Transaction().user)

        if (self.channel
                and not self.__class__.default_channel()
                and not Transaction().context.get('skip_check_user_channel')):
            raise UserError(gettext('sale_channel.channel_missing',
                    user.rec_name))
        return True

    @classmethod
    def copy(cls, sales, default=None):
        """
        Duplicating records
        """
        if default is None:
            default = {}

        default['channel_identifier'] = None
        default['exceptions'] = None

        return super(Sale, cls).copy(sales, default=default)

    def process_to_channel_state(self, channel_state):
        """
        Process the sale in tryton based on the state of order
        when its imported from channel.

        :param channel_state: State on external channel the order was imported.
        """
        pool = Pool()
        Sale = pool.get('sale.sale')

        data = self.channel.get_tryton_action(channel_state)

        if self.state == 'draft':
            self.invoice_method = data['invoice_method']
            self.shipment_method = data['shipment_method']
            self.save()

        if data['action'] in ['process_manually', 'process_automatically']:
            if self.state == 'draft':
                Sale.quote([self])
            if self.state == 'quotation':
                Sale.confirm([self])

        if data['action'] == 'process_automatically' and \
                self.state == 'confirmed':
            Sale.process([self])


class SaleLine(metaclass=PoolMeta):
    "Sale Line"
    __name__ = 'sale.line'

    # XXX: to identify sale order item in external channel
    channel_identifier = fields.Char('Channel Identifier', readonly=True)
