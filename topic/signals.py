from django.dispatch import receiver
from django.db.models.signals import post_save

from topic.models import Topic
from topic.utils import generate_slug_for_topic


# noinspection PyUnusedLocal
@receiver(post_save, sender=Topic)
def create_author_secret_key(sender, instance: Topic, **kwargs):
    slug = generate_slug_for_topic(instance)
