"""
Tests for CRUD operations on views for the Topic model
with proper authentication and validation are written here.
"""
import typing

from django.shortcuts import reverse

from rest_framework.test import APITestCase
from rest_framework.response import Response

from backend import utils as u
from topic.models import Topic
from author.models import Author
from topic.tests.generators import create_topic
from author.tests.generators import create_author
from topic.serializers import (
    TopicListSerializer,
    TopicDetailSerializer
)

BASE_URL = '/api/topics/'


class TopicRetrieveAPIViewTest(APITestCase):
    """
    All views dealing with data retrieval regarding the
    Topic model are tested here. This includes topic lists,
    detail view, etc. Test data of 25 topics is chosen.
    An Author model instance is also conducted for aid in
    creations of said 25 topics.
    """

    @classmethod
    def setUpTestData(cls) -> None:

        # Create authors.
        cls.author: Author = create_author()

        # Create topics.
        cls.topics: typing.List[Topic] = list(reversed([
            create_topic(cls.author.id) for _ in range(25)
        ]))

    def test_topic_list_paginated(self) -> None:
        """
        Makes a request to /api/topics/ and checks for topics being
        properly paginated and in proper format.
        """
        page = 1
        for topic_index in range(0, 25, 10):
            response: Response = self.client.get(f'{reverse("topic:list")}?page={page}')
            data = u.get_json(response)
            results = data['results']

            current_page_topics = self.topics[topic_index:topic_index+10]
            serialized_current_page_topics = TopicListSerializer(current_page_topics, many=True).data

            self.assertEqual(results, serialized_current_page_topics)
            page += 1

    def test_topic_detail_view(self) -> None:
        """
        Simply makes requests to all reverse urls for topic details
        and compares serialized data against them.
        """

        for topic in self.topics:
            response: Response = self.client.get(topic.get_absolute_url())
            data = u.get_json(response)
            serialized_data = TopicDetailSerializer(topic).data
            self.assertEqual(data, serialized_data)
