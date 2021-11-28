# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2021 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Customer Order Views
"""

from __future__ import unicode_literals, absolute_import

import decimal

import six
from sqlalchemy import orm

from rattail.db import model
from rattail.util import pretty_quantity
from rattail.batch import get_batch_handler

from webhelpers2.html import tags, HTML

from tailbone.db import Session
from tailbone.views import MasterView


class CustomerOrderView(MasterView):
    """
    Master view for customer orders
    """
    model_class = model.CustomerOrder
    route_prefix = 'custorders'
    editable = False

    labels = {
        'id': "ID",
        'status_code': "Status",
    }

    grid_columns = [
        'id',
        'customer',
        'person',
        'created',
        'status_code',
    ]

    form_fields = [
        'id',
        'store',
        'customer',
        'person',
        'pending_customer',
        'phone_number',
        'email_address',
        'total_price',
        'status_code',
        'created',
        'created_by',
    ]

    has_rows = True
    model_row_class = model.CustomerOrderItem
    rows_viewable = False

    row_labels = {
        'order_uom': "Order UOM",
    }

    row_grid_columns = [
        'sequence',
        'product_brand',
        'product_description',
        'product_size',
        'order_quantity',
        'order_uom',
        'case_quantity',
        'total_price',
        'status_code',
    ]

    def query(self, session):
        return session.query(model.CustomerOrder)\
                      .options(orm.joinedload(model.CustomerOrder.customer))

    def configure_grid(self, g):
        super(CustomerOrderView, self).configure_grid(g)

        g.set_joiner('customer', lambda q: q.outerjoin(model.Customer))
        g.set_joiner('person', lambda q: q.outerjoin(model.Person))

        g.filters['customer'] = g.make_filter('customer', model.Customer.name,
                                              label="Customer Name",
                                              default_active=True,
                                              default_verb='contains')
        g.filters['person'] = g.make_filter('person', model.Person.display_name,
                                            label="Person Name",
                                            default_active=True,
                                            default_verb='contains')

        g.set_sorter('customer', model.Customer.name)
        g.set_sorter('person', model.Person.display_name)

        g.set_enum('status_code', self.enum.CUSTORDER_STATUS)

        g.set_sort_defaults('created', 'desc')

        g.set_link('id')
        g.set_link('customer')
        g.set_link('person')

    def configure_form(self, f):
        super(CustomerOrderView, self).configure_form(f)

        f.set_readonly('id')

        f.set_renderer('store', self.render_store)
        f.set_renderer('customer', self.render_customer)
        f.set_renderer('person', self.render_person)
        f.set_renderer('pending_customer', self.render_pending_customer)

        f.set_type('total_price', 'currency')

        f.set_enum('status_code', self.enum.CUSTORDER_STATUS)

        f.set_readonly('created')

        f.set_readonly('created_by')
        f.set_renderer('created_by', self.render_user)

    def render_person(self, order, field):
        person = order.person
        if not person:
            return ""
        text = six.text_type(person)
        url = self.request.route_url('people.view', uuid=person.uuid)
        return tags.link_to(text, url)

    def render_pending_customer(self, batch, field):
        pending = batch.pending_customer
        if not pending:
            return
        text = six.text_type(pending)
        url = self.request.route_url('pending_customers.view', uuid=pending.uuid)
        return tags.link_to(text, url)

    def get_row_data(self, order):
        return self.Session.query(model.CustomerOrderItem)\
                           .filter(model.CustomerOrderItem.order == order)

    def get_parent(self, item):
        return item.order

    def make_row_grid_kwargs(self, **kwargs):
        kwargs = super(CustomerOrderView, self).make_row_grid_kwargs(**kwargs)

        assert not kwargs['main_actions']
        kwargs['main_actions'].append(
            self.make_action('view', icon='eye', url=self.row_view_action_url))

        return kwargs

    def row_view_action_url(self, item, i):
        if self.request.has_perm('custorders.items.view'):
            return self.request.route_url('custorders.items.view', uuid=item.uuid)

    def configure_row_grid(self, g):
        super(CustomerOrderView, self).configure_row_grid(g)
        app = self.get_rattail_app()
        handler = app.get_batch_handler(
            'custorder',
            default='rattail.batch.custorder:CustomerOrderBatchHandler')

        g.set_type('case_quantity', 'quantity')
        g.set_type('order_quantity', 'quantity')
        g.set_type('cases_ordered', 'quantity')
        g.set_type('units_ordered', 'quantity')

        if handler.product_price_may_be_questionable():
            g.set_renderer('total_price', self.render_price_with_confirmation)
        else:
            g.set_type('total_price', 'currency')

        g.set_enum('order_uom', self.enum.UNIT_OF_MEASURE)
        g.set_renderer('status_code', self.render_row_status_code)

        g.set_label('sequence', "Seq.")
        g.filters['sequence'].label = "Sequence"
        g.set_label('product_brand', "Brand")
        g.set_label('product_description', "Description")
        g.set_label('product_size', "Size")
        g.set_label('status_code', "Status")

        g.set_sort_defaults('sequence')

        g.set_link('product_brand')
        g.set_link('product_description')

    def render_price_with_confirmation(self, item, field):
        price = getattr(item, field)
        app = self.get_rattail_app()
        text = app.render_currency(price)
        if item.price_needs_confirmation:
            return HTML.tag('span', class_='has-background-warning',
                            c=[text])
        return text

    def render_row_status_code(self, item, field):
        text = self.enum.CUSTORDER_ITEM_STATUS.get(item.status_code,
                                                   six.text_type(item.status_code))
        if item.status_text:
            return HTML.tag('span', title=item.status_text, c=[text])
        return text

    def get_batch_handler(self):
        return get_batch_handler(
            self.rattail_config, 'custorder',
            default='rattail.batch.custorder:CustomerOrderBatchHandler')

    def create(self, form=None, template='create'):
        """
        View for creating a new customer order.  Note that it does so by way of
        maintaining a "new customer order" batch, until the user finally
        submits the order, at which point the batch is converted to a proper
        order.
        """
        self.handler = self.get_batch_handler()
        batch = self.get_current_batch()

        if self.request.method == 'POST':

            # first we check for traditional form post
            action = self.request.POST.get('action')
            post_actions = [
                'start_over_entirely',
                'delete_batch',
            ]
            if action in post_actions:
                return getattr(self, action)(batch)

            # okay then, we'll assume newer JSON-style post params
            data = dict(self.request.json_body)
            action = data.get('action')
            json_actions = [
                'assign_contact',
                'unassign_contact',
                'update_phone_number',
                'update_email_address',
                'update_pending_customer',
                'get_customer_info',
                # 'set_customer_data',
                'get_product_info',
                'get_past_items',
                'add_item',
                'update_item',
                'delete_item',
                'submit_new_order',
            ]
            if action in json_actions:
                result = getattr(self, action)(batch, data)
                return self.json_response(result)

        items = [self.normalize_row(row)
                 for row in batch.active_rows()]

        context = self.get_context_contact(batch)

        context.update({
            'batch': batch,
            'normalized_batch': self.normalize_batch(batch),
            'new_order_requires_customer': self.handler.new_order_requires_customer(),
            'product_price_may_be_questionable': self.handler.product_price_may_be_questionable(),
            'allow_contact_info_choice': self.handler.allow_contact_info_choice(),
            'restrict_contact_info': self.handler.should_restrict_contact_info(),
            'order_items': items,
            'product_key_label': self.rattail_config.product_key_title(),
        })

        return self.render_to_response(template, context)

    def get_current_batch(self):
        user = self.request.user
        if not user:
            raise RuntimeError("this feature requires a user to be logged in")

        try:
            # there should be at most *one* new batch per user
            batch = self.Session.query(model.CustomerOrderBatch)\
                                .filter(model.CustomerOrderBatch.mode == self.enum.CUSTORDER_BATCH_MODE_CREATING)\
                                .filter(model.CustomerOrderBatch.created_by == user)\
                                .filter(model.CustomerOrderBatch.executed == None)\
                                .one()

        except orm.exc.NoResultFound:
            # no batch yet for this user, so make one

            batch = self.handler.make_batch(
                self.Session(), created_by=user,
                mode=self.enum.CUSTORDER_BATCH_MODE_CREATING)
            self.Session.add(batch)
            self.Session.flush()

        return batch

    def start_over_entirely(self, batch):

        # delete pending customer if present
        pending = batch.pending_customer
        if pending:
            batch.pending_customer = None
            self.Session.delete(pending)

        # just delete current batch outright
        # TODO: should use self.handler.do_delete() instead?
        self.Session.delete(batch)
        self.Session.flush()

        # send user back to normal "create" page; a new batch will be generated
        # for them automatically
        route_prefix = self.get_route_prefix()
        url = self.request.route_url('{}.create'.format(route_prefix))
        return self.redirect(url)

    def delete_batch(self, batch):

        # delete pending customer if present
        pending = batch.pending_customer
        if pending:
            batch.pending_customer = None
            self.Session.delete(pending)

        # just delete current batch outright
        # TODO: should use self.handler.do_delete() instead?
        self.Session.delete(batch)
        self.Session.flush()

        # set flash msg just to be more obvious
        self.request.session.flash("New customer order has been deleted.")

        # send user back to customer orders page, w/ no new batch generated
        route_prefix = self.get_route_prefix()
        url = self.request.route_url(route_prefix)
        return self.redirect(url)

    def customer_autocomplete(self):
        """
        Customer autocomplete logic, which invokes the handler.
        """
        self.handler = self.get_batch_handler()
        term = self.request.GET['term']
        return self.handler.customer_autocomplete(self.Session(), term,
                                                  user=self.request.user)

    def person_autocomplete(self):
        """
        Person autocomplete logic, which invokes the handler.
        """
        self.handler = self.get_batch_handler()
        term = self.request.GET['term']
        return self.handler.person_autocomplete(self.Session(), term,
                                                user=self.request.user)

    def get_customer_info(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a customer UUID"}

        customer = self.Session.query(model.Customer).get(uuid)
        if not customer:
            return {'error': "Customer not found"}

        return self.info_for_customer(batch, data, customer)

    def info_for_customer(self, batch, data, customer):

        # most info comes from handler
        info = self.handler.get_customer_info(batch)

        # maybe add profile URL
        if info['person_uuid']:
            if self.request.has_perm('people.view_profile'):
                info['contact_profile_url'] = self.request.route_url(
                    'people.view_profile', uuid=info['person_uuid']),

        return info

    def assign_contact(self, batch, data):
        kwargs = {}

        # this will either be a Person or Customer UUID
        uuid = data['uuid']

        if self.handler.new_order_requires_customer():

            customer = self.Session.query(model.Customer).get(uuid)
            if not customer:
                return {'error': "Customer not found"}
            kwargs['customer'] = customer

        else:

            person = self.Session.query(model.Person).get(uuid)
            if not person:
                return {'error': "Person not found"}
            kwargs['person'] = person

        # invoke handler to assign contact
        try:
            self.handler.assign_contact(batch, **kwargs)
        except ValueError as error:
            return {'error': six.text_type(error)}

        self.Session.flush()
        context = self.get_context_contact(batch)
        context['success'] = True
        return context

    def get_context_contact(self, batch):
        context = {
            'customer_uuid': batch.customer_uuid,
            'person_uuid': batch.person_uuid,
            'phone_number': batch.phone_number,
            'contact_display': batch.contact_name,
            'email_address': batch.email_address,
            'contact_phones': self.handler.get_contact_phones(batch),
            'contact_emails': self.handler.get_contact_emails(batch),
            'contact_notes': self.handler.get_contact_notes(batch),
            'add_phone_number': bool(batch.get_param('add_phone_number')),
            'add_email_address': bool(batch.get_param('add_email_address')),
            'contact_profile_url': None,
            'new_customer_name': None,
            'new_customer_first_name': None,
            'new_customer_last_name': None,
            'new_customer_phone': None,
            'new_customer_email': None,
        }

        pending = batch.pending_customer
        if pending:
            context.update({
                'new_customer_first_name': pending.first_name,
                'new_customer_last_name': pending.last_name,
                'new_customer_name': pending.display_name,
                'new_customer_phone': pending.phone_number,
                'new_customer_email': pending.email_address,
            })

        # figure out if "contact is known" from user's perspective.
        # if we have a uuid then it's definitely known, otherwise if
        # we have a pending customer then it's definitely *not* known,
        # but if no pending customer yet then we can still "assume" it
        # is known, by default, until user specifies otherwise.
        contact = self.handler.get_contact(batch)
        if contact:
            context['contact_is_known'] = True
        else:
            context['contact_is_known'] = not bool(pending)

        # maybe add profile URL
        if batch.person_uuid:
            if self.request.has_perm('people.view_profile'):
                context['contact_profile_url'] = self.request.route_url(
                    'people.view_profile', uuid=batch.person_uuid)

        return context

    def unassign_contact(self, batch, data):
        self.handler.unassign_contact(batch)
        self.Session.flush()
        context = self.get_context_contact(batch)
        context['success'] = True
        return context

    def update_phone_number(self, batch, data):
        app = self.get_rattail_app()

        batch.phone_number = app.format_phone_number(data['phone_number'])

        if data.get('add_phone_number'):
            batch.set_param('add_phone_number', True)
        else:
            batch.clear_param('add_phone_number')

        self.Session.flush()
        return {
            'success': True,
            'phone_number': batch.phone_number,
            'add_phone_number': bool(batch.get_param('add_phone_number')),
        }

    def update_email_address(self, batch, data):

        batch.email_address = data['email_address']

        if data.get('add_email_address'):
            batch.set_param('add_email_address', True)
        else:
            batch.clear_param('add_email_address')

        self.Session.flush()
        return {
            'success': True,
            'email_address': batch.email_address,
            'add_email_address': bool(batch.get_param('add_email_address')),
        }

    def update_pending_customer(self, batch, data):

        try:
            self.handler.update_pending_customer(batch, self.request.user, data)
        except Exception as error:
            return {'error': six.text_type(error)}

        self.Session.flush()
        context = self.get_context_contact(batch)
        context['success'] = True
        return context

    def product_autocomplete(self):
        """
        Custom product autocomplete logic, which invokes the handler.
        """
        term = self.request.GET['term']

        # if handler defines custom autocomplete, use that
        handler = self.get_batch_handler()
        if handler.has_custom_product_autocomplete:
            return handler.custom_product_autocomplete(self.Session(), term,
                                                       user=self.request.user)

        # otherwise we use 'products.neworder' autocomplete
        app = self.get_rattail_app()
        autocomplete = app.get_autocompleter('products.neworder')
        return autocomplete.autocomplete(self.Session(), term)

    def get_product_info(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a product UUID"}

        product = self.Session.query(model.Product).get(uuid)
        if not product:
            return {'error': "Product not found"}

        return self.info_for_product(batch, data, product)

    def uom_choices_for_product(self, product):
        return self.handler.uom_choices_for_product(product)

    def info_for_product(self, batch, data, product):
        try:
            info = self.handler.get_product_info(batch, product)
        except Exception as error:
            return {'error': six.text_type(error)}
        else:
            info['url'] = self.request.route_url('products.view', uuid=info['uuid'])
            return info

    def get_past_items(self, batch, data):
        past_products = self.handler.get_past_products(batch)
        past_items = []

        for product in past_products:
            try:
                item = self.handler.get_product_info(batch, product)
            except:
                # nb. handler may raise error if product is "unsupported"
                pass
            else:
                past_items.append(item)

        return {'past_items': past_items}

    def normalize_batch(self, batch):
        return {
            'uuid': batch.uuid,
            'total_price': six.text_type(batch.total_price or 0),
            'total_price_display': "${:0.2f}".format(batch.total_price or 0),
            'status_code': batch.status_code,
            'status_text': batch.status_text,
        }

    def get_unit_price_display(self, obj):
        """
        Returns a display string for the given object's unit price.
        The object can be either a ``Product`` instance, or a batch
        row.
        """
        app = self.get_rattail_app()
        model = self.model
        if isinstance(obj, model.Product):
            products = app.get_products_handler()
            return products.render_price(obj.regular_price)
        else: # row
            return app.render_currency(obj.unit_price)

    def normalize_row(self, row):
        app = self.get_rattail_app()
        products = app.get_products_handler()

        product = row.product
        department = product.department if product else None
        cost = product.cost if product else None
        data = {
            'uuid': row.uuid,
            'sequence': row.sequence,
            'item_entry': row.item_entry,
            'product_uuid': row.product_uuid,
            'product_upc': six.text_type(row.product_upc or ''),
            'product_upc_pretty': row.product_upc.pretty() if row.product_upc else None,
            'product_brand': row.product_brand,
            'product_description': row.product_description,
            'product_size': row.product_size,
            'product_full_description': product.full_description if product else row.product_description,
            'product_weighed': row.product_weighed,

            'case_quantity': pretty_quantity(row.case_quantity),
            'cases_ordered': pretty_quantity(row.cases_ordered),
            'units_ordered': pretty_quantity(row.units_ordered),
            'order_quantity': pretty_quantity(row.order_quantity),
            'order_uom': row.order_uom,
            'order_uom_choices': self.uom_choices_for_product(product),

            'department_display': department.name if department else None,
            'vendor_display': cost.vendor.name if cost else None,

            'unit_price': six.text_type(row.unit_price) if row.unit_price is not None else None,
            'unit_price_display': self.get_unit_price_display(row),
            'total_price': six.text_type(row.total_price) if row.total_price is not None else None,
            'total_price_display': "${:0.2f}".format(row.total_price) if row.total_price is not None else None,

            'status_code': row.status_code,
            'status_text': row.status_text,
        }

        case_price = self.handler.get_case_price_for_row(row)
        data['case_price'] = six.text_type(case_price) if case_price is not None else None
        data['case_price_display'] = app.render_currency(case_price)

        if self.handler.product_price_may_be_questionable():
            data['price_needs_confirmation'] = row.price_needs_confirmation

        key = self.rattail_config.product_key()
        if key == 'upc':
            data['product_key'] = data['product_upc_pretty']
        else:
            data['product_key'] = getattr(product, key, data['product_upc_pretty'])

        if row.product:
            data.update({
                'product_url': self.request.route_url('products.view', uuid=row.product.uuid),
                'product_image_url': products.get_image_url(row.product),
            })

        unit_uom = self.enum.UNIT_OF_MEASURE_POUND if data['product_weighed'] else self.enum.UNIT_OF_MEASURE_EACH
        if row.order_uom == self.enum.UNIT_OF_MEASURE_CASE:
            if row.case_quantity is None:
                case_qty = unit_qty = '??'
            else:
                case_qty = data['case_quantity']
                unit_qty = pretty_quantity(row.order_quantity * row.case_quantity)
            data.update({
                'order_quantity_display': "{} {} (&times; {} {} = {} {})".format(
                    data['order_quantity'],
                    self.enum.UNIT_OF_MEASURE[self.enum.UNIT_OF_MEASURE_CASE],
                    case_qty,
                    self.enum.UNIT_OF_MEASURE[unit_uom],
                    unit_qty,
                    self.enum.UNIT_OF_MEASURE[unit_uom]),
            })
        else:
            data.update({
                'order_quantity_display': "{} {}".format(
                    pretty_quantity(row.order_quantity),
                    self.enum.UNIT_OF_MEASURE[unit_uom]),
            })

        return data

    def add_item(self, batch, data):
        if data.get('product_is_known'):

            uuid = data.get('product_uuid')
            if not uuid:
                return {'error': "Must specify a product UUID"}

            product = self.Session.query(model.Product).get(uuid)
            if not product:
                return {'error': "Product not found"}

            kwargs = {}
            if self.handler.product_price_may_be_questionable():
                kwargs['price_needs_confirmation'] = data.get('price_needs_confirmation')

            row = self.handler.add_product(batch, product,
                                           decimal.Decimal(data.get('order_quantity') or '0'),
                                           data.get('order_uom'),
                                           **kwargs)
            self.Session.flush()

        else: # product is not known
            raise NotImplementedError # TODO

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def update_item(self, batch, data):
        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        row = self.Session.query(model.CustomerOrderBatchRow).get(uuid)
        if not row:
            return {'error': "Row not found"}

        if row not in batch.active_rows():
            return {'error': "Row is not active for the batch"}

        if data.get('product_is_known'):

            uuid = data.get('product_uuid')
            if not uuid:
                return {'error': "Must specify a product UUID"}

            product = self.Session.query(model.Product).get(uuid)
            if not product:
                return {'error': "Product not found"}

            row.item_entry = product.uuid
            row.product = product
            row.order_quantity = decimal.Decimal(data.get('order_quantity') or '0')
            row.order_uom = data.get('order_uom')

            if self.handler.product_price_may_be_questionable():
                row.price_needs_confirmation = data.get('price_needs_confirmation')

            self.handler.refresh_row(row)
            self.Session.flush()
            self.Session.refresh(row)

        else: # product is not known
            raise NotImplementedError # TODO

        return {'batch': self.normalize_batch(batch),
                'row': self.normalize_row(row)}

    def delete_item(self, batch, data):

        uuid = data.get('uuid')
        if not uuid:
            return {'error': "Must specify a row UUID"}

        row = self.Session.query(model.CustomerOrderBatchRow).get(uuid)
        if not row:
            return {'error': "Row not found"}

        if row not in batch.active_rows():
            return {'error': "Row is not active for this batch"}

        self.handler.do_remove_row(row)
        return {'ok': True,
                'batch': self.normalize_batch(batch)}

    def submit_new_order(self, batch, data):
        try:
            result = self.execute_new_order_batch(batch, data)
        except Exception as error:
            return {'error': six.text_type(error)}
        else:
            if not result:
                return {'error': "Batch failed to execute"}

        next_url = None
        if isinstance(result, model.CustomerOrder):
            next_url = self.get_action_url('view', result)

        return {'ok': True, 'next_url': next_url}

    def execute_new_order_batch(self, batch, data):
        return self.handler.do_execute(batch, self.request.user)

    @classmethod
    def defaults(cls, config):
        cls._order_defaults(config)
        cls._defaults(config)

    @classmethod
    def _order_defaults(cls, config):
        route_prefix = cls.get_route_prefix()
        url_prefix = cls.get_url_prefix()

        # person autocomplete
        config.add_route('{}.person_autocomplete'.format(route_prefix),
                         '{}/person-autocomplete'.format(url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='person_autocomplete',
                        route_name='{}.person_autocomplete'.format(route_prefix),
                        renderer='json',
                        permission='people.list')

        # customer autocomplete
        config.add_route('{}.customer_autocomplete'.format(route_prefix),
                         '{}/customer-autocomplete'.format(url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='customer_autocomplete',
                        route_name='{}.customer_autocomplete'.format(route_prefix),
                        renderer='json',
                        permission='customers.list')

        # custom product autocomplete
        config.add_route('{}.product_autocomplete'.format(route_prefix),
                         '{}/product-autocomplete'.format(url_prefix),
                         request_method='GET')
        config.add_view(cls, attr='product_autocomplete',
                        route_name='{}.product_autocomplete'.format(route_prefix),
                        renderer='json',
                        permission='products.list')


# TODO: deprecate / remove this
CustomerOrdersView = CustomerOrderView


def includeme(config):
    CustomerOrderView.defaults(config)
