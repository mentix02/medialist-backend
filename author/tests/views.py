import uuid
import random
import typing

import faker

from author import utils as u
from author.models import Author
from topic.tests.generators import create_topic
from author.tests.generators import create_author
from topic.serializers import TopicListSerializer
from author.serializers import AuthorListSerializer
from article.tests.generators import create_article
from article.serializers import ArticleListSerializer

from django.shortcuts import reverse

from rest_framework import status
from rest_framework.test import APITestCase
from rest_framework.response import Response

# Set up a global fake factory
# and base url for testing.
fake = faker.Faker()
BASE_URL = '/api/authors'


class AuthorRetrieveAPIViewTest(APITestCase):
    """
    Simple unit tests for checking authentication, data formatting,
    and basic functionality for any Author based retrieval views
    such as AuthorListAPIView or AuthorDetailAPIView. It's an APITestCase
    provided by drf and that means that it uses the APIClient to make
    requests. That's a huge advantage because that lets us use token
    authentication in an easy way instead of doing some monkey patching
    magic.
    """

    @classmethod
    def setUpTestData(cls) -> None:
        """
        Creates a list of fake authors using author.tests.generators'
        generate_author() and compares the JSON result from AuthorListAPIView
        by testing valid and invalid authenticated requests. Also used
        for testing AuthorDetailAPIView that compares the author details.
        """

        # Define base url
        cls.url = BASE_URL + '/'

        # Make 9 "normal" authors.
        cls.authors: typing.List[Author] = [
            create_author() for _ in range(9)
        ]

        # Make 1 superuser author.
        cls.super_author: Author = create_author(True)

        # Serialize data once so that it's not called in ever test
        cls.serialized_data = AuthorListSerializer(Author.objects.all(), many=True).data

    def test_author_list_equality_with_valid_authentication(self) -> None:
        """
        Makes a valid (authenticated) request to /api/authors/ to compare list
        results with AuthorListSerializer serialized queryset data. Should return
        with a status code 200. Request is authenticated with authtoken for the
        super_author account inside of the Header.
        """

        # Set the Authorization header to the appropriate
        # format as the rest_framework expects using utils.
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(
            self.super_author.get_key()
        ))

        response = self.client.get(self.url)
        data = u.get_json(response)

        self.assertEqual(data, self.serialized_data, msg=data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_author_list_equality_with_invalid_authentication(self) -> None:
        """
        Similar to the previous test except the request sent to /api/authors/
        is invalid with improper permissions - once with an Author with no
        permissions and once with no authentication headers at all.
        """

        # Let's check for a request with no authorization

        response: Response = self.client.get(self.url)
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(data, {
            'detail': 'Authentication credentials were not provided.'
        })

        # Now lets check with an Author without permissions.

        # Select the underprivileged author randomly.
        author: Author = random.choice(self.authors)

        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(author.get_key()))

        response: Response = self.client.get(self.url)
        data: typing.Dict[typing.Any, typing.Any] = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(data, {
            'detail': 'You do not have permission to perform this action.'
        })

    def test_valid_authentication(self):
        """
        Makes a valid POST request to /api/authors/authenticate/ by provided
        a valid username & password combo and compares authtoken provided to
        the one in the database.
        """

        for author in self.authors + [self.super_author]:
            response: Response = self.client.post(BASE_URL + '/authenticate/', data={
                'username': author.username,
                'password': 'abcd1432'  # Might be a better way to store random passwords.
            })
            data = u.get_json(response)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(data, {
                'token': author.get_key()
            })

    def test_invalid_authentication(self):
        """
        Similar to test_valid_authenticate except this tests for invalid
        credentials and incomplete data. Easy.
        """

        # Test for incomplete data.
        for field in ('username', 'password'):
            response: Response = self.client.post(BASE_URL + '/authenticate/', data={
                field: random.choice(self.authors).username  # Random value because it doesn't really matter
            })
            data = u.get_json(response)

            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertEqual(data, {
                'detail': f"Field '{'password' if field.startswith('u') else 'username'}' not provided."
            })

        # Test for invalid password
        for author in self.authors + [self.super_author]:
            response = self.client.post(BASE_URL + '/authenticate/', data={
                'username': author.username,
                'password': 'aaaaabbbbccccdd' # invalid password
            })
            data = u.get_json(response)

            self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
            self.assertEqual(data, {
                'detail': 'Invalid credentials.'
            })


