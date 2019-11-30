"""
Helper utility functions.
"""
import json
import typing

from rest_framework.response import Response


def get_json(response: Response) -> typing.Dict[typing.Any, typing.Any]:
    body = response.content.decode()
    return json.loads(body)


def auth_header(key: str) -> str:
    return 'Token {}'.format(key)
