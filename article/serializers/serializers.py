from article.models import Article
from article.serializers.fields import TagListField
from author.serializers import AuthorDetailSerializer

from rest_framework import serializers


class ArticleListSerializer(serializers.ModelSerializer):
    tags = TagListField()
    topic = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    content = serializers.StringRelatedField(source='get_truncated_content')
    thumbnail = serializers.URLField(source='get_thumbnail')
    timestamp = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Article
        exclude = ('updated_on', 'created_on', 'thumbnail_url', 'draft')


class ArticleDetailSerializer(serializers.ModelSerializer):
    tags = TagListField()
    author = AuthorDetailSerializer()
    topic = serializers.StringRelatedField()
    thumbnail = serializers.URLField(source='get_thumbnail')
    timestamp = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Article
        exclude = ('created_on', 'updated_on', 'thumbnail_url', 'draft')
