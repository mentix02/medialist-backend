from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import post_save

from topic.models import Topic


# noinspection PyUnusedLocal
@receiver(post_save, sender=Topic)
def create_author_secret_key(sender, instance: Topic, **kwargs):
    slug = slugify(instance.name)
