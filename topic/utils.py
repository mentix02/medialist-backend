import logging

from django.db.models import QuerySet
from django.utils.text import slugify

from topic.models import Topic

logger = logging.getLogger(__name__)


def generate_slug_for_topic(topic: Topic, new_slug: str = None) -> str:
    """
    NOTE - this method is now defunct and is kept for archival
    purposes since the name and slug field for the Topic model
    have now been configured with the unique value as True -
    therefore there's no point in having a complex recursive
    function just to generate slugs when the names for all Topics
    will HAVE to be unique.

    --------------------------------------------------------------

    Generates a slug from the name of the Topic instance provided.
    If a topic from the slug generated is found, append the primary
    key of the topic found from the queryset and check for that.
    If that exists too, call itself recursively until a valid unique
    slug is found - and return it.
    """

    # Log that a defunct function is begin used -
    logger.warning('Do not use this function as it has been deprecated. '
                   'Please read more about why in it\'s respective docstring.')

    # Create a slug from the topic name provided
    slug = slugify(topic.name)

    if new_slug is not None:
        # If function was called recursively
        # assign the slug to test itself against
        # the queryset of Topic with matching slugs.
        slug = new_slug

    # Query database for Topic by
    # slug and order by primary key
    # to get the last Topic.
    qs: QuerySet = Topic.objects.filter(slug=slug).order_by('-pk')
    exists = qs.exists()

    if exists:
        # If the query set returns something
        # then append the pk of the last Topic
        # to the current instance's name.
        new_slug = '{}-{}'.format(slug, qs.first().pk)
        return generate_slug_for_topic(topic, new_slug)

    return slug
