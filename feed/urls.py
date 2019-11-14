from django.urls import path

from feed.views import index

app_name = 'feed'

urlpatterns = [
    path('', index, name='index')
]
