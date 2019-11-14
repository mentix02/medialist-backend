from django.urls import path

from author.views import (
    AuthorListAPIView,
    AuthorDetailAPIView,
    AuthorCreateAPIView,
    AuthorAuthenticateAPIView
)

app_name = 'author'

urlpatterns = [
    path('', AuthorListAPIView.as_view(), name='list'),
    path('create/', AuthorCreateAPIView.as_view(), name='create'),
    path('detail/<slug:username>/', AuthorDetailAPIView.as_view(), name='detail'),
    path('activate/<str:secret_key>/', AuthorAuthenticateAPIView.as_view(), name='activate'),
]
