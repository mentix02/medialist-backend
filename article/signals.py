from articles.models import Article
from articles.utils import generate_slug_for_article

from django.dispatch import receiver
from django.db.models.signals import pre_save


# noinspection PyUnusedLocal
@receiver(pre_save, sender=Article)
def generate_article_slug(sender, instance: Article, **kwargs):
    instance.slug = generate_slug_for_article(instance.title)
