# -*- coding: utf-8 -*-
# Authored by: Josh (joshzda@gmail.com)

from amazon_ad.api.base import ZADOpenAPI

ALLOW_REPORT_TYPES = [
    "campaigns",
    "adGroups",
    "targets",
    "keywords",
]


DEFAULT_REPORT_METRICS = {
    "campaigns":  [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2
        #
        # "adGroupName",
        # "adGroupId",
        # "keywordText",
        # "keywordBid",
        # "keywordStatus",
        # "targetId",
        #
        # "searchTermImpressionRank",
        # "searchTermImpressionShare"
        #
        # "targetingExpression",
        # "targetingText",
        # "targetingType",
        # "matchType",

        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",
        # "viewableImpressions",
        # "videoFirstQuartileViews",
        # "videoMidpointViews",
        # "videoThirdQuartileViews",
        # "videoCompleteViews",
        # "video5SecondViews",
        # "video5SecondViewRate",
        # "videoUnmutes",
        # "vtr",
        # "vctr",
    ],
    "adGroups": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2
        #
        "adGroupName",
        "adGroupId",
        # "keywordText",
        # "keywordBid",
        # "keywordStatus",
        # "targetId",
        #
        # "searchTermImpressionRank",
        # "searchTermImpressionShare"
        #
        # "targetingExpression",
        # "targetingText",
        # "targetingType",
        # "matchType",

        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",
        # "viewableImpressions",
        # "videoFirstQuartileViews",
        # "videoMidpointViews",
        # "videoThirdQuartileViews",
        # "videoCompleteViews",
        # "video5SecondViews",
        # "video5SecondViewRate",
        # "videoUnmutes",
        # "vtr",
        # "vctr",
    ],

    # Unsupported fields for targets report: keywordStatus,keywordText,keywordBid,matchType.
    # Unrecognized metric: query
    # Unsupported fields for targets report:
    # applicableBudgetRuleId,applicableBudgetRuleName,searchTermImpressionShare,campaignRuleBasedBudget,searchTermImpressionRank.
    # Metric vtr is not available for campaign type HEADLINE_SEARCH
    "targets": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2

        "adGroupName",
        "adGroupId",
        # "keywordText",
        # "keywordBid",
        # "keywordStatus",
        "targetId",

        # "searchTermImpressionRank",  # V2
        # "searchTermImpressionShare",  # V2

        "targetingExpression",
        "targetingText",
        "targetingType",
        # "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",  # V2
        # "viewableImpressions",  # V2
        # "videoFirstQuartileViews",  # V2
        # "videoMidpointViews",  # V2
        # "videoThirdQuartileViews",  # V2
        # "videoCompleteViews",  # V2
        # "video5SecondViews",  # V2
        # "video5SecondViewRate",  # V2
        # "videoUnmutes",  # V2
        # "vtr",  # V2
        # "vctr",  # V2
    ],
    "keywords": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        # "campaignRuleBasedBudget",  # V2
        # "applicableBudgetRuleId",  # V2
        # "applicableBudgetRuleName",  # V2

        "adGroupName",
        "adGroupId",
        "keywordText",
        "keywordBid",
        "keywordStatus",
        "targetId",

        # "searchTermImpressionRank",
        # "searchTermImpressionShare"

        "targetingExpression",
        "targetingText",
        "targetingType",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        # "query",
        # "viewableImpressions",
        # "videoFirstQuartileViews",
        # "videoMidpointViews",
        # "videoThirdQuartileViews",
        # "videoCompleteViews",
        # "video5SecondViews",
        # "video5SecondViewRate",
        # "videoUnmutes",
        # "vtr",
        # "vctr",
    ],
    # 貌似所有sb报表均可以导出这些字段（有的为空值），建议使用快照了导出全字段
    "all": [
        "campaignName",
        "campaignId",
        "campaignStatus",
        "campaignBudget",
        "campaignBudgetType",

        "campaignRuleBasedBudget",  # V2
        "applicableBudgetRuleId",  # V2
        "applicableBudgetRuleName",  # V2

        "adGroupName",
        "adGroupId",
        "keywordText",
        "keywordBid",
        "keywordStatus",
        "targetId",

        "searchTermImpressionRank",
        "searchTermImpressionShare"

        "targetingExpression",
        "targetingText",
        "targetingType",
        "matchType",
        "impressions",
        "clicks",
        "cost",
        "attributedDetailPageViewsClicks14d",
        "attributedSales14d",
        "attributedSales14dSameSKU",
        "attributedConversions14d",
        "attributedConversions14dSameSKU",
        "attributedOrdersNewToBrand14d",
        "attributedOrdersNewToBrandPercentage14d",
        "attributedOrderRateNewToBrand14d",
        "attributedSalesNewToBrand14d",
        "attributedSalesNewToBrandPercentage14d",
        "attributedUnitsOrderedNewToBrand14d",
        "attributedUnitsOrderedNewToBrandPercentage14d",
        "unitsSold14d",
        "dpv14d",

        "query",
        "viewableImpressions",
        "videoFirstQuartileViews",
        "videoMidpointViews",
        "videoThirdQuartileViews",
        "videoCompleteViews",
        "video5SecondViews",
        "video5SecondViewRate",
        "videoUnmutes",
        "vtr",
        "vctr",
    ],

}

