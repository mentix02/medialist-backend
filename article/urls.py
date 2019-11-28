from django.urls import path

from article.views import (
    ArticleDetailAPIView,
    RecentArticleListAPIView
)

app_name = 'article'

urlpatterns = (
    path('recent/', RecentArticleListAPIView.as_view(), name='recent'),
    path('detail/<slug:slug>/', ArticleDetailAPIView.as_view(), name='detail'),
)