class AuthorCreationAPIViewTest(APITestCase):
    """
    Unit tests devoted entirely to testing of Author creation methods. These
    tests are written to have 100% coverage of the AuthorCreateAPIView view.
    """

    def test_author_registration_with_existing_username(self) -> None:
        """
        Makes a request to /api/authors/create/ to create a user but
        expects failure because we'll provide a username that already
        exists in the database by picking an Author randomly from db.
        """

        # Create a fake test Author
        author: Author = create_author()

        # Construct POST request with taken username
        response: Response = self.client.post(BASE_URL + '/create/', {
            'password': 'abcd1432',
            'bio': fake.text(120),
            'email': fake.email(),
            'username': author.username,
            'first_name': fake.first_name(),
        })

        data: typing.Dict[typing.Any, typing.Any] = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(data, {
            'detail': f"User '{author.username}' already exists."
        })

    def test_author_registration_with_invalid_data(self) -> None:
        """
        Makes invalid requests to /api/authors/create/ by sending incomplete
        or poorly formatted data - such as having a space in a username or not
        including a required param in the POST body. Takes care of two error
        responses in one test case.
        """

        # First check without any parameters. It should return with an
        # error message for the username field since that's what the view
        # tried to check for first - before anything else.
        response: Response = self.client.post(BASE_URL + '/create/')
        data: typing.Dict[typing.Any, typing.Any] = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(data, {
            'detail': "Field 'username' not provided."
        })

        # Now check with an invalid username - one having a space and a
        # dollar sign. We dont' even need to send any more data (other than email)
        # since the view immediately returns an invalid username (or email) error
        # if they (email and username) aren't valid.
        response = self.client.post(BASE_URL + '/create/', {
            'username': 'mentix 02$',
            'email': 'manan.yadav02@gmail.com'
        })
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
        self.assertEqual(data, {
            'detail': 'Requires 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
        })

        post_data = {
            'bio': fake.text(120),
            'email': fake.email(),
            'password': 'abcd1432',
            'username': fake.user_name(),
            'first_name': fake.first_name(),
        }

        # Now check with two missing fields - password and bio.
        for missing_field in ['bio', 'password']:

            # Make a local for loop specific copy
            # to delete required missing field.
            d = post_data.copy()
            del d[missing_field]

            response = self.client.post(BASE_URL + '/create/', d)
            data = u.get_json(response)

            # It should raise a 'bio' field error since that's entered into the data
            # dictionary that's passed as params to the create() Author method first.
            self.assertEqual(response.status_code, status.HTTP_422_UNPROCESSABLE_ENTITY)
            self.assertEqual(data, {
                'detail': f"Field '{missing_field}' not provided."
            })


class AuthorAuthenticateAPIViewTest(APITestCase):
    """
    Simply for testing the verification view for the Author model.
    The methods for verifying and promoting have already been tested
    inside of the authors/tests/models.py tests so this is just for
    testing the working of the view rather than the model.methods themselves.
    """

    def setUp(self) -> None:
        self.author: Author = Author.objects.create_user(
            'mentix02',
            'manan.yadav02@example.com',
            'abcd1432',
            first_name='Manan',
            bio='I like to code so I wrote this site.'
        )

    def test_verification_with_valid_token(self) -> None:
        """
        Makes a valid request to a valid URL for verification of new Author
        account with the secret_key inside the URL. Writing this makes me
        think if I should just use the authtoken.key as the secret_key - instead
        of manually generating a UUID from scratch every time an Author is saved,
        I'd just need to regenerate a new authtoken. That might have several
        disadvantages - the authtoken would be made public to the Author and a
        hacker (not in a bad sense) might try to develop his / her own hacks. I
        think I'll keep secret_key as a custom UUID field thing.
        """

        secret_key = str(self.author.secret_key)
        verification_url = reverse('author:verify', kwargs={'secret_key': str(secret_key)})

        # Make sure URL's don't change.
        self.assertEqual(verification_url, f'/api/authors/verify/{secret_key}/')

        # Make valid request and get response
        response: Response = self.client.get(verification_url)

        self.assertEqual(response.status_code, 302)

        # Now test if the method "verify" was called
        self.assertEqual(Author.objects.get().verified, True)
        # We don't wanna give him too many privileges
        self.assertEqual(self.author.is_staff, False)

    def test_verification_with_invalid_token(self) -> None:
        """
        Makes a valid request to an invalid URL containing the secret_key that
        does not belong to any existing Author. This should result in nothing
        but an error response with status code 404.
        """

        uuids: typing.List[str] = []
        for i in range(2, 5):
            uuids.append(str(uuid.uuid5(
                uuid.uuid1(1),
                f'abcd123456{i}'
            )))

        for temp_uuid in uuids:
            response: Response = self.client.get(f'/api/authors/verify/{temp_uuid}/')
            data = u.get_json(response)
            self.assertEqual(response.status_code, 404)
            self.assertEqual(data, {
                'detail': 'Not found.'
            })


