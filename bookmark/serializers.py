from bookmark.models import Bookmark
from article.serializers import ArticleListSerializer

from rest_framework.serializers import ModelSerializer


class BookmarkSerializer(ModelSerializer):

    article = ArticleListSerializer()

    class Meta:
        model = Bookmark
        fields = ('article',)
