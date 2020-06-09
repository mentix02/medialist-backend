from article.models import Article
from clarent.clarent import Clarent

from django.dispatch import receiver
from django.utils.text import slugify
from django.db.models.signals import pre_save


# noinspection PyUnusedLocal
@receiver(pre_save, sender=Article)
def generate_article_slug(sender, instance: Article, **kwargs):
    instance.slug = slugify(instance.title)
    instance.objectivity = Clarent(instance.content).objectivity
