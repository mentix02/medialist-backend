"""
Helper methods for generating fake Topic models.
Should not be used except for testing purposes and
stress testing over a lot of models.
"""
from faker import Faker

from random import choice

from topic.models import Topic

fake = Faker()

THUMBNAIL_URL = (
    'https://picsum.photos/id/557/1900/1080',
    'https://picsum.photos/id/251/1900/1080',
    'https://picsum.photos/id/700/1900/1080',
    'https://picsum.photos/id/420/1900/1080',
    'https://picsum.photos/id/1000/1900/1080',
)


def create_topic(author_id: int) -> Topic:
    """
    Creates a fake topic. Topics with the same name might occur
    due to faker's factory being pseudo random but that's a risk
    I'm willing to take. Is it better to be smart or be lucky?
    """
    return Topic.objects.create(
        author_id=author_id,
        name=fake.text(45)[:-1],
        description=fake.text(150),
        thumbnail_url=choice(THUMBNAIL_URL),
    )
