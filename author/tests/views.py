import random
import typing

import faker

from author import utils as u
from author.models import Author
from author.tests.generators import create_author
from author.serializers import AuthorListSerializer

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
    such as AuthorListAPIView or AuthorDetailAPIView. Currently it
    only uses the django.test.Client but future tests might include
    drf's APIClient. To be decided.
    """

    @classmethod
    def setUpTestData(cls):
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

    def test_author_list_equality_with_valid_authentication(self):
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

    def test_author_list_equality_with_invalid_authentication(self):
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


class AuthorCreationAPIViewTest(APITestCase):
    """
    Unit tests devoted entirely to testing of Author creation methods. These
    tests are written to have 100% coverage of the AuthorCreateAPIView view.
    """

    def test_author_registration_with_existing_username(self):
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

    def test_author_registration_with_invalid_data(self):
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
        # dollar sign. We dont' even need to send any more data since
        # the view immediately returns an invalid username error response.
        response = self.client.post(BASE_URL + '/create/', {
            'username': 'mentix 02$'
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
