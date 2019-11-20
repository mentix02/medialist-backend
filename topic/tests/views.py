"""
Tests for CRUD operations on views for the Topic model
with proper authentication and validation are written here.
"""
import random
import typing

from faker import Faker

from django.shortcuts import reverse
from django.core.exceptions import ObjectDoesNotExist

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.response import Response

from backend import utils as u
from topic.models import Topic
from author.models import Author
from author.utils import auth_header
from topic.tests.generators import create_topic
from author.tests.generators import create_author
from topic.serializers import (
    TopicListSerializer,
    TopicDetailSerializer
)

fake = Faker()
BASE_URL = '/api/topics'


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


class TopicCreationAPIViewTest(APITestCase):
    """
    Tests the TopicCreateAPIView with various invalid inputs (and valid).
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Make a temporary author to check make authenticated responses with.
        """
        cls.author = create_author()
        cls.data = {
            'name': fake.text(45)[:-1],
            'description': fake.text(150),
            'thumbnail_url': 'https://picsum.photos/id/271/1900/1080',
        }

    def test_unauthenticated_topic_creation(self):
        """
        Makes an unauthenticated request to /api/topics/create/ to 
        (hopefully) raise Unauthorized error.
        """
        response: Response = self.client.post(reverse('topic:create'))
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data, {'detail': 'Authentication credentials were not provided.'})

    def test_authenticated_topic_creation_with_incomplete_data(self):
        """
        Makes a properly authenticated request to /api/topics/create/ but
        with invalid (read: incomplete) data that should result in error.
        """

        self.client.credentials(HTTP_AUTHORIZATION=auth_header(self.author.get_key()))

        for field in self.data.keys():

            # Make a copy of the data so that
            # the original isn't changed because
            # every iteration will remove one
            # field - going through all.
            temp_data = self.data.copy()
            del temp_data[field]

            response: Response = self.client.post(reverse('topic:create'), data=temp_data)
            response_data = u.get_json(response)

            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)

            # Special case for thumbnail_url field since the
            # view (and Topic model) either expects a FILE
            # upload or an image url. For testing purposes,
            # we only work with placeholder image urls.
            if field == 'thumbnail_url':
                self.assertEqual(response_data, {
                    'detail': 'Either provide a url for a thumbnail or an image upload.'
                })
            else:
                self.assertEqual(response_data, {
                    'detail': f"Field '{field}' not provided."
                })

    def test_authenticated_topic_creation(self):
        """
        Makes a valid request to /api/topics/create/ with proper auth creds
        and valid (read: complete) POST data.
        """

        # Authenticate via header token
        self.client.credentials(HTTP_AUTHORIZATION=auth_header(self.author.get_key()))

        response: Response = self.client.post(reverse('topic:create'), data=self.data)
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Assert response with serialized last entry in Topic table
        self.assertEqual(data, TopicDetailSerializer(
            Topic.objects.last()
        ).data)


class TopicDeletionAPIViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:

        cls.authors: typing.List[typing.Tuple[int, Author]] = [
            (index, create_author()) for index in range(1, 3)
        ]

        # Create 4 topics, 2 by each author.
        cls.author_1_topics: typing.List[Topic] = [
            create_topic(cls.authors[0][1].pk) for _ in range(2)
        ]
        cls.author_2_topics: typing.List[Topic] = [
            create_topic(cls.authors[1][1].pk) for _ in range(2)
        ]
        cls.topics: typing.Set[Topic] = set(cls.author_1_topics + cls.author_2_topics)

    def test_unauthenticated_deletion(self):
        """
        Make unauthenticated request to /api/topics/delete/<slug:slug>/ to
        assert Unauthorized Error and apt response.
        """

        response: Response = self.client.delete(reverse('topic:delete', kwargs={
            'slug': random.choice(self.author_1_topics).slug
        }))
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data, {'detail': 'Authentication credentials were not provided.'})

    def test_invalid_permission_topic_deletion(self):
        """
        Make valid authorized delete requests to /api/topics/delete/<slug:slug>/
        to raise a Forbidden error with apt response.
        """

        for index, author in self.authors:

            # Authenticate delete request with current author
            self.client.credentials(HTTP_AUTHORIZATION=auth_header(author.get_key()))

            topics_not_by_author = self.topics.difference(getattr(self, f'author_{index}_topics'))

            for topic in topics_not_by_author:
                response: Response = self.client.delete(reverse('topic:delete', kwargs={
                    'slug': topic.slug
                }))
                data = u.get_json(response)
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
                self.assertEqual(data, {'detail': 'Deletion is not authorized.'})

    def test_valid_permission_topic_deletion(self):
        """
        Last test to run in this APITestCase - makes valid delete requests
        /api/topics/delete/<slug:slug>/ and compares status code and check
        for existence inside of database.
        """

        for index, author in self.authors:

            self.client.credentials(HTTP_AUTHORIZATION=auth_header(author.get_key()))
            topics_by_author = getattr(self, f'author_{index}_topics')

            for topic in topics_by_author:

                topic_slug = topic.slug

                response: Response = self.client.delete(reverse('topic:delete', kwargs={
                    'slug': topic_slug
                }))
                # No need to get data since a 204 response doesn't return anything.

                self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

                # Now check for data.
                with self.assertRaises(ObjectDoesNotExist):
                    Topic.objects.get(slug__iexact=topic_slug)
