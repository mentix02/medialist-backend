"""
Global helper utility functions.
"""
import json
import typing

from rest_framework.response import Response


def get_json(response: Response) -> typing.Dict[typing.Any, typing.Any]:
    body = response.content.decode()
    return json.loads(body)


def auth_header(key: str) -> str:
    return 'Token {}'.format(key)


def replace(text: str, chars: typing.Iterable[str], value: str = '') -> str:
    """
    Replaces all character in a string with
    provided value and returns new string.
    """
    text  = list(text)
    chars = set(chars)
    for index in range(len(text)):
        if text[index] in chars:
            text[index] = value
    return ''.join(text)
