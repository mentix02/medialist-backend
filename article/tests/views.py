import random

from backend import utils as u

from django.shortcuts import reverse

from article.models import Article
from topic.tests.generators import create_topic
from author.tests.generators import create_author
from article.tests.generators import create_article
from article.serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer
)

from rest_framework import status
from rest_framework.test import APITestCase


class ArticleRetrievalTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = create_author()

        cls.topics = [create_topic(cls.author.pk) for _ in range(3)]

        cls.articles = [create_article(
            draft=False,
            author_id=cls.author.id,
            topic_id=random.choice(cls.topics).id,
        ) for _ in range(5)]

        create_article(
            topic_id=random.choice(cls.topics).id,
            author_id=cls.author.id,
            draft=True
        )

    def test_recent_article_retrieval(self):

        response = self.client.get(reverse('article:recent'))
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(data), Article.objects.filter(draft=False).count())

        serialized_data = ArticleListSerializer(
            Article.objects.filter(draft=False), many=True
        ).data
        self.assertEqual(data, serialized_data)

    def test_article_detail_retrieval(self):

        article = random.choice(self.articles)

        response = self.client.get(reverse('article:detail', kwargs={
            'slug': article.slug
        }))
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        serialized_data = ArticleDetailSerializer(
            Article.objects.get(pk=article.pk)
        ).data
        self.assertEqual(data, serialized_data)
