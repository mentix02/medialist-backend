import random
import backend.utils as u
from typing import List

from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from article.models import Article
from bookmark.models import Bookmark
from topic.tests.generators import create_topic
from author.tests.generators import create_author
from article.tests.generators import create_article
from article.serializers import ArticleListSerializer


class BookmarkCreationAndDeletionTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = create_author()
        cls.topic = create_topic(cls.author.pk)
        cls.articles: List[Article] = [
            create_article(topic_id=cls.topic.id, author_id=cls.author.id, draft=False)
            for _ in range(5)
        ]

    def test_unauthenticated_bookmark_creation(self):

        article: Article = random.choice(self.articles)

        response = self.client.post(reverse('bookmark:bookmark'), data={
            'article_id': article.id
        })
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data, {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_authenticated_bookmark_creation(self):
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))
        article: Article = random.choice(self.articles)

        self.bookmarked_article_id = article.id

        response = self.client.post(reverse('bookmark:bookmark'), data={
            'article_id': article.id
        })
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED, msg=data)
        self.assertEqual(data, {
            'detail': {
                'action': 'created'
            }
        })

    def test_authenticated_bookmark_deletion(self):
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))
        bookmark, _ = Bookmark.objects.get_or_create(
            author=self.author, article=random.choice(self.articles)
        )
        bookmarked_article_id = bookmark.article_id

        response = self.client.post(reverse('bookmark:bookmark'), data={
            'article_id': bookmarked_article_id
        })
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, {
            'detail': {
                'action': 'deleted'
            }
        })

    def test_incomplete_form_data_post(self):
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))
        response = self.client.post(reverse('bookmark:bookmark'))
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(data, {
            'detail': "Field 'article_id' not provided."
        })

    def test_invalid_article_pk_bookmark_creation(self):
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))
        response = self.client.post(reverse('bookmark:bookmark'), data={
            'article_id': Article.objects.first().id + random.randint(1, 10)            
        })
        data = u.get_json(response)
        self.assertEqual(response.status_code, 404)
        self.assertEqual(data, {
            'detail': 'Article does not exist.'
        })


class BookmarkRelatedRetrievalViewsTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = create_author()
        cls.topic = create_topic(cls.author.pk)
        cls.articles: List[Article] = [
            create_article(topic_id=cls.topic.id, author_id=cls.author.id, draft=False)
            for _ in range(5)
        ]

    def test_get_articles_author_bookmarked_test(self):
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))
        response = self.client.get(reverse('bookmark:list'))
        data = u.get_json(response)

        author_bookmarked_articles = [
            bookmark.article for bookmark in self.author.bookmarks.all()
        ]
        serialized_data = ArticleListSerializer(author_bookmarked_articles, many=True).data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['results'], serialized_data)

    def test_get_articles_ids_author_bookmarked_test(self):
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))
        response = self.client.get(reverse('bookmark:pk-list'))
        data = u.get_json(response)

        author_bookmarked_articles_ids = [
            bookmark.article.id for bookmark in self.author.bookmarks.all()
        ]

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data, author_bookmarked_articles_ids)
