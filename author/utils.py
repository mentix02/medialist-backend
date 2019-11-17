"""
Helper methods that aid in testing, writing views,
and meagre model querying stuff for the Author model.
"""
import json
import uuid
import typing

from author.models import Author
from author.serializers import AuthorListSerializer

from django.core.validators import EmailValidator
from django.core.exceptions import (
    ValidationError,
    ObjectDoesNotExist
)

from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from rest_framework.utils.serializer_helpers import ReturnDict


def is_available(username: str) -> bool:
    """
    Helper function to check username availability. Can be a 
    better way instead of trying to invoke an ObjectDoesNotExist
    exception. Not that I know of one yet.

    Another method could be to filter with username__exact and
    `return results or False` but that would return a QuerySet if
    Author was found, which in theory, should work but that would
    mean is_available doesn't return a boolean value. I could
    also do -
    ```
    return True if Author.objects.filter(username__exact=username) \
           else False
    ```

    After much testing, this method is, surprisingly, a little faster
    for checking the availability of a username. Thus, it will be used.
    """
    try:
        Author.objects.get(username__exact=username)
        return False
    except ObjectDoesNotExist:
        return True


def get_author_serialized_data(author: Author, token: bool = False) -> ReturnDict:
    """
    Similar to get_queried_author_serialized_data, except this
    takes in a direct Author instance and serializes it - in fact
    the queried method uses this function's logic to return its data.
    """

    data = AuthorListSerializer(author).data

    if token:
        # In a perfect world, this function
        # won't be called with token boolean
        # False since this will almost always
        # be utilized when an authenticated
        # request comes through - either
        # when Author is signing up or logging in.
        key = Token.objects.get(user__exact=author).key
        data['token'] = key

    return data


def get_queried_author_serialized_data(username: str, token: bool = False) -> ReturnDict:
    """
    Gets a dictionary-like object serialized by AuthorListSerializer
    by querying for a username. If an Author with provided username
    wasn't found, returns a static ReturnDict with an error message.
    An OrderedDict or even a dictionary can be used but for the sake
    of consistency and mypy's static checking, a ReturnDict is utilized
    since that's what serializer.data returns.
    """
    try:
        author = Author.objects.get(username=username)
        return get_author_serialized_data(author, token)
    except ObjectDoesNotExist:
        # Need to have a kwarg 'serializer'
        # since that's how rest_framework
        # is written - ReturnDict is just
        # OrderedDict but by having a back
        # link to the serializer as a data member.
        return ReturnDict(error='User not found.', serializer=None)


def get_json(response: Response) -> typing.Dict[typing.Any, typing.Any]:
    body = response.content.decode()
    return json.loads(body)


def auth_header(key: str) -> str:
    return 'Token {}'.format(key)


def is_valid_uuid(uuid_str: str) -> bool:
    """
    Copied shamelessly from http://bit.ly/33Omn1g.
    """
    try:
        uuid.UUID(uuid_str)
        return True
    except ValueError:
        return False


def is_valid_email(email: str) -> bool:
    """
    Simple email format validator using
    Django's internal email validator.
    """
    validator = EmailValidator()
    try:
        validator(email)
        # Since validator accepted email,
        return True
    except ValidationError:
        return False
