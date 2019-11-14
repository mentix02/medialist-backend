from django.apps import AppConfig


class AuthorConfig(AppConfig):
    name = 'author'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from author.signals import create_author_secret_key_and_send_auth_email
