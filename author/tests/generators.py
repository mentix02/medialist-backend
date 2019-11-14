"""
Helper methods for generating fake
Author models. Should not be used
except for testing purposes and stress
testing over a lot of models.
"""
from faker import Faker

from author.models import Author

fake = Faker()


def create_author(staff: bool = False) -> Author:
    author: Author = Author.objects.create_user(
        email=fake.email(),
        bio=fake.text(120),
        password='abcd1432',
        username=fake.user_name(),
        first_name=fake.first_name(),
    )

    if staff:
        author.promote()

    return author
