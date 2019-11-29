from django.urls import path

from bookmark.views import (
    BookmarkAPIView,
    ArticleSortedByBookmarksAPIView,
    ArticleIDsSortedByAuthorBookmarkAPIView,
)

app_name = 'bookmark'

urlpatterns = (
    path('bookmark/', BookmarkAPIView.as_view(), name='bookmark'),
    path('list/', ArticleSortedByBookmarksAPIView.as_view(), name='list'),
    path('pk_list/', ArticleIDsSortedByAuthorBookmarkAPIView.as_view(), name='pk-list'),
)