class AuthorUpdateAPIViewTest(APITestCase):

    @classmethod
    def setUpTestData(cls):
        cls.author: Author = Author.objects.create_user(
            'mentix02',
            'manan.yadav02@example.com',
            'abcd1432',
            first_name='Manan',
            bio='I like to code so I wrote this site.'
        )
        cls.key = cls.author.get_key()

        # Read why this is constructed inside of the
        # test_invalid_update_request_with_take_username
        # test case. Only username is required but it's
        # more reliable this way to populate fields.
        cls.temporary_author = Author.objects.create_user(
            'aryan_something',
            'aryan_something@example.com',
            'abcd1432',
            first_name='Aryan',
            bio='Play football and blah blah yada.'
        )

    def test_invalid_update_request_with_taken_username(self):
        """
        Tests to update an Author instance with a username that has already
        been taken - in this case, the username of the second author constructed
        only for this test case inside of the setUpTestData because it will be
        deleted once the test case finishes running automatically by Django. This
        should raise a 409 error with same error message as AuthorCreateAPIView.

        tl;dr - this makes an authenticated request to update mentix02's Author
        instance but with a username that already belongs to another user (the
        cls.temporary_author) - that returns an error and this test cases verifies.
        """
        self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(self.author.get_key()))
        response: Response = self.client.patch(BASE_URL + '/update/', data={
            'username': self.temporary_author.username
        })
        data = u.get_json(response)

        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT, msg=data)
        self.assertEqual(data, {'detail': f"User '{self.temporary_author.username}' already exists."})

    def test_valid_update_request(self):

        bio = fake.text(120)
        username = fake.user_name()
        first_name = fake.first_name()

        # Changes different fields in a loop.
        data: typing.Dict[str, str] = {
            'bio': bio,
            'username': username,
            'first_name': first_name,
        }

        for field, value in data.items():
            # Update the authorization header for every field because the
            # because with every update, a new authtoken is generated for
            # the user and the previous one is rendered invalid. The self.
            # author instance is refreshed from database at end of this loop
            # because then it's also updated and .save() has been called.
            self.client.credentials(HTTP_AUTHORIZATION=u.auth_header(
                self.author.get_key()
            ))

            # Make actual response and get back JSON data. Hopefully,
            # no errors are raised since the AuthorUpdateAPIView doesn't
            # implement a lot of sanity checks or exception handling.
            response: Response = self.client.patch(BASE_URL + '/update/', data={
                field: value
            })

            # Refresh author instance.
            self.author.refresh_from_db()

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(getattr(self.author, field), value)


class AuthorSortedDataTest(APITestCase):
    """
    Tests for checking views for data that is grouped together
    by their Author foreign key instances - data includes articles
    and topics.
    """

    @classmethod
    def setUpTestData(cls):
        cls.author_1 = create_author()
        cls.author_2 = create_author()

        cls.topics_by_author_1 = [
            create_topic(cls.author_1.id) for _ in range(2)
        ]
        cls.topics_by_author_2 = [
            create_topic(cls.author_2.id) for _ in range(2)
        ]

        cls.articles_by_author_1 = [
            create_article(author_id=cls.author_1.id, topic_id=random.choice(
                [topic.pk for topic in cls.topics_by_author_2 + cls.topics_by_author_1]
            )) for _ in range(5)
        ]
        cls.articles_by_author_2 = [
            create_article(author_id=cls.author_2.id, topic_id=random.choice(
                [topic.pk for topic in cls.topics_by_author_1 + cls.topics_by_author_2]
            )) for _ in range(5)
        ]

    def make_test(self, model_type: str, model_serializer, url_name: str):
        """
        A custom generic test maker to not duplicate the same code over
        and over - it takes a model_type that is a string of model types.
        It could be "articles" or "topics" so that a getattr call can
        get the data members from some string formatting as the variables
        are named following a certain syntax. Then it makes a GET request
        to the url_name that was provided with the apt parameters (in this
        case, the username). Then it's simply a matter of asserting cases.
        """

        for author_id in [1, 2]:
            username = getattr(self, f'author_{author_id}').username

            instances = getattr(self, f'{model_type}_by_author_{author_id}')
            instances_data = model_serializer(instances, many=True).data

            response = self.client.get(reverse(url_name, kwargs={
                'username': username
            }))
            data = u.get_json(response)

            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.assertEqual(data['count'], len(instances_data))

    def test_author_sorted_topics(self):
        """
        Make requests to /api/authors/detail/<username>/topics/ and get all
        the topics by a particular author in JSON format. Simple.
        """

        self.make_test('topics', TopicListSerializer, 'author:topics')

    def test_author_sorted_articles(self):
        """
        Similar to test_author_sorted_topics except for Article model.
        """

        self.make_test('articles', ArticleListSerializer, 'author:articles')
