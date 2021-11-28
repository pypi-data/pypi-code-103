#!/opt/local/bin/python
# Copyright 2015, Octoboxy LLC.  All Rights Reserved.

import base
import sys

from django.conf                  import settings
from django.core.management.base  import BaseCommand, CommandError
from django.db                    import connection

from django.core.management.commands import migrate
from django.contrib.staticfiles.management.commands import collectstatic


class Command(BaseCommand):
  help              = 'Drops all tables that we own in the database.'

  def add_arguments(self, parser):
    parser.add_argument('--bootstrap', action='store_true', help='Follow with an automatic migrate and bootstrap')
    parser.add_argument('--diediedie', action='store_true', help='I really know what I am doing, skip confirmation please')

  def handle(self, *args, **options):
    reboot          = options.get('bootstrap')
    diediedone      = options.get('diediedie')

    tables          = self.FindTables()
    if not tables and not reboot:
      print('No tables found to destroy.')
      sys.exit(1)

    if not diediedone and tables:
      self.Affirmation(reboot, tables)
    if tables:
      self.DropTables(tables)
    if reboot:
      migrate.Command().handle(
          app_label       = None,
          database        = 'default',
          fake            = False,
          fake_initial    = False,
          interactive     = False,
          migration_name  = None,
          plan            = False,
          run_syncdb      = False,
          verbosity       = 0,
      )

      base.backups.Bootstrap(base.backups.ListModels(None, None))

      collectstatic.Command().handle(
          clear=            False,
          dry_run=          False,
          ignore_patterns=  [],
          interactive=      False,
          link=             False,
          post_process=     True,
          use_default_ignore_patterns=True,
          verbosity=        0,
      )


  def Affirmation(self, reboot, tables):
    tables_str      = '   ' + '\n   '.join(tables)
    reboot_str      = reboot and ', migrate, and bootstrap' or ''
    print('\n{}\n\nAbout to drop{} all the above tables.'.format(tables_str, reboot_str))
    confirm         = input('Is this really what you want to do?  If so, confirm by typing "diediedie": ')
    if confirm:
      confirm       = confirm.strip().lower()
    if confirm != 'diediedie':
      print('Aborted.')
      sys.exit(1)

  def FindTables(self):
    username    = settings.DATABASES['default']['USER']
    cursor      = connection.cursor()
    cursor.execute('SELECT tablename FROM pg_catalog.pg_tables WHERE tableowner = %s;', [username, ])
    tables      = [x[0] for x in cursor.fetchall() if x and x[0]]
    tables.sort()
    return tables

  def DropTables(self, tables):
    tables      = ', '.join(tables)
    cursor      = connection.cursor()
    cursor.execute('DROP TABLE {} CASCADE;'.format(tables))
    cursor.close()
