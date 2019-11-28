from article.models import Article
from article.serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer
)

from rest_framework.generics import ListAPIView, RetrieveAPIView


class RecentArticleListAPIView(ListAPIView):
    """
    Gets the last N number of articles to display in a list. Used
    for getting recently written Articles that aren't drafts.
    """
    pagination_class = None
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        N = self.request.GET.get('N', 12)
        articles = Article.objects.filter(draft=False)[:N]
        return articles


class ArticleDetailAPIView(RetrieveAPIView):
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    serializer_class = ArticleDetailSerializer
    queryset = Article.objects.filter(draft=False)
