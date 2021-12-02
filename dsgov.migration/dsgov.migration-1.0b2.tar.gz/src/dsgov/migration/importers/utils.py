# -*- coding: utf-8 -*-

import csv
import pandas as pd
import numpy as np
import logging


logger = logging.getLogger('Transmogrifier')


class Filters():
    filters = []
    keys_tags = []

    def __init__(self, s_year=2000, e_yaer=2025, search_year=True):
        self.start_year = int(s_year)
        self.end_year = int(e_yaer)
        self.search_year = search_year

    def check_cond(self, key):
        return True if key in self.filters else False

    def load_from_csv(self, filter_file):

        filters = []
        with open(filter_file, mode='r') as infile:
            reader = csv.DictReader(infile, delimiter=';')
            for r in reader:
                filters.append(r)
        self.filters = filters

    def load_from_excel(self, filter_file):
        """
        Load filter data from excel file.
        """
        # Try to load filters from sheet filters
        filters = pd.read_excel(
            filter_file, sheet_name='filters', header=0, converters={'tags': str}).to_dict('records')
        df = pd.DataFrame(filters)
        df['tags'] = df['tags'].astype(str)
        df1 = df.where(df.notnull(), None)
        filters1 = df1.to_dict('records')
        self.filters = filters1

        # Try to load tags from sheet key_tags
        keys_tags = pd.read_excel(
            filter_file, sheet_name='keys_tags').to_dict('records')
        df = pd.DataFrame(keys_tags)
        df1 = df.where(df.notnull(), None)
        keys_tags1 = df1.to_dict('records')
        self.keys_tags = keys_tags1

    def get_years(self, item_filter):
        """
        Get years range to tag item.
        """
        years = []
        if item_filter.get('tag_years') is not None:
            year_range = str(item_filter.get('tag_years')).split('-')
            start = int(year_range[0])
            end = int(year_range[1])
            while start <= end:
                years.append(str(start))
                start += 1
        return years

    def locate_year_in_path(self, item_filter, path):
        """
        Look for years in path.
        """
        years_to_tag = []
        years = self.get_years(item_filter)
        for y in years:
            if y in path:
                years_to_tag.append(y)
        return years_to_tag

    def add_tags(self, new_tags, item_tags):
        """
        Add tags from list.
        """
        for tag in new_tags:
            if self.tag_exists(tag, item_tags):
                continue
            else:
                item_tags.append(tag)
        return item_tags

    def get_filter(self, item):
        """
        Get all filters from a specified content type.
        """
        content_type = item.get('_type')
        content_path = item.get('_path')
        for f in self.filters:
            if f.get('content_type') == content_type:
                if (f.get('original_path') in content_path) \
                        or (f.get('original_path') == '*'):
                    logger.info(
                        '[filters found] type: %s, in path: %s',
                        f.get('content_type'),
                        f.get('original_path'))
                    return f
            else:
                if f.get('content_type') == '*':
                    if (f.get('original_path') in content_path) \
                            or (f.get('original_path') == '*'):
                        logger.info(
                            '[filters found] type: %s, in path: %s',
                            f.get('content_type'),
                            f.get('original_path'))
                        return f
        return None

    def get_filter_tags(self, item_filter):
        """
        Getl all tags from filter to be appended to item tags.
        """
        filter_tags = item_filter.get('tags')
        if filter_tags == 'nan':
            return []
        if filter_tags is not None:
            filter_tags = str(filter_tags).replace(', ', ',').split(',')
        else:
            filter_tags = []
        return filter_tags

    def get_item_tags(self, item):
        """
        Get all actual tegs from item.
        """
        if item.get('subjects') is not None:
            return item.get('subjects')
        else:
            if item.get('subject') is not None:
                return item.get('subject')
        return []

    def tag_exists(self, tag, item_tags):
        """
        Check if a tag alredy exists in item.
        """
        for t in item_tags:
            if t == tag:
                return True
        return False

    def locate_key_tags_in_path(self, item_filter, path):
        """
        Search for key tags in path.
        """
        extra_tags = []
        if item_filter.get('extra_tags'):
            for tag in self.keys_tags:
                k = tag.get('key')
                t = tag.get('tag')
                k_list = str(k).replace(', ', ',').split(',')
                if all(k_ in path for k_ in k_list):
                    extra_tags.append(t)
        return extra_tags

    def update_data(self, item, item_filter):
        """
        Update item data.
        """

        # item = item
        item_id = item.get('id')
        if item_id is None:
            item_id = item.get('_id')

        # Save current path for tag lookup and backup
        current_path = item.get('_path')

        # Set item path
        if not item_filter.get('new_path') is None:
            if item_filter.get('preserv_path') is True:
                new_item_path = item_filter.get('new_path') + current_path
            else:
                new_item_path = item_filter.get('new_path') + '/' + item_id

            if item_filter.get('include_uid_in_path'):
                new_item_path = new_item_path + '-' + item.get('_uid')
            item['_path'] = new_item_path

        # Strip string form item path
        if not item_filter.get('strip') is None:
            item['_path'] = str(item['_path']).strip(item_filter.get('strip'))

        # Check if item must be excluded from navigation
        item['exclude_from_nav'] = item_filter.get('exclude_from_nav')

        # Get current item tags
        item_tags = self.get_item_tags(item)

        # Set item tags
        new_tags = self.get_filter_tags(item_filter)
        item_tags = self.add_tags(new_tags, item_tags)

        # Look for extra tags
        extra_tags = self.locate_key_tags_in_path(item_filter, current_path)
        item_tags = self.add_tags(extra_tags, item_tags)

        # Look for years in path to tag
        years_tag = self.locate_year_in_path(item_filter, current_path)
        item_tags = self.add_tags(years_tag, item_tags)

        # Log add tags if exists
        if len(item_tags) > 0:
            logger.info('[adding tags] %s', item_tags)

        # Add tags to item
        item['subjects'] = tuple(item_tags)

        return item

    def update_item(self, item):
        f = self.get_filter(item)
        if f is not None:
            return self.update_data(item, f)
        else:
            logger.info('[no filters found for] %s', item.get('_path'))
        return item
