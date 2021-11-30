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
DataSync Views
"""

from __future__ import unicode_literals, absolute_import

import getpass
import subprocess
import logging

from rattail.db import model
from rattail.datasync.config import load_profiles
from rattail.datasync.util import get_lastrun, purge_datasync_settings

from tailbone.views import MasterView
from tailbone.util import csrf_token


log = logging.getLogger(__name__)


class DataSyncChangeView(MasterView):
    """
    Master view for the DataSyncChange model.
    """
    model_class = model.DataSyncChange
    url_prefix = '/datasync/changes'
    permission_prefix = 'datasync'
    creatable = False
    editable = False
    bulk_deletable = True

    labels = {
        'batch_id': "Batch ID",
    }

    grid_columns = [
        'source',
        'batch_id',
        'batch_sequence',
        'payload_type',
        'payload_key',
        'deletion',
        'obtained',
        'consumer',
    ]

    def configure_grid(self, g):
        super(DataSyncChangeView, self).configure_grid(g)

        # batch_sequence
        g.set_label('batch_sequence', "Batch Seq.")
        g.filters['batch_sequence'].label = "Batch Sequence"

        g.set_sort_defaults('obtained')
        g.set_type('obtained', 'datetime')

    def template_kwargs_index(self, **kwargs):
        kwargs['allow_filemon_restart'] = bool(self.rattail_config.get('tailbone', 'filemon.restart'))
        return kwargs

    def restart(self):
        cmd = self.rattail_config.getlist('tailbone', 'datasync.restart',
                                          # nb. simulate by default
                                          default='/bin/sleep 3')
        log.debug("attempting datasync restart with command: %s", cmd)
        result = subprocess.call(cmd)
        if result == 0:
            self.request.session.flash("DataSync daemon has been restarted.")
        else:
            self.request.session.flash("DataSync daemon could not be restarted; result was: {}".format(result), 'error')
        return self.redirect(self.request.get_referrer(default=self.request.route_url('datasyncchanges')))

    def configure(self):
        """
        View for configuring the DataSync daemon.
        """
        if self.request.method == 'POST':
            # if self.request.is_xhr and not self.request.POST:
            if self.request.POST.get('purge_settings'):
                self.delete_settings()
                self.request.session.flash("Settings have been removed.")
                return self.redirect(self.request.current_route_url())
            else:
                data = self.request.json_body
                self.save_settings(data)
                self.request.session.flash("Settings have been saved.  "
                                           "You should probably restart DataSync now.")
                return self.json_response({'success': True})

        profiles = load_profiles(self.rattail_config,
                                 include_disabled=True,
                                 ignore_problems=True)

        profiles_data = []
        for profile in sorted(profiles.values(), key=lambda p: p.key):
            data = {
                'key': profile.key,
                'watcher_spec': profile.watcher_spec,
                'watcher_dbkey': profile.watcher.dbkey,
                'watcher_delay': profile.watcher.delay,
                'watcher_retry_attempts': profile.watcher.retry_attempts,
                'watcher_retry_delay': profile.watcher.retry_delay,
                'watcher_default_runas': profile.watcher.default_runas,
                'watcher_consumes_self': profile.watcher.consumes_self,
                # 'notes': None,   # TODO
                'enabled': profile.enabled,
            }

            consumers = []
            if profile.watcher.consumes_self:
                pass
            else:
                for consumer in sorted(profile.consumers, key=lambda c: c.key):
                    consumers.append({
                        'key': consumer.key,
                        'consumer_spec': consumer.spec,
                        'consumer_dbkey': consumer.dbkey,
                        'consumer_runas': getattr(consumer, 'runas', None),
                        'consumer_delay': consumer.delay,
                        'consumer_retry_attempts': consumer.retry_attempts,
                        'consumer_retry_delay': consumer.retry_delay,
                        'enabled': consumer.enabled,
                    })
            data['consumers_data'] = consumers
            profiles_data.append(data)

        return {
            'master': self,
            # TODO: really only buefy themes are supported here
            'use_buefy': self.get_use_buefy(),
            'index_title': "DataSync Changes",
            'index_url': self.get_index_url(),
            'profiles': profiles,
            'profiles_data': profiles_data,
            'restart_command': self.rattail_config.get('tailbone', 'datasync.restart'),
            'system_user': getpass.getuser(),
        }

    def save_settings(self, data):
        model = self.model

        # collect new settings
        settings = []
        watch = []
        for profile in data['profiles']:
            pkey = profile['key']
            if profile['enabled']:
                watch.append(pkey)
            settings.extend([
                {'name': 'rattail.datasync.{}.watcher'.format(pkey),
                 'value': profile['watcher_spec']},
                {'name': 'rattail.datasync.{}.watcher.db'.format(pkey),
                 'value': profile['watcher_dbkey']},
                {'name': 'rattail.datasync.{}.watcher.delay'.format(pkey),
                 'value': profile['watcher_delay']},
                {'name': 'rattail.datasync.{}.watcher.retry_attempts'.format(pkey),
                 'value': profile['watcher_retry_attempts']},
                {'name': 'rattail.datasync.{}.watcher.retry_delay'.format(pkey),
                 'value': profile['watcher_retry_delay']},
                {'name': 'rattail.datasync.{}.consumers.runas'.format(pkey),
                 'value': profile['watcher_default_runas']},
            ])
            consumers = []
            if profile['watcher_consumes_self']:
                consumers = ['self']
            else:
                for consumer in profile['consumers_data']:
                    ckey = consumer['key']
                    if consumer['enabled']:
                        consumers.append(ckey)
                    settings.extend([
                        {'name': 'rattail.datasync.{}.consumer.{}'.format(pkey, ckey),
                         'value': consumer['consumer_spec']},
                        {'name': 'rattail.datasync.{}.consumer.{}.db'.format(pkey, ckey),
                         'value': consumer['consumer_dbkey']},
                        {'name': 'rattail.datasync.{}.consumer.{}.delay'.format(pkey, ckey),
                         'value': consumer['consumer_delay']},
                        {'name': 'rattail.datasync.{}.consumer.{}.retry_attempts'.format(pkey, ckey),
                         'value': consumer['consumer_retry_attempts']},
                        {'name': 'rattail.datasync.{}.consumer.{}.retry_delay'.format(pkey, ckey),
                         'value': consumer['consumer_retry_delay']},
                        {'name': 'rattail.datasync.{}.consumer.{}.runas'.format(pkey, ckey),
                         'value': consumer['consumer_runas']},
                    ])
            settings.extend([
                {'name': 'rattail.datasync.{}.consumers'.format(pkey),
                 'value': ', '.join(consumers)},
            ])
        settings.extend([
            {'name': 'rattail.datasync.watch',
             'value': ', '.join(watch)},
            {'name': 'tailbone.datasync.restart',
             'value': data['restart_command']},
        ])

        # delete all current settings
        self.delete_settings()

        # create all new settings
        for setting in settings:
            self.Session.add(model.Setting(name=setting['name'],
                                           value=setting['value']))

    def delete_settings(self):
        purge_datasync_settings(self.rattail_config, self.Session())

    @classmethod
    def defaults(cls, config):
        cls._defaults(config)
        cls._datasync_defaults(config)

    @classmethod
    def _datasync_defaults(cls, config):
        permission_prefix = cls.get_permission_prefix()

        # fix permission group title
        config.add_tailbone_permission_group(permission_prefix, label="DataSync")

        # restart datasync
        config.add_tailbone_permission(permission_prefix,
                                       '{}.restart'.format(permission_prefix),
                                       label="Restart the DataSync daemon")
        config.add_route('datasync.restart', '/datasync/restart',
                         request_method='POST')
        config.add_view(cls, attr='restart',
                        route_name='datasync.restart',
                        permission='{}.restart'.format(permission_prefix))

        # configure datasync
        config.add_tailbone_permission(permission_prefix,
                                       '{}.configure'.format(permission_prefix),
                                       label="Configure the DataSync daemon")
        config.add_route('datasync.configure', '/datasync/configure')
        config.add_view(cls, attr='configure',
                        route_name='datasync.configure',
                        permission='{}.configure'.format(permission_prefix),
                        renderer='/datasync/configure.mako')

# TODO: deprecate / remove this
DataSyncChangesView = DataSyncChangeView


def includeme(config):
    DataSyncChangeView.defaults(config)
