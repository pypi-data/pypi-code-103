#!/usr/bin/env python3
# coding: utf-8

import os

import volkanic.environ
from volkanic.compat import cached_property


class GlobalInterface(volkanic.environ.GlobalInterfacePlus):
    package_name = 'joker.environ'
    default_config = {}
    _meta = {}

    # this method will be moved to JokerInterface at ver 0.3.0
    @classmethod
    def under_joker_dir(cls, *paths):
        path = os.environ.get('JOKER_HOME', cls.under_home_dir('.joker'))
        if not cls._meta.get('joker_dir_made'):
            os.makedirs(path, int('700', 8), exist_ok=True)
            cls._meta['joker_dir_made'] = True
        return os.path.join(path, *paths)

    def under_temp_dir(self, ext=''):
        name = os.urandom(17).hex() + ext
        return self.under_data_dir('tmp', name, mkdirs=True)

    # both will be removed
    get_temp_path = under_temp_dir
    under_temp_path = under_temp_dir
    _get_conf_search_paths = None

    @cached_property
    def jinja2_env(self):
        # noinspection PyPackageRequirements
        from jinja2 import Environment, PackageLoader, select_autoescape
        return Environment(
            loader=PackageLoader(self.package_name, 'templates'),
            autoescape=select_autoescape(['html', 'xml']),
        )
