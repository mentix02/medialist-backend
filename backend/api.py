from django.urls import path, include

urlpatterns = (
    path('authors/', include('author.urls')),
    path('articles/', include('article.urls')),
)
