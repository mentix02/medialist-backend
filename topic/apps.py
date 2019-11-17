from django.apps import AppConfig


class TopicConfig(AppConfig):
    name = 'topic'

    def ready(self):
        # noinspection PyUnresolvedReferences
        from topic.signals import generate_topic_slug
