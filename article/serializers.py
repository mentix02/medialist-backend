from article.models import Article

from rest_framework import serializers

from taggit_serializer import serializers as ts


class ArticleListSerializer(ts.TaggitSerializer, serializers.ModelSerializer):
    tags = ts.TagListSerializerField()
    topic = serializers.StringRelatedField()
    author = serializers.StringRelatedField()
    thumbnail = serializers.URLField(source='get_thumbnail')
    created_on = serializers.DateTimeField(format='%b. %d, %Y')
    uploaded_on = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Article
        fields = ('pk', 'title', 'created_on', 'uploaded_on', 'topic', 'author', 'tags', 'slug')
