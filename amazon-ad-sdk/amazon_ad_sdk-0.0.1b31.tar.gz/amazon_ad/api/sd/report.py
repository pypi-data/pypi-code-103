# -*- coding: utf-8 -*-
# Authored by: Ryan

from amazon_ad.api.base import ZADOpenAPI

ALLOW_REPORT_TYPES = [
    "campaigns",
    "adGroups",
    "productAds",
    "targets",
    "asins",
]

# 所有的广告策略
ALL_TACTICS = ['T00001', 'T00020', 'T00030', 'remarketing']

REPORT_TYPE_METRIC_MAPPING = {
    'campaigns': {
        'T00020': ['campaignName',
                   'campaignId',
                   'impressions',
                   'clicks',
                   'cost',
                   'currency',
                   'attributedConversions1d',
                   'attributedConversions7d',
                   'attributedConversions14d',
                   'attributedConversions30d',
                   'attributedConversions1dSameSKU',
                   'attributedConversions7dSameSKU',
                   'attributedConversions14dSameSKU',
                   'attributedConversions30dSameSKU',
                   'attributedUnitsOrdered1d',
                   'attributedUnitsOrdered7d',
                   'attributedUnitsOrdered14d',
                   'attributedUnitsOrdered30d',
                   'attributedSales1d',
                   'attributedSales7d',
                   'attributedSales14d',
                   'attributedSales30d',
                   'attributedSales1dSameSKU',
                   'attributedSales7dSameSKU',
                   'attributedSales14dSameSKU',
                   'attributedSales30dSameSKU',
                   'attributedOrdersNewToBrand14d',
                   'attributedSalesNewToBrand14d',
                   'attributedUnitsOrderedNewToBrand14d',
                   'costType',
                   'viewImpressions',
                   'viewAttributedConversions14d',
                   'viewAttributedSales14d',
                   'viewAttributedUnitsOrdered14d'],
        'T00030': ['campaignName',
                   'campaignId',
                   'impressions',
                   'clicks',
                   'cost',
                   'currency',
                   'attributedConversions1d',
                   'attributedConversions7d',
                   'attributedConversions14d',
                   'attributedConversions30d',
                   'attributedConversions1dSameSKU',
                   'attributedConversions7dSameSKU',
                   'attributedConversions14dSameSKU',
                   'attributedConversions30dSameSKU',
                   'attributedUnitsOrdered1d',
                   'attributedUnitsOrdered7d',
                   'attributedUnitsOrdered14d',
                   'attributedUnitsOrdered30d',
                   'attributedSales1d',
                   'attributedSales7d',
                   'attributedSales14d',
                   'attributedSales30d',
                   'attributedSales1dSameSKU',
                   'attributedSales7dSameSKU',
                   'attributedSales14dSameSKU',
                   'attributedSales30dSameSKU',
                   'attributedOrdersNewToBrand14d',
                   'attributedSalesNewToBrand14d',
                   'attributedUnitsOrderedNewToBrand14d',
                   'costType',
                   'viewImpressions',
                   'viewAttributedConversions14d',
                   'viewAttributedSales14d',
                   'viewAttributedUnitsOrdered14d'],
        'remarketing': ['campaignName',
                        'campaignId',
                        'impressions',
                        'clicks',
                        'cost',
                        'currency',
                        'attributedConversions1d',
                        'attributedConversions7d',
                        'attributedConversions14d',
                        'attributedConversions30d',
                        'attributedConversions1dSameSKU',
                        'attributedConversions7dSameSKU',
                        'attributedConversions14dSameSKU',
                        'attributedConversions30dSameSKU',
                        'attributedUnitsOrdered1d',
                        'attributedUnitsOrdered7d',
                        'attributedUnitsOrdered14d',
                        'attributedUnitsOrdered30d',
                        'attributedSales1d',
                        'attributedSales7d',
                        'attributedSales14d',
                        'attributedSales30d',
                        'attributedSales1dSameSKU',
                        'attributedSales7dSameSKU',
                        'attributedSales14dSameSKU',
                        'attributedSales30dSameSKU'],
        'T00001': ['campaignName',
                   'campaignId',
                   'campaignStatus',
                   'currency',
                   'impressions',
                   'clicks',
                   'cost',
                   'attributedDPV14d',
                   'attributedUnitsSold14d',
                   'attributedSales14d']},
    'adGroups': {'T00020': ['campaignName',
                            'campaignId',
                            'adGroupName',
                            'adGroupId',
                            'impressions',
                            'clicks',
                            'cost',
                            'currency',
                            'attributedConversions1d',
                            'attributedConversions7d',
                            'attributedConversions14d',
                            'attributedConversions30d',
                            'attributedConversions1dSameSKU',
                            'attributedConversions7dSameSKU',
                            'attributedConversions14dSameSKU',
                            'attributedConversions30dSameSKU',
                            'attributedUnitsOrdered1d',
                            'attributedUnitsOrdered7d',
                            'attributedUnitsOrdered14d',
                            'attributedUnitsOrdered30d',
                            'attributedSales1d',
                            'attributedSales7d',
                            'attributedSales14d',
                            'attributedSales30d',
                            'attributedSales1dSameSKU',
                            'attributedSales7dSameSKU',
                            'attributedSales14dSameSKU',
                            'attributedSales30dSameSKU',
                            'attributedOrdersNewToBrand14d',
                            'attributedSalesNewToBrand14d',
                            'attributedUnitsOrderedNewToBrand14d',
                            'bidOptimization',
                            'viewImpressions',
                            'viewAttributedConversions14d',
                            'viewAttributedSales14d',
                            'viewAttributedUnitsOrdered14d'],
                 'T00030': ['campaignName',
                            'campaignId',
                            'adGroupName',
                            'adGroupId',
                            'impressions',
                            'clicks',
                            'cost',
                            'currency',
                            'attributedConversions1d',
                            'attributedConversions7d',
                            'attributedConversions14d',
                            'attributedConversions30d',
                            'attributedConversions1dSameSKU',
                            'attributedConversions7dSameSKU',
                            'attributedConversions14dSameSKU',
                            'attributedConversions30dSameSKU',
                            'attributedUnitsOrdered1d',
                            'attributedUnitsOrdered7d',
                            'attributedUnitsOrdered14d',
                            'attributedUnitsOrdered30d',
                            'attributedSales1d',
                            'attributedSales7d',
                            'attributedSales14d',
                            'attributedSales30d',
                            'attributedSales1dSameSKU',
                            'attributedSales7dSameSKU',
                            'attributedSales14dSameSKU',
                            'attributedSales30dSameSKU',
                            'attributedOrdersNewToBrand14d',
                            'attributedSalesNewToBrand14d',
                            'attributedUnitsOrderedNewToBrand14d',
                            'bidOptimization',
                            'viewImpressions',
                            'viewAttributedConversions14d',
                            'viewAttributedSales14d',
                            'viewAttributedUnitsOrdered14d'],
                 'remarketing': ['campaignName',
                                 'campaignId',
                                 'adGroupName',
                                 'adGroupId',
                                 'impressions',
                                 'clicks',
                                 'cost',
                                 'currency',
                                 'attributedConversions1d',
                                 'attributedConversions7d',
                                 'attributedConversions14d',
                                 'attributedConversions30d',
                                 'attributedConversions1dSameSKU',
                                 'attributedConversions7dSameSKU',
                                 'attributedConversions14dSameSKU',
                                 'attributedConversions30dSameSKU',
                                 'attributedUnitsOrdered1d',
                                 'attributedUnitsOrdered7d',
                                 'attributedUnitsOrdered14d',
                                 'attributedUnitsOrdered30d',
                                 'attributedSales1d',
                                 'attributedSales7d',
                                 'attributedSales14d',
                                 'attributedSales30d',
                                 'attributedSales1dSameSKU',
                                 'attributedSales7dSameSKU',
                                 'attributedSales14dSameSKU',
                                 'attributedSales30dSameSKU']},
    'productAds': {'T00020': ['campaignName',
                              'campaignId',
                              'adGroupName',
                              'adGroupId',
                              'asin',
                              'sku',
                              'adId',
                              'impressions',
                              'clicks',
                              'cost',
                              'currency',
                              'attributedConversions1d',
                              'attributedConversions7d',
                              'attributedConversions14d',
                              'attributedConversions30d',
                              'attributedConversions1dSameSKU',
                              'attributedConversions7dSameSKU',
                              'attributedConversions14dSameSKU',
                              'attributedConversions30dSameSKU',
                              'attributedUnitsOrdered1d',
                              'attributedUnitsOrdered7d',
                              'attributedUnitsOrdered14d',
                              'attributedUnitsOrdered30d',
                              'attributedSales1d',
                              'attributedSales7d',
                              'attributedSales14d',
                              'attributedSales30d',
                              'attributedSales1dSameSKU',
                              'attributedSales7dSameSKU',
                              'attributedSales14dSameSKU',
                              'attributedSales30dSameSKU',
                              'attributedOrdersNewToBrand14d',
                              'attributedSalesNewToBrand14d',
                              'attributedUnitsOrderedNewToBrand14d',
                              'viewImpressions',
                              'viewAttributedConversions14d',
                              'viewAttributedSales14d',
                              'viewAttributedUnitsOrdered14d'],
                   'T00030': ['campaignName',
                              'campaignId',
                              'adGroupName',
                              'adGroupId',
                              'asin',
                              'sku',
                              'adId',
                              'impressions',
                              'clicks',
                              'cost',
                              'currency',
                              'attributedConversions1d',
                              'attributedConversions7d',
                              'attributedConversions14d',
                              'attributedConversions30d',
                              'attributedConversions1dSameSKU',
                              'attributedConversions7dSameSKU',
                              'attributedConversions14dSameSKU',
                              'attributedConversions30dSameSKU',
                              'attributedUnitsOrdered1d',
                              'attributedUnitsOrdered7d',
                              'attributedUnitsOrdered14d',
                              'attributedUnitsOrdered30d',
                              'attributedSales1d',
                              'attributedSales7d',
                              'attributedSales14d',
                              'attributedSales30d',
                              'attributedSales1dSameSKU',
                              'attributedSales7dSameSKU',
                              'attributedSales14dSameSKU',
                              'attributedSales30dSameSKU',
                              'attributedOrdersNewToBrand14d',
                              'attributedSalesNewToBrand14d',
                              'attributedUnitsOrderedNewToBrand14d',
                              'viewImpressions',
                              'viewAttributedConversions14d',
                              'viewAttributedSales14d',
                              'viewAttributedUnitsOrdered14d'],
                   'remarketing': ['campaignName',
                                   'campaignId',
                                   'adGroupName',
                                   'adGroupId',
                                   'asin',
                                   'sku',
                                   'adId',
                                   'impressions',
                                   'clicks',
                                   'cost',
                                   'currency',
                                   'attributedConversions1d',
                                   'attributedConversions7d',
                                   'attributedConversions14d',
                                   'attributedConversions30d',
                                   'attributedConversions1dSameSKU',
                                   'attributedConversions7dSameSKU',
                                   'attributedConversions14dSameSKU',
                                   'attributedConversions30dSameSKU',
                                   'attributedUnitsOrdered1d',
                                   'attributedUnitsOrdered7d',
                                   'attributedUnitsOrdered14d',
                                   'attributedUnitsOrdered30d',
                                   'attributedSales1d',
                                   'attributedSales7d',
                                   'attributedSales14d',
                                   'attributedSales30d',
                                   'attributedSales1dSameSKU',
                                   'attributedSales7dSameSKU',
                                   'attributedSales14dSameSKU',
                                   'attributedSales30dSameSKU']},
    'targets': {'T00020': ['campaignName',
                           'campaignId',
                           'adGroupName',
                           'adGroupId',
                           'targetId',
                           'targetingExpression',
                           'targetingText',
                           'targetingType',
                           'impressions',
                           'clicks',
                           'cost',
                           'currency',
                           'attributedConversions1d',
                           'attributedConversions7d',
                           'attributedConversions14d',
                           'attributedConversions30d',
                           'attributedConversions1dSameSKU',
                           'attributedConversions7dSameSKU',
                           'attributedConversions14dSameSKU',
                           'attributedConversions30dSameSKU',
                           'attributedUnitsOrdered1d',
                           'attributedUnitsOrdered7d',
                           'attributedUnitsOrdered14d',
                           'attributedUnitsOrdered30d',
                           'attributedSales1d',
                           'attributedSales7d',
                           'attributedSales14d',
                           'attributedSales30d',
                           'attributedSales1dSameSKU',
                           'attributedSales7dSameSKU',
                           'attributedSales14dSameSKU',
                           'attributedSales30dSameSKU',
                           'attributedOrdersNewToBrand14d',
                           'attributedSalesNewToBrand14d',
                           'attributedUnitsOrderedNewToBrand14d',
                           'viewImpressions',
                           'viewAttributedConversions14d',
                           'viewAttributedSales14d',
                           'viewAttributedUnitsOrdered14d'],
                'T00030': ['campaignName',
                           'campaignId',
                           'adGroupName',
                           'adGroupId',
                           'targetId',
                           'targetingExpression',
                           'targetingText',
                           'targetingType',
                           'impressions',
                           'clicks',
                           'cost',
                           'currency',
                           'attributedConversions1d',
                           'attributedConversions7d',
                           'attributedConversions14d',
                           'attributedConversions30d',
                           'attributedConversions1dSameSKU',
                           'attributedConversions7dSameSKU',
                           'attributedConversions14dSameSKU',
                           'attributedConversions30dSameSKU',
                           'attributedUnitsOrdered1d',
                           'attributedUnitsOrdered7d',
                           'attributedUnitsOrdered14d',
                           'attributedUnitsOrdered30d',
                           'attributedSales1d',
                           'attributedSales7d',
                           'attributedSales14d',
                           'attributedSales30d',
                           'attributedSales1dSameSKU',
                           'attributedSales7dSameSKU',
                           'attributedSales14dSameSKU',
                           'attributedSales30dSameSKU',
                           'attributedOrdersNewToBrand14d',
                           'attributedSalesNewToBrand14d',
                           'attributedUnitsOrderedNewToBrand14d',
                           'viewImpressions',
                           'viewAttributedConversions14d',
                           'viewAttributedSales14d',
                           'viewAttributedUnitsOrdered14d']},
    'asins': {'T00020': ['campaignName',
                         'campaignId',
                         'adGroupName',
                         'adGroupId',
                         'asin',
                         'otherAsin',
                         'sku',
                         'currency',
                         'attributedUnitsOrdered1dOtherSKU',
                         'attributedUnitsOrdered7dOtherSKU',
                         'attributedUnitsOrdered14dOtherSKU',
                         'attributedUnitsOrdered30dOtherSKU',
                         'attributedSales1dOtherSKU',
                         'attributedSales7dOtherSKU',
                         'attributedSales14dOtherSKU',
                         'attributedSales30dOtherSKU'],
              'T00030': ['campaignName',
                         'campaignId',
                         'adGroupName',
                         'adGroupId',
                         'asin',
                         'otherAsin',
                         'sku',
                         'currency',
                         'attributedUnitsOrdered1dOtherSKU',
                         'attributedUnitsOrdered7dOtherSKU',
                         'attributedUnitsOrdered14dOtherSKU',
                         'attributedUnitsOrdered30dOtherSKU',
                         'attributedSales1dOtherSKU',
                         'attributedSales7dOtherSKU',
                         'attributedSales14dOtherSKU',
                         'attributedSales30dOtherSKU']}}


