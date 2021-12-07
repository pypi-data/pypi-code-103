from django.urls import path

from ..views.contentViews import *

urlpatterns = [
    path('statements/get/<int:id>/', ShowStatement.as_view(), name="show_statement"),
    path('statements/with/hashtag/', ShowStatementsWithHashtag.as_view(), name="show_statement_with_hashtag"),
    path('statements/feed/', ShowStatementFeed.as_view(), name="show_statement_feed"),
    path('statements/feed/pagination/', ShowStatementFeedPagination.as_view(), name="show_statement_feed_pagination"),
    path('trending/hashtag/', ShowTrendingHashtag.as_view(), name="show_trending_hashtags"),
]