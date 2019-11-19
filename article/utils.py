from django.db.models import QuerySet
from django.utils.text import slugify

from article.models import Article


def generate_slug_for_article(article: Article, new_slug: str = None) -> str:
    """
    Reads the title field from the provided article and generates
    a unique slug using recursion. This method should be called inside
    of the signals.py to generate a slug for each article as it's
    created.
    """

    # Create a slug from the article name provided
    slug = slugify(article.name)

    if new_slug is not None:
        # If function was called recursively
        # assign the slug to test itself against
        # the queryset of Article with matching slugs.
        slug = new_slug

    # Query database for Article by
    # slug and order by primary key
    # to get the last Article.
    qs: QuerySet = Article.objects.filter(slug=slug).order_by('-pk')
    exists = qs.exists()

    if exists:
        # If the query set returns something
        # then append the pk of the last Topic
        # to the current instance's name.
        new_slug = '{}-{}'.format(slug, qs.first().pk)
        return generate_slug_for_article(topic, new_slug)

    return slug