class SdReport(ZADOpenAPI):
    def request(self, record_type, report_date, tactic, metrics):
        """
        POST    /sd/{recordType}/report
        """

        path = '/sd/{record_type}/report'.format(record_type=record_type)

        if isinstance(metrics, (list, tuple)):
            metrics = ','.join(metrics)

        data = {
            'reportDate': report_date,
            'tactic': tactic,
            'metrics': metrics
        }
        return self.post(path, data)

    def _get_metrics(self, metrics, default):
        if not metrics:
            metrics = default

        return metrics

    def campaigns(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))

        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_t00001(self, report_date, metrics=None, **kwargs):
        tactic = 'T00001'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def campaigns_remarketing(self, report_date, metrics=None, **kwargs):
        tactic = 'remarketing'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('campaigns').get(tactic))
        return self.request('campaigns', report_date, tactic, metrics)

    def ad_groups(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))

        return self.request('adGroups', report_date, tactic, metrics)

    def ad_groups_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))
        return self.request('adGroups', report_date, tactic, metrics)

    def ad_groups_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))
        return self.request('adGroups', report_date, tactic, metrics)

    def ad_groups_remarketing(self, report_date, metrics=None, **kwargs):
        tactic = 'remarketing'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('adGroups').get(tactic))
        return self.request('adGroups', report_date, tactic, metrics)

    def product_ads(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))

        return self.request('productAds', report_date, tactic, metrics)

    def product_ads_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))
        return self.request('productAds', report_date, tactic, metrics)

    def product_ads_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))
        return self.request('productAds', report_date, tactic, metrics)

    def product_ads_remarketing(self, report_date, metrics=None, **kwargs):
        tactic = 'remarketing'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('productAds').get(tactic))
        return self.request('productAds', report_date, tactic, metrics)

    def targets(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get(tactic))

        return self.request('targets', report_date, tactic, metrics)

    def targets_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get(tactic))
        return self.request('targets', report_date, tactic, metrics)

    def targets_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('targets').get(tactic))
        return self.request('targets', report_date, tactic, metrics)

    def asins(self, report_date, tactic, metrics=None, **kwargs):

        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('asins').get(tactic))

        return self.request('asins', report_date, tactic, metrics)

    def asins_t00020(self, report_date, metrics=None, **kwargs):
        tactic = 'T00020'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('asins').get(tactic))
        return self.request('asins', report_date, tactic, metrics)

    def asins_t00030(self, report_date, metrics=None, **kwargs):
        tactic = 'T00030'
        metrics = self._get_metrics(metrics, REPORT_TYPE_METRIC_MAPPING.get('asins').get(tactic))
        return self.request('asins', report_date, tactic, metrics)

    def local_test(self, **kwargs):
        """
        测试用的接口
        """
        path = kwargs.get('path')
        data = kwargs.get('data')
        return self.post(path, data)