# 这些字段存在于 赞助品牌视频报告，即 creativeType=video
AVAILABLE_VIDEO_REPORT_METRICS = [
    "campaignName",
    "campaignId",
    "campaignStatus",
    "campaignBudget",
    "campaignBudgetType",
    "adGroupName",
    "adGroupId",
    "keywordText",
    "keywordBid",
    "keywordStatus",
    "targetId",
    "targetingExpression",
    "targetingText",
    "targetingType",
    "matchType",
    "impressions",
    "clicks",
    "cost",
    "attributedSales14d",
    "attributedSales14dSameSKU",
    "attributedConversions14d",
    "attributedConversions14dSameSKU",

    "query",  # V2
    "viewableImpressions",  # V2
    "videoFirstQuartileViews",  # V2
    "videoMidpointViews",  # V2
    "videoThirdQuartileViews",  # V2
    "videoCompleteViews",  # V2
    "video5SecondViews",  # V2
    "video5SecondViewRate",  # V2
    "videoUnmutes",  # V2
    "vtr",  # V2
    "vctr",  # V2
]


# 这些字段仅在video报表中存在
VIDEO_METRICS = [
    # "query",  # V2
    "viewableImpressions",  # V2
    "videoFirstQuartileViews",  # V2
    "videoMidpointViews",  # V2
    "videoThirdQuartileViews",  # V2
    "videoCompleteViews",  # V2
    "video5SecondViews",  # V2
    "video5SecondViewRate",  # V2
    "videoUnmutes",  # V2
    "vtr",  # V2
    "vctr",  # V2
]


# 这些类型的报表可以按相应的维度来细分出的报表
DEFAULT_REPORT_DIMENSIONAL = {
    "keywords": "query",  # search terms 搜索词
    "campaigns": "placement",  # placement location 展示位置
}

DEFAULT_CREATIVE_TYPE = [
    "video"
]


