from article.models import Article
from article.serializers.fields import TagListField

from rest_framework import serializers


class ArticleListSerializer(serializers.ModelSerializer):
    tags = TagListField()
    topic = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    truncated_content = serializers.StringRelatedField()
    thumbnail = serializers.URLField(source='get_thumbnail')
    timestamp = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Article
        exclude = ('content', 'updated_on', 'created_on', 'thumbnail_url', 'draft')


class ArticleDetailSerializer(serializers.ModelSerializer):
    tags = TagListField()
    topic = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    thumbnail = serializers.URLField(source='get_thumbnail')
    timestamp = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Article
        exclude = ('created_on', 'updated_on', 'thumbnail_url', 'draft')
