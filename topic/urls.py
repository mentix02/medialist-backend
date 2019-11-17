from django.urls import path

from topic.views import (
    TopicListAPIView,
    TopicDetailAPIView,
    TopicCreateAPIView,
)

app_name = 'topic'

urlpatterns = [
    path('', TopicListAPIView.as_view(), name='list'),
    path('create/', TopicCreateAPIView.as_view(), name='create'),
    path('detail/<slug:slug>/', TopicDetailAPIView.as_view(), name='detail')
]