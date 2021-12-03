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
Products Handler
"""

from __future__ import unicode_literals, absolute_import

import six
import sqlalchemy as sa
from sqlalchemy import orm

from rattail import pod
from rattail.util import load_object
from rattail.app import GenericHandler
from rattail.gpc import GPC
from rattail.barcodes import upce_to_upca


class ProductsHandler(GenericHandler):
    """
    Base class and default implementation for product handlers.

    A products handler of course should get the final say in how products are
    handled.  This means everything from pricing, to whether or not a
    particular product can be deleted, etc.
    """

    def find_products_by_key(self, session, value, **kwargs):
        """
        Locate any products where the "key" matches the given value.

        By default this search is as "thorough" as possible and may
        return multiple results in some cases where you might not
        expect them.  Please pass the :param:`only` param if you need
        a more focused search etc.

        :param session: Session for the Rattail database.

        :param value: Value to search for.  Can be a GPC object or
           string.

        :param only: You can optionally direct the logic to search
           only for certain types of keys, by passing a list here,
           e.g.  ``['upc', 'sku']``, or can just pass a single string
           (e.g. ``'upc'``) if only one key is needed.  Otherwise by
           default the logic will search for "all" possible keys.

        :param vendor: You can optionally specify a Vendor, if your
           search needs to include a SKU lookup.  Only matches for
           that vendor will be returned.  Note that by default there
           is no vendor which means "any" SKU might match.

        :param include_keys: You can optionally request that the
           return value include indications of which key was matched,
           for each product result.

        :returns: If :param:`include_keys` is true, then will return a
           list of 2-tuples representing each match.  The first
           element of the tuple will be the "key" field pseudonym
           which was matched on; the second element will be the
           product.

           But if ``include_keys`` is false, then will return just a
           simple list of the products, i.e. won't include the keys.

           Either way of course the list might be empty.
        """
        from rattail.db.api.products import (get_product_by_upc,
                                             get_product_by_item_id,
                                             get_product_by_scancode,
                                             get_product_by_code,
                                             get_product_by_vendor_code)

        model = self.model
        only = kwargs.get('only')
        if isinstance(only, six.string_types):
            only = [only]
        vendor = kwargs.get('vendor')
        include_keys = kwargs.get('include_keys', False)
        products = []

        # don't bother if we're given empty value
        if not value:
            return products

        # TODO: most of the function calls below are only good for "at
        # most one" result.  in some cases there may be more than one
        # match in fact, which will raise an error.  need to refactor
        # somehow to account for that..for now just pass `only` param
        # to avoid the problematic keys for your situation.

        # maybe look for 'uuid' match
        if not only or 'uuid' in only:
            product = session.query(model.Product).get(value)
            if product:
                products.append(('uuid', product))

        # maybe look for 'upc' match
        if not only or 'upc' in only:

            # if value is a GPC we kind of only have one thing to try
            if isinstance(value, GPC):
                product = get_product_by_upc(session, value)
                if product:
                    products.append(('upc', product))

            else: # not GPC, so must convert

                if value.isdigit():

                    # we first assume the value *does* include check digit
                    provided = GPC(value, calc_check_digit=False)
                    product = get_product_by_upc(session, provided)
                    if product:
                        products.append(('upc', product))

                    # but we can also calculate a check digit and try that
                    checked = GPC(value, calc_check_digit='upc')
                    product = get_product_by_upc(session, checked)
                    if product:
                        products.append(('upc', product))

                    # one last trick is to expand UPC-E to UPC-A and then reattempt
                    # the lookup, *with* check digit (since it would be known)
                    if len(value) in (6, 8):
                        checked = GPC(upce_to_upca(value), calc_check_digit='upc')
                        product = get_product_by_upc(session, checked)
                        if product:
                            products.append(('upc', product))

        # maybe look for 'item_id' match
        if not only or 'item_id' in only:
            product = get_product_by_item_id(session, value)
            if product:
                products.append(('item_id', product))

        # maybe look for 'scancode' match
        if not only or 'scancode' in only:
            product = get_product_by_scancode(session, value)
            if product:
                products.append(('scancode', product))

        # maybe look for 'altcode' match
        if not only or 'altcode' in only:
            product = get_product_by_code(session, value)
            if product:
                products.append(('altcode', product))

        # maybe look for 'sku' match
        if not only or 'sku' in only:
            product = get_product_by_vendor_code(session, value,
                                                 vendor=vendor)
            if product:
                products.append(('sku', product))

        # maybe strip keys out of the result
        if not include_keys:
            products = [tup[1] for tup in products]

        return products

    def get_url(self, product, **kwargs):
        """
        Return the Tailbone "view" URL for the given product.
        """
        base_url = self.config.base_url()
        if base_url:
            return '{}/products/{}'.format(base_url, product.uuid)

    def get_image_url(self, product=None, upc=None, **kwargs):
        """
        Return the preferred image URL for the given UPC or product.
        """
        base_url = self.config.base_url()

        # we prefer the "image on file" if available
        if base_url and product and product.image:
            return '{}/products/{}/image'.format(base_url, product.uuid)

        # and if this product is a pack item, then we prefer the unit
        # item image as fallback, if available
        if base_url and product and product.is_pack_item():
            unit = product.unit
            if unit and unit.image:
                return '{}/products/{}/image'.format(base_url, unit.uuid)

        # fallback to the POD image, if available and so configured
        if self.config.getbool('tailbone', 'products.show_pod_image',
                               default=False):
            if product and not upc:
                upc = product.upc
            if upc:
                return self.get_pod_image_url(upc)

        if base_url:
            return '{}/tailbone/img/product.png'.format(base_url)

    def get_pod_image_url(self, upc, **kwargs):
        """
        Return the POD image URL for the given UPC.
        """
        if upc:
            return pod.get_image_url(self.config, upc)

    def render_price(self, price, html=False, **kwargs):
        """
        Render the given ``price`` object as text.

        :returns: String containing the rendered price, or ``None`` if
           nothing was applicable.
        """
        if price.price is not None and price.pack_price is not None:
            if price.multiple > 1:
                return "{} / {}  ({} / {})".format(
                    self.app.render_currency(price.price),
                    price.multiple,
                    self.app.render_currency(price.pack_price),
                    price.pack_multiple)
            return "{}  ({} / {})".format(
                self.app.render_currency(price.price),
                self.app.render_currency(price.pack_price),
                price.pack_multiple)
        if price.price is not None:
            if price.multiple is not None and price.multiple > 1:
                return "{} / {}".format(
                    self.app.render_currency(price.price),
                    price.multiple)
            return self.app.render_currency(price.price)
        if price.pack_price is not None:
            return "{} / {}".format(
                self.app.render_currency(price.pack_price),
                price.pack_multiple)

    def get_uom_sil_codes(self, session, uppercase=False, **kwargs):
        """
        This should return a dict, keys of which are UOM abbreviation strings,
        and values of which are corresponding SIL code strings.

        :param session: Reference to current Rattail DB session.
        :param uppercase: Set to ``True`` to cause all UOM abbreviations to be
           upper-cased when adding to the map.
        :returns: Dictionary containing all known UOM / SIL code mappings.
        """
        model = self.model

        def normalize(uom):
            if uom.sil_code:
                return uom.sil_code

        def make_key(uom, normal):
            key = uom.abbreviation
            if uppercase:
                key = key.upper()
            return key

        return self.cache_model(session, model.UnitOfMeasure,
                                normalizer=normalize,
                                key=make_key)

    def get_uom_sil_code(self, session, uom, uppercase=False, **kwargs):
        """
        This should return a SIL code which corresponds to the given UOM
        abbreviation string.  Useful when you just need one out of the blue,
        but if you need multiple codes looked up then you're probably better
        off using :meth:`get_uom_sil_codes()` for efficiency.

        :param session: Reference to current Rattail DB session.
        :param uppercase: Set to ``True`` to cause the UOM abbreviation to be
           upper-cased before performing the lookup.  This effectively makes
           the search case-insensitive.
        :param uom:  Unit of measure as abbreviated string, e.g. ``'LB'``.
        :returns: SIL code for the UOM, as string (e.g. ``'49'``), or ``None``
           if no matching code was found.
        """
        model = self.model
        query = session.query(model.UnitOfMeasure)
        if uppercase:
            query = query.filter(sa.func.upper(model.UnitOfMeasure.abbreviation) == uom.upper())
        else:
            query = query.filter(model.UnitOfMeasure.abbreviation == uom)
        try:
            match = query.one()
        except orm.exc.NoResultFound:
            pass
        else:
            return match.sil_code

    def collect_wild_uoms(self, **kwargs):
        """
        Collect all UOM abbreviations "from the wild" and ensure each is
        represented within the Rattail Units of Measure table.

        Note that you should not need to override this method.  Please override
        :meth:`find_wild_uoms()` instead.
        """
        session = self.make_session()
        model = self.model

        wild_uoms = self.find_wild_uoms(session, **kwargs)

        known_uoms = self.cache_model(session, model.UnitOfMeasure,
                                      key='abbreviation')

        for wild_uom in wild_uoms:
            if wild_uom not in known_uoms:
                uom = model.UnitOfMeasure()
                uom.abbreviation = wild_uom
                session.add(uom)

        session.commit()
        session.close()

    def find_wild_uoms(self, session, **kwargs):
        """
        Query some database(s) in order to discover all UOM abbreviations which
        exist "in the wild".

        You are encouraged to override this method as needed.  Note that
        certain POS integration packages may provide some common logic which
        may be used for this.

        :param session: Reference to current Rattail DB session.

        :returns: A list of strings, e.g. ``['OZ', 'LB', ...]``.
        """
        return []


def get_products_handler(config, **kwargs):
    """
    Create and return the configured :class:`ProductsHandler` instance.
    """
    spec = config.get('rattail', 'products.handler')
    if spec:
        factory = load_object(spec)
    else:
        factory = ProductsHandler
    return factory(config, **kwargs)
