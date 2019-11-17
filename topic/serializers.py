from topic.models import Topic

from rest_framework import serializers


class TopicListSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format='%b. %d, %Y')

    class Meta:
        model = Topic
        fields = ('pk', 'name', 'slug', 'created_on', 'uploaded_on'),
