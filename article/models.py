"""
Article model definition.
"""
import typing
import logging

from django.db import models
from django.conf import settings
from django.utils.text import Truncator

from topic.models import Topic
from backend.utils import replace

from taggit.managers import TaggableManager
from cloudinary.models import CloudinaryField


logger = logging.getLogger(__name__)


class ArticleManager(models.Manager):
    def all(self):
        """
        A custom logging warning is raised if ALL articles are
        queried since that's not something one would want to do
        in production. It might be completely disallowed but the
        admin panel might call it and that might break things.
        """
        logger.warning('All Article instances are being fetched.')
        return self.get_queryset()


class Article(models.Model):
    """
    Article model definition. Each Article has an Author connected
    to it as a ForeignKey.

    Each Article instance also has a TaggableManager field for
    managing Tags - coming from django-taggit. Documentation -
    https://bitly.com/33sWPGH. Tags are serialized using
    django-taggit-serializer. Docs can be found here - http://bit.ly/36TAtAm.
    It's not used much except for serializing articles. An
    internal way for converting the tags to JSON can be implemented
    to reduce dependencies.

    There's an objectivity metric that is discussed below - it's
    used for the machine learning model (not made yet) to predict
    an objectivity rating.

    TODO build and train the model.
    """

    objects = ArticleManager()

    tags = TaggableManager(blank=True)

    # Main body of an Article.
    # No text limit. Not yet.
    content = models.TextField()

    title = models.CharField(max_length=150)

    # An article by default is NOT
    # a draft. Authors would have to
    # manually check the draft input
    # to save it to their Author
    # dashboard for their eyes only.
    draft = models.BooleanField(default=False)

    # This field is updated automatically
    # when an Article is update. It's also
    # updated when an Article is modified.
    # It's not the same as created_at because
    # that's only updated when the Article
    # is added into the database for the first time.
    updated_on = models.DateTimeField(auto_now=True)

    # Read documentation for updated_at field
    created_on = models.DateTimeField(auto_now_add=True)

    # The topic field establishes the
    # the relationship between an Article
    # and the Topic that it comes under.
    # I want Articles to be preserved if the
    # admin of its parent Topic deletes the
    # topic and thus the topic field is
    # nullable. That does not mean that the
    # user can select a "None" option when
    # writing a new Article - a topic HAS
    # to be provided by a user.
    topic = models.ForeignKey(Topic, on_delete=models.SET_NULL,
                              null=True, related_name='articles')

    # Every Article instance has to be authored
    # (no pun intended) by an Author. But it CAN
    # have NULL as an author. No, no anonymous posts.
    # This isn't 4chan as much as I'd like it to be.
    # An author field can only be NULL if the author
    # ForeignKey was deleted after posting an article.
    # I've thought about keeping at least the username
    # field for author but I always hate when websites
    # don't let me delete my account when I'm done
    # with it and gives me the option to "deactivate"
    # and thus implying that my info will remain with them
    # forever and ever. So when an Author is deleted,
    # all the username fields serialized with any Article
    # data will convert to a "null" (in JSON format) and
    # the frontend will just say User or something generic
    # with a disabled link and no data on a popover.
    # The field is a ForeignKey to settings.AUTH_USER_MODEL
    # because that's how the Django documentation
    # recommends us to do it. It's better that way because
    # now I can have circular imports for referencing Article
    # model inside of the author/models.py file or vice versa.
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               null=True,
                               related_name='articles',
                               on_delete=models.SET_NULL,)

    # This field is just for querying Articles
    # in a URL friendly way. A slug is just a
    # title that has been separated by dashes
    # "-". It's automatically generated by post_save
    # signals in article/signals.py using
    # inbuilt django slugify methods with proper
    # uniqueness checks and validation with
    # internationalization support.
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    # User uploaded file goes to Cloudinary server.
    thumbnail = CloudinaryField(null=True, blank=True)

    # Objectivity is defined as a floating
    # point value that will be determined
    # by the machine learning model. It will
    # almost always be leaning towards 0.
    objectivity = models.FloatField(blank=True, default=0, editable=False)

    # In case Author does not want to upload a
    # file image him/herself.
    thumbnail_url = models.URLField(default='https://picsum.photos/1900/1080', null=True, blank=True)

    def get_thumbnail(self):
        """
        Checks for existence of thumbnail fields - either as a Cloudinary
        field or the thumbnail_url if the Author entered a URL instead
        of a thumbnail file.
        """
        if self.thumbnail:
            # noinspection PyUnresolvedReferences
            return self.thumbnail.url
        else:
            return self.thumbnail_url

    @property
    def timestamp(self):
        return self.updated_on if self.updated_on else self.created_on

    def get_truncated_content(self, length: int = 20) -> str:
        try:
            length = int(length)
        except ValueError:
            return self.content
        return Truncator(self.content).words(length, truncate=' …')

    @property
    def truncated_content(self) -> str:
        return self.get_truncated_content()

    @property
    def objective(self) -> bool:
        """
        Returns a boolean value if the objectivity computed by the model
        is more than 0.5.
        """
        return self.objectivity >= 0.5

    @property
    def subjectivity(self) -> float:
        """
        Objectivity is calculated from a range of 0 to 1 thus subjectivity
        is simply 1 minus the objectivity.
        """
        return 1 - self.objectivity

    def set_tags_from_string(self, tags: str) -> None:

        tags: typing.List[str] = replace(tags, ' "\'').split(',')

        for tag in tags:
            self.tags.add(tag)

    def __str__(self) -> str:
        """
        Textual representation for admin panel for Article. Maybe should
        add a timestamp parameter as well to give a more dashboard type feel.
        """
        return self.title

    class Meta:
        ordering = ('-created_on', '-updated_on', '-pk')
