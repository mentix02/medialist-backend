from django.urls import path

from topic.views import (
    TopicListAPIView,
    TopicDetailAPIView,
    TopicDeleteAPIView,
    TopicCreateAPIView,
    TopicSortedArticlesAPIView,
)

app_name = 'topic'

urlpatterns = [
    path('', TopicListAPIView.as_view(), name='list'),
    path('create/', TopicCreateAPIView.as_view(), name='create'),
    path('delete/<slug:slug>/', TopicDeleteAPIView.as_view(), name='delete'),
    path('detail/<slug:slug>/', TopicDetailAPIView.as_view(), name='detail'),
    path('detail/<slug:slug>/articles/', TopicSortedArticlesAPIView.as_view(), name='articles')
]
