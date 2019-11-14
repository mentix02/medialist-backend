from article.views import RecentArticleListAPIView

from django.urls import path

app_name = 'article'

urlpatterns = (
    path('', RecentArticleListAPIView.as_view(), name='list'),
)
