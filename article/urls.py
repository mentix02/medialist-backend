from article.views import RecentArticleListAPIView

from django.urls import path

app_name = 'article'

urlpatterns = (
    path('recent/', RecentArticleListAPIView.as_view(), name='recent'),
)
