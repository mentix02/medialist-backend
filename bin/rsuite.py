#!/usr/bin/env python3
from typing import Dict, List

import requests

BASE_URL = 'http://localhost:8000/api'

topic_url = f'{BASE_URL}/topics'
author_url = f'{BASE_URL}/authors'
article_url = f'{BASE_URL}/articles'
bookmark_url = f'{BASE_URL}/bookmark'

topics: Dict[str, str] = {
    'list': f'{topic_url}/',
    'create': f'{topic_url}/create/',
    'delete': f'{topic_url}/delete/',
    'detail': topic_url + '/detail/{}/'
}

authors: Dict[str, str] = {
    'list': f'{author_url}/',
    'create': f'{author_url}/create/',
    'auth': f'{author_url}/authenticate/',
}

bookmarks: Dict[str, str] = {
    'list': f'{bookmark_url}/list/',
    'create': f'{bookmark_url}/bookmark/',
}

articles: Dict[str, str] = {
    'create': f'{article_url}/create/'
}


def get_bookmarks(username: str) -> List[Dict[str, str]]:
    return requests.get(bookmarks['list'], headers=get_auth_header(username)).json()


def create_bookmark(username: str, article_id: int) -> Dict[str, Dict[str, str]]:
    return requests.post(bookmarks['create'], data={'article_id': article_id}, headers=get_auth_header(username))


def get_topics() -> Dict[str, str]:
    r = requests.get(topics['list'])
    return r.json()


def get_topic(slug: str) -> Dict[str, str]:
    r = requests.get(topics['detail'].format(slug))
    return r.json()


def get_auth_header(username: str = 'mentix02', password: str = 'abcd1432') -> Dict[str, str]:
    r = requests.post(authors['auth'], data=locals())
    assert r.status_code == 200, 'Invalid credentials.'
    return {'Authorization': f'Token {r.json().get("token")}'}


def f_topic(name: str, description: str, thumbnail_url: str) -> Dict[str, str]:
    return locals()


def f_author(username: str, email: str, first_name: str, password: str, bio: str) -> Dict[str, str]:
    return locals()


def f_article(title: str, content: str, topic: int, thumbnail_url: str) -> Dict[str, str]:
    return locals()


def create_topic(username: str, *args):
    return requests.post(topics['create'], data=f_topic(*args), headers=get_auth_header(username))


def create_author(*args):
    return requests.post(authors['create'], data=f_author(*args))


def create_article(username: str, *args):
    return requests.post(articles['create'], data=f_article(*args), headers=get_auth_header(username))
