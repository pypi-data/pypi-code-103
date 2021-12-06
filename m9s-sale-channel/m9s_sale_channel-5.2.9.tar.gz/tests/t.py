# -*- coding: utf-8 -*-
"""
    tests/test_sale_channel.py

"""
import unittest
from decimal import Decimal
from contextlib import nested

import trytond.tests.test_tryton
from trytond.tests.test_tryton import pool, USER, ModuleTestCase, \
    with_transaction
from trytond.exceptions import UserError
from trytond.transaction import Transaction


class BaseTestCase(unittest.TestCase):
    '''
    Base Test Case sale payment module.
    '''

    def setUp(self):
        """
        Set up data used in the tests.
        this method is called before each test function execution.
        """
        trytond.tests.test_tryton.install_module('sale_channel')

        Currency = pool.get('currency.currency')
        Company = pool.get('company.company')
        Party = pool.get('party.party')
        User = pool.get('res.user')
        Country = pool.get('country.country')
        Subdivision = pool.get('country.subdivision')
        Sale = pool.get('sale.sale')
        SaleLine = pool.get('sale.line')
        SaleChannel = pool.get('sale.channel')
        Location = pool.get('stock.location')
        PriceList = pool.get('product.price_list')
        Payment_Term = pool.get('account.invoice.payment_term')
        Sequence = pool.get('ir.sequence')
        Group = pool.get('res.group')
        ImportDataWizard = pool.get(
            'sale.channel.import_data', type='wizard'
        )

    def _create_product_template(self, name, vlist, uri, uom='Unit'):
        """
        Create a product template with products and return its ID
        :param name: Name of the product
        :param vlist: List of dictionaries of values to create
        :param uri: uri of product template
        :param uom: Note it is the name of UOM (not symbol or code)
        """
        ProductTemplate = pool.get('product.template')
        Uom = pool.get('product.uom')

        for values in vlist:
            values['name'] = name
            values['default_uom'], = Uom.search([('name', '=', uom)], limit=1)
            values['sale_uom'], = Uom.search([('name', '=', uom)], limit=1)
            values['products'] = [('create', [{}])]
        return ProductTemplate.create(vlist)

    def _get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec
        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """
        Account = pool.get('account.account')
        Company = pool.get('company.company')

        if company is None:
            company, = Company.search([], limit=1)

        accounts = Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts[0] if accounts else False

    def _create_coa_minimal(self, company):
        """Create a minimal chart of accounts
        """
        AccountTemplate = pool.get('account.account.template')
        Account = pool.get('account.account')

        account_create_chart = pool.get(
            'account.create_chart', type="wizard")

        account_template, = AccountTemplate.search([
            ('parent', '=', None),
            ('name', '=', 'Minimal Account Chart')
        ])

        session_id, _, _ = account_create_chart.create()
        create_chart = account_create_chart(session_id)
        create_chart.account.account_template = account_template
        create_chart.account.company = company
        create_chart.transition_create_account()

        receivable, = Account.search([
            ('kind', '=', 'receivable'),
            ('company', '=', company),
        ])
        payable, = Account.search([
            ('kind', '=', 'payable'),
            ('company', '=', company),
        ])
        create_chart.properties.company = company
        create_chart.properties.account_receivable = receivable
        create_chart.properties.account_payable = payable
        create_chart.transition_create_properties()

    def get_account_by_kind(self, kind, company=None, silent=True):
        """Returns an account with given spec
        :param kind: receivable/payable/expense/revenue
        :param silent: dont raise error if account is not found
        """
        Account = pool.get('account.account')
        Company = pool.get('company.company')

        if company is None:
            company, = Company.search([], limit=1)

        accounts = Account.search([
            ('kind', '=', kind),
            ('company', '=', company)
        ], limit=1)
        if not accounts and not silent:
            raise Exception("Account not found")
        return accounts and accounts[0].id or None

    def _create_payment_term(self):
        """Create a simple payment term with all advance
        """
        PaymentTerm = pool.get('account.invoice.payment_term')

        return PaymentTerm.create([{
            'name': 'Direct',
            'lines': [('create', [{'type': 'remainder'}])]
        }])

    def setup_defaults(self):
        """Creates default data for testing
        """
        currency, = Currency.create([{
            'name': 'US Dollar',
            'code': 'USD',
            'symbol': '$',
        }])

        # Create a payment term
        payment_term, = _create_payment_term()

        country, = Country.create([{
            'name': 'United States of America',
            'code': 'US',
        }])

        subdivision, = Subdivision.create([{
            'country': country.id,
            'name': 'California',
            'code': 'CA',
            'type': 'state',
        }])

        # Create party
        with Transaction().set_context(company=None):
            company_party, sale_party = Party.create([{
                'name': 'Openlabs',
                'addresses': [('create', [{
                    'name': 'Openlabs',
                    'city': 'Gothom',
                    'country': country.id,
                    'subdivision': subdivision.id,
                }])],
                'customer_payment_term': payment_term.id,
            }, {
                'name': 'John Wick',
                'addresses': [('create', [{
                    'name': 'John Wick',
                    'city': 'Gothom',
                    'country': country.id,
                    'subdivision': subdivision.id,
                }, {
                    'name': 'John Doe',
                    'city': 'Gothom',
                    'country': country.id,
                    'subdivision': subdivision.id,
                }])],
                'customer_payment_term': payment_term.id,
            }])

        company, = Company.create([{
            'party': company_party,
            'currency': currency
        }])

        user = User(USER)
        User.write([user], {
            'company': company,
            'main_company': company,
        })

        sales_user, = User.create([{
            'name': 'Sales Person',
            'login': 'sale',
            'company': company,
            'main_company': company,
            'groups': [('add', [
                Group.search([('name', '=', 'Sales')])[0].id
            ])]
        }])

        price_list = PriceList(
            name='PL 1',
            company=company
        )
        price_list.save()
        _create_coa_minimal(company)

        # Create product templates with products
        template1, = _create_product_template(
            'product-1',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('10'),
                'cost_price': Decimal('5'),
                'account_expense': _get_account_by_kind('expense').id,
                'account_revenue': _get_account_by_kind('revenue').id,
            }],
            uri='product-1',
        )
        template2, = _create_product_template(
            'product-2',
            [{
                'type': 'goods',
                'salable': True,
                'list_price': Decimal('15'),
                'cost_price': Decimal('5'),
                'account_expense': _get_account_by_kind('expense').id,
                'account_revenue': _get_account_by_kind('revenue').id,
            }],
            uri='product-2',
        )
        product1 = template1.products[0]
        product2 = template2.products[0]

        with Transaction().set_context(company=company.id):
            channel1, channel2, channel3, channel4 = \
                SaleChannel.create([{
                    'name': 'Channel 1',
                    'code': 'C1',
                    'address': company_party.addresses[0].id,
                    'source': 'manual',
                    'timezone': 'UTC',
                    'warehouse': Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': payment_term.id,
                    'price_list': price_list,
                }, {
                    'name': 'Channel 2',
                    'code': 'C2',
                    'address': company_party.addresses[0].id,
                    'source': 'manual',
                    'timezone': 'US/Pacific',
                    'warehouse': Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': payment_term.id,
                    'price_list': price_list,
                    'read_users': [('add', [sales_user.id])],
                }, {
                    'name': 'Channel 3',
                    'code': 'C3',
                    'address': company_party.addresses[0].id,
                    'source': 'manual',
                    'warehouse': Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': payment_term.id,
                    'price_list': price_list,
                    'read_users': [('add', [sales_user.id])],
                    'create_users': [('add', [sales_user.id])],
                }, {
                    'name': 'Channel 4',
                    'code': 'C4',
                    'address': company_party.addresses[0].id,
                    'source': 'manual',
                    'timezone': 'US/Eastern',
                    'warehouse': Location.search([
                        ('code', '=', 'WH')
                    ])[0].id,
                    'invoice_method': 'manual',
                    'shipment_method': 'manual',
                    'payment_term': payment_term.id,
                    'price_list': price_list,
                    'read_users': [('add', [sales_user.id])],
                    'create_users': [('add', [sales_user.id])],
                }])

        sales_user.current_channel = channel3
        sales_user.save()
        self.assertTrue(channel3.rec_name in sales_user.status_bar)

        # Save IDs to share between transactions
        sales_user_id = sales_user.id

    def create_sale(self, res_user_id, channel=None):
        """
        Create sale in new transaction
        """
        with nested(
                Transaction().set_user(res_user_id),
                Transaction().set_context(
                    company=company.id, current_channel=channel
                )):
            sale = Sale(
                party=sale_party,
                invoice_address=sale_party.addresses[0],
                shipment_address=sale_party.addresses[0],
                lines=[],
            )
            sale.save()
            sale.on_change_channel()
            self.assertEqual(sale.invoice_method, 'manual')
            if channel:
                self.assertEqual(sale.channel_type, channel.source)
            return sale


class TestSaleChannel(BaseTestCase, ModuleTestCase):
    """
    Test Sale Channel Module
    """
    module = "sale_channel"

    @with_transaction()
    def test_0010_permission_sale_admin(self):
        SALE_ADMIN = USER
        setup_defaults()

        #      USER       Channel1    Channel2    Channel3  Channel4
        #    sale_user       -           R           RW       RW
        #    sale_admin     N/A         N/A         N/A      N/A

        # Creating sale with admin(sale_admin) user
        create_sale(SALE_ADMIN, channel1)
        create_sale(SALE_ADMIN, channel2)
        create_sale(SALE_ADMIN, channel3)
        create_sale(SALE_ADMIN, channel4)

    @with_transaction()
    def test_0020_permission_sale_user(self):
        """
        Cannot create on channel without any permissions
        """
        setup_defaults()

        #      USER       Channel1    Channel2    Channel3  Channel4
        #    sale_user       -           R           RW       RW
        #    sale_admin     N/A         N/A         N/A      N/A

        with self.assertRaises(UserError):
            # Can not create without create_permission
            create_sale(sales_user_id, channel1)

    @with_transaction()
    def test_0030_permission_sale_user(self):
        """
        Cannot create sale on readonly channel
        """
        setup_defaults()

        #      USER       Channel1    Channel2    Channel3  Channel4
        #    sale_user       -           R           RW       RW
        #    sale_admin     N/A         N/A         N/A      N/A

        with self.assertRaises(UserError):
            # Can not create using Read channel
            create_sale(sales_user_id, channel2)

    @with_transaction()
    def test_0040_permission_sale_user(self):
        """
        Ability to read orders in channels the user has access to
        """
        setup_defaults()

        # Create a bunch of orders first
        SALE_ADMIN = USER
        sale1 = create_sale(SALE_ADMIN, channel1)
        sale2 = create_sale(SALE_ADMIN, channel2)
        sale3 = create_sale(SALE_ADMIN, channel3)
        sale4 = create_sale(SALE_ADMIN, channel4)

        #      USER       Channel1    Channel2    Channel3  Channel4
        #    sale_user       -           R           RW       RW
        #    sale_admin     N/A         N/A         N/A      N/A

        with Transaction().set_user(sales_user_id):
            sales = Sale.search([])

            self.assertEqual(len(sales), 3)
            self.assertTrue(sale1 not in sales)  # No Access
            self.assertTrue(sale2 in sales)      # R
            self.assertTrue(sale3 in sales)      # RW
            self.assertTrue(sale4 in sales)      # RW

    @with_transaction()
    def test_0050_permission_sale_user(self):
        """
        Cannot edit sale on channel with no access
        """
        setup_defaults()

        #      USER       Channel1    Channel2    Channel3  Channel4
        #    sale_user       -           R           RW       RW
        #    sale_admin     N/A         N/A         N/A      N/A

        sale1 = create_sale(USER, channel1)

        with self.assertRaises(UserError):
            with Transaction().set_user(sales_user_id):
                sale1 = Sale(sale1.id)
                # Try write on No Access Channel's Sale
                sale1.invoice_address = sale_party.addresses[1]
                sale1.save()

    @with_transaction()
    def test_0060_permission_sale_user(self):
        """
        CAN edit sale on Create/Read channel
        """
        setup_defaults()

        #      USER       Channel1    Channel2    Channel3  Channel4
        #    sale_user       -           R           RW       RW
        #    sale_admin     N/A         N/A         N/A      N/A

        sale2 = create_sale(USER, channel2)
        sale3 = create_sale(USER, channel3)

        with Transaction().set_user(sales_user_id):
            sale2 = Sale(sale2.id)
            sale3 = Sale(sale3.id)

            sale3.invoice_address = sale_party.addresses[1]
            sale3.save()

            self.assertEqual(
                sale3.invoice_address, sale_party.addresses[1]
            )

            sale2.invoice_address = sale_party.addresses[1]
            sale2.save()

    @with_transaction()
    def test_0080_check_create_access(self):
        """
        Check user have access to channel
        """
        SALE_ADMIN = USER
        setup_defaults()

        #      USER       Channel1    Channel2    Channel3  Channel4
        #    sale_user       -           R           RW       RW
        #    sale_admin     N/A         N/A         N/A      N/A

        # Creating sale with admin(sale_admin) user
        sale1 = create_sale(SALE_ADMIN, channel1)
        sale2 = create_sale(SALE_ADMIN, channel2)
        sale3 = create_sale(SALE_ADMIN, channel3)

        with Transaction().set_user(sales_user_id):
            with self.assertRaises(UserError):
                Sale.copy([sale1])

            copy_sale2, = Sale.copy([sale2])
            self.assertNotEqual(copy_sale2, sale2)
            # Assert with sale_users current channel
            self.assertNotEqual(copy_sale2.channel, sale2.channel)
            self.assertEqual(
                copy_sale2.channel, sales_user.current_channel
            )

            copy_sale3, = Sale.copy([sale3])
            self.assertNotEqual(copy_sale3, sale3)
            self.assertEqual(copy_sale3.channel, sale3.channel)

    @with_transaction()
    def test_0090_check_channel_exception(self):
        """
        Check if channel exception is being created
        """
        ChannelException = pool.get('channel.exception')

        setup_defaults()

        sale = create_sale(1, channel1)

        self.assertFalse(sale.has_channel_exception)

        channel_exception, = ChannelException.create([{
            'origin': '%s,%s' % (sale.__name__, sale.id),
            'log': 'Sale has exception',
            'channel': sale.channel.id,
        }])

        self.assertTrue(channel_exception)

        self.assertTrue(sale.has_channel_exception)

        # Mark exception as resolved
        channel_exception.is_resolved = True
        channel_exception.save()

        self.assertFalse(sale.has_channel_exception)

    @with_transaction()
    def test_0095_check_channel_exception_searcher(self):
        """
        Check searcher for channel exception
        """
        ChannelException = pool.get('channel.exception')

        setup_defaults()

        sale1 = create_sale(1, channel1)
        sale2 = create_sale(1, channel1)
        sale3 = create_sale(1, channel1)

        self.assertFalse(sale1.has_channel_exception)
        self.assertFalse(sale2.has_channel_exception)

        self.assertEqual(
            Sale.search([
                ('has_channel_exception', '=', True)
            ], count=True), 0
        )

        self.assertEqual(
            Sale.search([
                ('has_channel_exception', '=', False)
            ], count=True), 3
        )

        ChannelException.create([{
            'origin': '%s,%s' % (sale1.__name__, sale1.id),
            'log': 'Sale has exception',
            'channel': sale1.channel.id,
            'is_resolved': False,
        }])

        ChannelException.create([{
            'origin': '%s,%s' % (sale2.__name__, sale2.id),
            'log': 'Sale has exception',
            'channel': sale2.channel.id,
            'is_resolved': True,
        }])

        self.assertEqual(
            Sale.search([('has_channel_exception', '=', True)]),
            [sale1]
        )

        # Sale2 has exception but is resolved already
        self.assertEqual(
            Sale.search([('has_channel_exception', '=', False)]),
            [sale3, sale2]
        )

    @with_transaction()
    def test_0100_orders_import_wizard(self):
        """
        Check orders import wizard
        """
        setup_defaults()
        with Transaction().set_context(
            active_id=channel1, company=company.id
        ):
            session_id, start_state, end_state = \
                ImportDataWizard.create()
            ImportDataWizard.execute(session_id, {}, start_state)
            import_data = ImportDataWizard(session_id)
            import_data.start.import_orders = True
            import_data.start.import_products = True
            import_data.start.channel = channel1

            # 1. Product / Order is being imported but properties are not
            # set So it will ask for properties first
            self.assertFalse(import_data.get_default_property('revenue'))
            self.assertFalse(import_data.get_default_property('expense'))

            self.assertEqual(import_data.transition_next(), 'properties')

            import_data.properties.account_revenue = \
                get_account_by_kind('revenue')
            import_data.properties.account_expense = \
                get_account_by_kind('expense')
            import_data.properties.company = company.id

            self.assertEqual(
                import_data.transition_create_properties(), 'import_'
            )

            # Properties are created
            self.assertTrue(import_data.get_default_property('revenue'))
            self.assertTrue(import_data.get_default_property('expense'))

            # Since properties are set, it wont ask for properties
            # again
            self.assertEqual(import_data.transition_next(), 'import_')

            with self.assertRaises(NotImplementedError):
                # NotImplementedError is thrown in this case.
                # Importing orders feature is not available in this module
                import_data.transition_import_()

    @with_transaction()
    def test_0200_channel_availability(self):
        StockMove = pool.get('stock.move')
        Location = pool.get('stock.location')

        setup_defaults()

        self.assertEqual(
            channel1.get_availability(product1),
            {'type': 'bucket', 'value': 'out_of_stock'}
        )
        self.assertEqual(
            channel1.get_availability(product2),
            {'type': 'bucket', 'value': 'out_of_stock'}
        )

        lost_and_found, = Location.search([
            ('type', '=', 'lost_found')
        ])
        with Transaction().set_context(company=company.id):
            # Bring in inventory for item 1
            StockMove.create([{
                'from_location': lost_and_found,
                'to_location': channel1.warehouse.storage_location,
                'quantity': 10,
                'product': product1,
                'uom': product1.default_uom,
            }])
        self.assertEqual(
            channel1.get_availability(product1),
            {'type': 'bucket', 'value': 'in_stock'}
        )
        self.assertEqual(
            channel1.get_availability(product2),
            {'type': 'bucket', 'value': 'out_of_stock'}
        )

    @with_transaction()
    def test_0095_check_duplicate_channel_identifier_for_sale(self):
        """
        Check if error is raised for duplicate channel identifier in sale
        """
        setup_defaults()

        sale1 = create_sale(1, channel1)

        sale2 = create_sale(1, channel1)

        sale1.channel_identifier = 'Test Sale 1'
        sale1.save()

        # Put same channel identifer for sale 2, should raise error
        with self.assertRaises(UserError):
            sale2.channel_identifier = 'Test Sale 1'
            sale2.save()

    @with_transaction()
    def test_0100_return_sale_with_channel_identifier(self):
        """
        Check if return sale works with channel_identifier
        """
        ReturnSale = pool.get('sale.return_sale', type='wizard')
        Sale = pool.get('sale.sale')

        setup_defaults()

        # Return sale with channel identifier
        sale1 = create_sale(1, channel1)

        sale1.channel_identifier = 'Test Sale 1'
        sale1.save()

        session_id, _, _ = ReturnSale.create()

        return_sale = ReturnSale(session_id)

        with Transaction().set_context(active_ids=[sale1.id]):
            return_sale.do_return_(return_sale.return_.get_action())

        # Return sale with lines
        sale2 = create_sale(1, channel1)
        sale2.channel_identifier = 'Test Sale 2'
        sale2.save()
        Sale.write([sale2], {
            'lines': [
                ('create', [{
                    'type': 'comment',
                    'channel_identifier': 'Test Sale Line',
                    'description': 'Test Desc'
                }])
            ]
        })

        session_id, _, _ = ReturnSale.create()

        return_sale = ReturnSale(session_id)

        with Transaction().set_context(active_ids=[sale2.id]):
            return_sale.do_return_(return_sale.return_.get_action())

    @with_transaction()
    def test_0110_map_tax(self):
        """
        Check if tax is mapped
        """

        SaleChannel = pool.get('sale.channel')
        SaleChannelTax = pool.get('sale.channel.tax')
        Tax = pool.get('account.tax')

        setup_defaults()

        new_channel, = SaleChannel.create([{
            'name': 'Channel 1',
            'code': 'C1',
            'address': company_party.addresses[0].id,
            'source': 'manual',
            'warehouse': Location.search([
                ('code', '=', 'WH')
            ])[0].id,
            'currency': currency.id,
            'invoice_method': 'manual',
            'shipment_method': 'manual',
            'payment_term': payment_term.id,
            'price_list': price_list,
            'company': company.id,
        }])

        tax1, = Tax.create([
            {
                'name': "tax1",
                'description': "This is description",
                'type': 'percentage',
                'company': company.id,
                'invoice_account': _get_account_by_kind('revenue').id,
                'credit_note_account':
                    _get_account_by_kind('revenue').id,
                'rate': Decimal('8.00'),
            }
        ])

        mapped_tax, = SaleChannelTax.create([{
            'name': 'new_channel_tax',
            'rate': Decimal('8.00'),
            'tax': tax1.id,
            'channel': new_channel.id,
        }])

        self.assertEqual(
            new_channel.get_tax('new_channel_tax', Decimal('8.00')), tax1
        )

    @with_transaction()
    def test_0120_check_channel_exception(self):
        """
        Check that duplication of sale does not duplicate its
        exceptions (irrespective of being resolved or not)
        """
        Sale = pool.get('sale.sale')
        ChannelException = pool.get('channel.exception')

        setup_defaults()

        sale = create_sale(1, channel1)

        self.assertFalse(sale.has_channel_exception)

        # create an exception manually for sake of test
        channel_exception, = ChannelException.create([{
            'origin': '%s,%s' % (sale.__name__, sale.id),
            'log': 'Sale has some dummy exception',
            'channel': sale.channel.id,
        }])

        self.assertTrue(channel_exception)
        self.assertTrue(sale.has_channel_exception)

        duplicate_sale, = Sale.copy([sale])
        self.assertFalse(duplicate_sale.has_channel_exception)


def suite():
    """
    Define Suite
    """
    test_suite = trytond.tests.test_tryton.suite()
    test_suite.addTests(
        unittest.TestLoader().loadTestsFromTestCase(TestSaleChannel)
    )
    return test_suite


if __name__ == '__main__':
    unittest.TextTestRunner(verbosity=2).run(suite())
