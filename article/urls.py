from django.urls import path

from article.views import (
    ArticleDetailAPIView,
    ArticleCreateAPIView,
    RecentArticleListAPIView
)

app_name = 'article'

urlpatterns = (
    path('create/', ArticleCreateAPIView.as_view(), name='create'),
    path('recent/', RecentArticleListAPIView.as_view(), name='recent'),
    path('detail/<slug:slug>/', ArticleDetailAPIView.as_view(), name='detail'),
)
