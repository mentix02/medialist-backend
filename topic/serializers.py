from topic.models import Topic
from author.serializers import AuthorListSerializer

from rest_framework import serializers


class TopicListSerializer(serializers.ModelSerializer):

    author = serializers.StringRelatedField()
    thumbnail = serializers.URLField(source='get_thumbnail')
    created_on = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Topic
        fields = ('pk', 'name', 'slug', 'created_on', 'author', 'thumbnail')


class TopicDetailSerializer(serializers.ModelSerializer):

    author = AuthorListSerializer()
    thumbnail = serializers.URLField(source='get_thumbnail')
    created_on = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Topic
        exclude = ('thumbnail_url',)
