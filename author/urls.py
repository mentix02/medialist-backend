from django.urls import path

from author.views import (
    AuthorListAPIView,
    AuthorDetailAPIView,
    AuthorCreateAPIView,
    AuthorUpdateAPIView,
    AuthorVerifyAPIView,
    AuthorRetrieveTokenView,
    AuthorSortedTopicListAPIView,
    AuthorSortedArticleListAPIView
)

app_name = 'author'

urlpatterns = [
    path('', AuthorListAPIView.as_view(), name='list'),
    path('create/', AuthorCreateAPIView.as_view(), name='create'),
    path('update/', AuthorUpdateAPIView.as_view(), name='update'),
    path('authenticate/', AuthorRetrieveTokenView.as_view(), name='authenticate'),
    path('detail/<slug:username>/', AuthorDetailAPIView.as_view(), name='detail'),
    path('verify/<uuid:secret_key>/', AuthorVerifyAPIView.as_view(), name='verify'),
    path('detail/<slug:username>/topics/', AuthorSortedTopicListAPIView.as_view(), name='topics'),
    path('detail/<slug:username>/articles/', AuthorSortedArticleListAPIView.as_view(), name='articles')
]