class SbReport(ZADOpenAPI):
    def request(self, record_type, report_date, metrics, segment=None, creative_type=None):
        """
        POST    /v2/hsa/{recordType}/report

        Request the creation of a performance report for all entities of a single type which have performance data to
        report. Record types can be: campaigns, adGroups, and keywords

        :param record_type: 枚举 ['campaigns', 'adGroups', 'keywords']
        :param report_date: 报表日期, 格式为: YYYYMMDD
        :param metrics: 列表对象，成员为报表指标，即导出字段；若 metrics=None, 则使用默认指标
        :param segment: [可选]
        :param creative_type: [可选]; 枚举 ['video']
        """

        path = '/v2/hsa/{record_type}/report'.format(record_type=record_type)

        if creative_type:
            metrics = list(set(metrics).intersection(set(AVAILABLE_VIDEO_REPORT_METRICS)))
            metrics = list(set(metrics + VIDEO_METRICS))

        if isinstance(metrics, (list, tuple)):
            metrics = ','.join(metrics)

        data = {
           'reportDate': report_date,
           'metrics': metrics
        }

        if segment:
            data['segment'] = segment

        if creative_type:
            data['creativeType'] = creative_type

        return self.post(path, data)

    def _get_metrics(self, metrics, default):
        if not metrics:
            metrics = default

        return metrics

    def campaigns(self, report_date, metrics=None, creative_type=None):

        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('campaigns'))

        return self.request('campaigns', report_date, metrics, creative_type=creative_type)

    def campaigns_video(self, report_date, metrics=None):
        """campaigns视频"""
        return self.campaigns(report_date, metrics=metrics, creative_type='video')

    def placements(self, report_date, metrics=None, creative_type=None):

        segment = DEFAULT_REPORT_DIMENSIONAL.get('campaigns')

        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('campaigns'))

        return self.request('campaigns', report_date, metrics, segment, creative_type)

    def placements_video(self, report_date, metrics=None):
        """placements视频"""
        return self.placements(report_date, metrics=metrics, creative_type='video')

    def ad_groups(self, report_date, metrics=None, creative_type=None):

        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('adGroups'))

        return self.request('adGroups', report_date, metrics, creative_type=creative_type)

    def ad_groups_video(self, report_date, metrics=None):
        """ad_groups视频"""
        return self.ad_groups(report_date, metrics=metrics, creative_type='video')

    def keywords(self, report_date, metrics=None, creative_type=None):

        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('keywords'))

        return self.request('keywords', report_date, metrics, creative_type=creative_type)

    def keywords_video(self, report_date, metrics=None):
        """keywords视频"""
        return self.keywords(report_date, metrics=metrics, creative_type='video')

    def keywords_query(self, report_date, metrics=None, creative_type=None):
        """
        search term report
        """

        segment = DEFAULT_REPORT_DIMENSIONAL.get('keywords')

        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('keywords'))

        # Not available for search term report.
        not_allow_metrics = [
            "targetingType",
            "targetingExpression",
            "targetId",  # Note that this field is not currently supported and will have an empty value.
            "targetingText",
            "attributedSales14dSameSKU",
            "attributedUnitsOrderedNewToBrand14d",
            "attributedOrdersNewToBrand14d",
            "attributedOrdersNewToBrandPercentage14d",
            "attributedSalesNewToBrand14d",
            "attributedUnitsOrderedNewToBrandPercentage14d",
            "unitsSold14d",
            "attributedOrderRateNewToBrand14d",
            "attributedSalesNewToBrandPercentage14d",
            "dpv14d",
            "attributedConversions14dSameSKU",
            "attributedDetailPageViewsClicks14d",
        ]

        metrics = list(set(metrics).difference(set(not_allow_metrics)))

        return self.request('keywords', report_date, metrics, segment, creative_type)

    def keywords_query_video(self, report_date, metrics=None):
        """queries视频"""
        return self.keywords_query(report_date, metrics=metrics, creative_type='video')

    def keywords_placement(self, report_date, metrics=None, creative_type=None):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('keywords'))
        return self.request('keywords', report_date, metrics, segment='placement', creative_type=creative_type)

    def keywords_placement_video(self, report_date, metrics=None):
        return self.keywords_placement(report_date, metrics=metrics, creative_type='video')

    def targets(self, report_date, metrics=None, creative_type=None):
        metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('targets'))
        return self.request('targets', report_date, metrics, creative_type=creative_type)

    def targets_video(self, report_date, metrics=None):
        return self.targets(report_date, metrics=metrics, creative_type='video')

    # Exception: Query segmentation is not supported for HSA targets reports
    # def targets_query(self, report_date, metrics=None, creative_type=None):
    #     """
    #     search term report
    #     """
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('targets'))
    #     not_allow_metrics = [
    #         "targetingType",
    #         "targetingExpression",
    #         "targetId",
    #         "targetingText",
    #         "attributedSales14dSameSKU",
    #         "attributedUnitsOrderedNewToBrand14d",
    #         "attributedOrdersNewToBrand14d",
    #         "attributedOrdersNewToBrandPercentage14d",
    #         "attributedSalesNewToBrand14d",
    #         "attributedUnitsOrderedNewToBrandPercentage14d",
    #         "unitsSold14d",
    #         "attributedOrderRateNewToBrand14d",
    #         "attributedSalesNewToBrandPercentage14d",
    #         "dpv14d",
    #         "attributedConversions14dSameSKU",
    #         "attributedDetailPageViewsClicks14d",
    #     ]
    #     metrics = list(set(metrics).difference(set(not_allow_metrics)))
    #     return self.request('targets', report_date, metrics, segment='query', creative_type=creative_type)

    # Exception: Segment '[PLACEMENT]' is not supported for 'targets' report for specified campaign type(s)
    # def targets_placement(self, report_date, metrics=None, creative_type=None):
    #     metrics = self._get_metrics(metrics, DEFAULT_REPORT_METRICS.get('targets'))
    #     return self.request('targets', report_date, metrics, segment='placement', creative_type=creative_type)

    def local_test(self, **kwargs):
        """
        测试用的接口
        """
        path = kwargs.get('path')
        data = kwargs.get('data')
        return self.post(path, data)
