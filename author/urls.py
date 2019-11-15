from django.urls import path

from author.views import (
    AuthorListAPIView,
    AuthorDetailAPIView,
    AuthorCreateAPIView,
    AuthorUpdateAPIView,
    AuthorAuthenticateAPIView
)

app_name = 'author'

urlpatterns = [
    path('', AuthorListAPIView.as_view(), name='list'),
    path('create/', AuthorCreateAPIView.as_view(), name='create'),
    path('update/<slug:username>/', AuthorUpdateAPIView.as_view(), name='update'),
    path('detail/<slug:username>/', AuthorDetailAPIView.as_view(), name='detail'),
    path('verify/<uuid:secret_key>/', AuthorAuthenticateAPIView.as_view(), name='verify'),
]
