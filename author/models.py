"""
Definition of Author model. Akin to the "user" of the website. Author is
a user who can write posts, bookmark posts, comment as well as "like" posts.
"""
from django.db import models
from django.contrib.auth.models import AbstractUser


class Author(AbstractUser):
    """
    Custom extension to the inbuilt model provided by contrib.auth.models.User.
    """

    # A small piece of text describing the Author.
    bio = models.TextField(max_length=200)

    # Only verified people can write, bookmark, rate
    # articles. Note - verified Authors does not mean
    # like a "blue tick" Twitter type deal. It just
    # means that the Author has a verified email and
    # is just not a bot. It's different from the is_staff
    # property. The is_staff = True, on the other hand,
    # means that the Author instance has been "promote"d
    # meaning that the "promote" method has been called
    # upon the instance and now whenever someone reads
    # any Article authored by this particular author, the
    # author will have a blue tick next to them.
    verified = models.BooleanField(default=False)

    # Secret key is used inside of urls whenever an
    # actions such as Author deletion request, or a
    # verification request is sent to an Author instances
    # emails. Since a simple GET request can't carry any
    # data except query params, it's easier to insert the
    # secret_key inside of the url. The secret_key also
    # has to be modified every time an Author model is saved.
    # This is accomplished by using django's dispatch signals
    # defined by author/signals.py.
    secret_key = models.UUIDField(null=True, blank=True, unique=True)

    def __str__(self) -> str:
        return self.username

    def verify(self) -> None:
        self.verified = True
        self.save()

    def promote(self) -> None:
        self.verify()
        self.is_staff = True
        self.save()

    class Meta:
        ordering = ('-date_joined', '-pk')

    def get_key(self) -> str:
        return self.auth_token.key

    def get_topics(self) -> models.QuerySet:
        return self.topics.all()

    def get_articles(self) -> models.QuerySet:
        return self.articles.filter(draft=False)
