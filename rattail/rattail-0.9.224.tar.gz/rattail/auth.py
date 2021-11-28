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
Auth Handler

See also :doc:`rattail-manual:base/handlers/other/auth`.
"""

from __future__ import unicode_literals, absolute_import

import sqlalchemy_continuum as continuum

from rattail.app import GenericHandler


class AuthHandler(GenericHandler):
    """
    Base class and default implementation for auth handlers.
    """

    def authenticate_user(self, session, username, password):
        """
        Try to authenticate the given credentials.  If successful,
        this should return a Rattail ``User`` instance; otherwise
        returns ``None``.
        """
        from rattail.db.auth import authenticate_user

        return authenticate_user(session, username, password)

    def generate_unique_username(self, session, **kwargs):
        """
        Generate a unique username using data from ``kwargs`` as hints.
        """
        model = self.model

        original_username = self.generate_username(session, **kwargs)
        username = original_username

        # only if given a session, can we check for unique username
        if session:
            counter = 1
            while True:
                users = session.query(model.User)\
                               .filter(model.User.username == username)\
                               .count()
                if not users:
                    break
                username = "{}{:02d}".format(original_username, counter)
                counter += 1

        return username

    def generate_username(self, session, **kwargs):
        """
        Generate a unique username using data from ``kwargs`` as hints.
        """
        person = kwargs.get('person')
        if person:
            first = (person.first_name or '').strip().lower()
            last = (person.last_name or '').strip().lower()
            return '{}.{}'.format(first, last)
            
        return 'newuser'

    def make_user(self, **kwargs):
        """
        Make and return a new User instance.
        """
        model = self.model
        session = kwargs.pop('session', None)

        if 'username' not in kwargs:
            kwargs['username'] = self.generate_unique_username(session, **kwargs)

        user = model.User(**kwargs)
        return user

    def grant_permission(self, role, permission):
        """
        Grant a permission to the role.
        """
        if permission not in role.permissions:
            role.permissions.append(permission)

    def revoke_permission(self, role, permission):
        """
        Revoke a permission from the role.
        """
        if permission in role.permissions:
            role.permissions.remove(permission)

    def cache_permissions(self, session, principal,
                          include_guest=True,
                          include_authenticated=True):
        """
        Return a set of permission names, which represents all
        permissions effectively granted to the given principal.

        :param session: A SQLAlchemy session instance.

        :param principal: May be either a
           :class:`~rattail.db.model.users.User` or
           :class:`~rattail.db.model.users.Role` instance.  It is also
           expected that this may sometimes be ``None``, in which case
           the "Guest" role will typically be assumed.

        :param include_guest: Whether or not the "Guest" role should
           be included when checking permissions.  If ``False``, then
           Guest's permissions will *not* be consulted.

        :param include_authenticated: Whether or not the
           "Authenticated" role should be included when checking
           permissions.

        Note that if no ``principal`` is provided, and
        ``include_guest`` is set to ``False``, then no checks will
        actually be done, and the return value will be ``False``.
        """
        from rattail.db.auth import guest_role, authenticated_role

        # we will use any `roles` attribute which may be present.  in practice we
        # would be assuming a User in this case
        if hasattr(principal, 'roles'):

            roles = []
            for role in principal.roles:
                include = False
                if role.node_type:
                    if role.node_type == self.config.node_type():
                        include = True
                else:
                    include = True
                if include:
                    roles.append(role)

            # here our User assumption gets a little more explicit
            if include_authenticated:
                roles.append(authenticated_role(session))

        # otherwise a non-null principal is assumed to be a Role
        elif principal is not None:
            roles = [principal]

        # fallback assumption is "no roles"
        else:
            roles = []

        # maybe include guest roles
        if include_guest:
            roles.append(guest_role(session))

        # build the permissions cache
        cache = set()
        for role in roles:
            cache.update(role.permissions)

        return cache

    def has_permission(self, session, principal, permission,
                       include_guest=True,
                       include_authenticated=True):
        """
        Determine if a principal has been granted a permission.

        Under the hood this really just invokes
        :meth:`cache_permissions()` for the principal, and then checks
        to see if the given permission is included in that set.
        """
        perms = self.cache_permissions(session, principal,
                                       include_guest=include_guest,
                                       include_authenticated=include_authenticated)
        return permission in perms

    def delete_user(self, user, **kwargs):
        """
        Delete the given user account.  Use with caution!  As this
        generally cannot be undone.

        Default behavior here is of course to delete the account, but
        it also must try to "remove" the user association from various
        places, in particular the continuum transactions table.
        Please note that this will leave certain record versions as
        appearing to be "without an author".
        """
        session = self.app.get_session(user)

        # disassociate user from transactions
        self.remove_user_from_continuum_transactions(user)

        # finally, delete the user outright
        session.delete(user)
        return True

    def remove_user_from_continuum_transactions(self, user):
        """
        Remove the given user from all Continuum transactions.
        """
        session = self.app.get_session(user)
        model = self.model

        # remove the user from any continuum transactions
        # nb. we can use "any" model class here, to obtain Transaction
        Transaction = continuum.transaction_class(model.User)
        transactions = session.query(Transaction)\
                              .filter(Transaction.user_id == user.uuid)\
                              .all()
        for txn in transactions:
            txn.user_id = None
