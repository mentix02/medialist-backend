from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import pre_save

from topic.models import Topic


# noinspection PyUnusedLocal
@receiver(pre_save, sender=Topic)
def generate_topic_slug(sender, instance: Topic, **kwargs):
    instance.slug = slugify(instance.name)
