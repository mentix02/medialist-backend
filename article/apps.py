from django.apps import AppConfig


class ArticleConfig(AppConfig):
    name = 'article'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from article.signals import generate_article_slug
