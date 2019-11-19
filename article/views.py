from article.models import Article
from article.serializers import ArticleListSerializer

from rest_framework.generics import ListAPIView


class RecentArticleListAPIView(ListAPIView):
    """
    Gets the last N number of articles to
    display in a list. Used for getting
    recently written Articles.
    """
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        N = self.request.GET.get('N', 12)
        articles = Article.objects.filter(draft=False)[N:]
        return articles
