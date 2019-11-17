from django.urls import path, include

urlpatterns = (
    path('topics/', include('topic.urls')),
    path('authors/', include('author.urls')),
    path('articles/', include('article.urls')),
)
