import random
import typing
import itertools

from backend import utils as u

from django.utils import lorem_ipsum
from django.shortcuts import reverse

from topic.models import Topic
from article.models import Article
from author.tests.generators import create_author
from article.tests.generators import create_article
from topic.tests.generators import (
    create_topic,
    THUMBNAIL_URL_IDs
)
from article.serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer
)

from taggit.models import Tag
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
        self.assertEqual(len(data['results']), Article.objects.filter(draft=False).count())

        serialized_data = ArticleListSerializer(
            Article.objects.filter(draft=False), many=True
        ).data
        self.assertEqual(data['count'], Article.objects.filter(draft=False).count())
        self.assertEqual(data['results'], serialized_data)

    def test_limit_exceeding_recent_article(self):
        n = random.randint(21, 100)
        response = self.client.get(f"{reverse('article:recent')}?n={n}")
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
        self.assertEqual(data['detail'], "Can't retrieve more than 20 articles.")

    def test_invalid_n_recent_articles_param(self):
        for n in ['abcd', '34e1', '0x3', '3.01', '301ea']:
            response = self.client.get(f"{reverse('article:recent')}?n={n}")
            data = u.get_json(response)

            self.assertEqual(response.status_code, status.HTTP_406_NOT_ACCEPTABLE)
            self.assertEqual(data['detail'], 'Invalid value for n provided.')

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

    def test_article_sorted_by_tags_retrieval(self):
        """
        Makes a combination of half of the tags in the test database and
        tests the articles that contain them - half was used because it's
        "good enough" to test for all the articles in all probability.
        """
        tags: typing.List[str] = [tag.name for tag in Tag.objects.all()]
        tags_combinations = set()

        for r in range(1, int(len(tags) // 2)):
            tags_combinations |= set(itertools.combinations(tags, r))

        for tag_c in tags_combinations:
            url = f'{reverse("article:tags")}?tags={",".join(tag_c)}'

            response = self.client.get(url)
            data = u.get_json(response)

            articles = Article.objects.filter(draft=False)
            for tag in tag_c:
                articles = articles.filter(tags__name__in=[tag]).distinct()

            serialized_data = ArticleListSerializer(articles, many=True).data

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(data['results'], serialized_data)

        # Test for when the GET argument "tags" isn't provided.
        response = self.client.get(reverse('article:tags'))
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(data['results'], [])


class ArticleCreationTest(APITestCase):

    @classmethod
    def setUpTestData(cls) -> None:
        cls.author = create_author()
        cls.author.verify()
        cls.topics = [create_topic(cls.author.pk) for _ in range(3)]
        cls.article_data = {
            'title': 'Hello World',
            'tags': 'hello,world',
            'content': lorem_ipsum.paragraphs(4),
            'topic_id': random.choice(cls.topics).id,
            'thumbnail_url': 'https://picsum.photos/id/'
                             f'{random.choice(THUMBNAIL_URL_IDs)}'
                             '/1900/1080/',
        }

    def test_unauthenticated_article_creation(self):
        """
        Makes an unauthenticated request to /api/articles/create/ and
        asserts proper output with error messages.
        """

        # No need to provided data since the view would return
        # an error response without reading the POST request's data.
        response = self.client.post(reverse('article:create'))
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data, {
            'detail': 'Authentication credentials were not provided.'
        })

    def test_authenticated_article_creation_invalid_data(self):
        """
        Make a valid authenticated request to /api/articles/create/ with
        incomplete (read: invalid) data and check for error messages.
        """

        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))

        for field in self.article_data:
            d = self.article_data.copy()
            del d[field]

            response = self.client.post(reverse('article:create'), data=d)
            data = u.get_json(response)

            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            if field != 'thumbnail_url':
                self.assertEqual(data, {
                    'detail': f"Field '{field}' not provided."
                })
            else:
                self.assertEqual(data, {
                    'detail': 'Either provide a url for an article thumbnail or an image upload.'
                })

    def test_authenticated_article_creation(self):
        """
        Finally test proper creation.
        """

        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))

        response = self.client.post(reverse('article:create'), data=self.article_data)
        data = u.get_json(response)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(data, ArticleDetailSerializer(
            Article.objects.first()
        ).data)

    def test_authenticated_article_creation_with_existing_name(self):
        """
        Due to the order of how the tests run, the test_authenticated_article_creation
        should run before this test but for some reason the test database isn't populated
        with the article created in the former test case. Thus, a new article is created
        with the same data as self.article_data and
        """

        # Create an Article
        Article.objects.create(**self.article_data)

        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))

        response = self.client.post(reverse('article:create'), data=self.article_data)
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(data, {
            'detail': f"Article with title '{self.article_data['title']}' exists."
        })

    def test_article_creation_with_invalid_topic_id(self):
        """
        Pretty self explanatory - test with valid creds and data but for
        a Topic instance that doesn't exist - with an id.
        """
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))

        article_data = self.article_data.copy()
        article_data['topic_id'] = Topic.objects.first().id + 10

        response = self.client.post(reverse('article:create'), data=article_data)
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(data, {
            'detail': 'Topic not found.'
        })
