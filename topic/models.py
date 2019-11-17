from django.db import models
from django.conf import settings
from django.shortcuts import reverse

from cloudinary.models import CloudinaryField


class Topic(models.Model):
    """
    A Topic is a collection of Articles. Article instances don't
    HAVE to have a Topic instance however - that's because I don't
    want to lose all the Articles posted under a particular topic
    if the admin of a the same deletes it. For that on_delete
    parameter would have to be models.CASCADE but it is not -
    it's set to models.SET_NULL.

    Read more in author/models.py's Article definition and documentation.

    Topics can only be created by Author that have the attribute
    is_staff set to True - meaning that they are staff members.
    That doesn't mean anything other than the fact that they've
    written a certain number of Articles and the same set of
    Articles have been rated consistently high in objectivity.

    TODO write a metric system for checking how well an author
         is rated objectively and otherwise and automate the process
         of promoting them to staff members.
    """

    description = models.CharField(max_length=200)

    # After much thought, the names for all topics
    # should be unique because if there's even a
    # similar sounding topic, then chances are that
    # the same topic has already been covered in the past.
    name = models.CharField(max_length=100, unique=True)

    # Lets Authors upload a file for the thumbnail
    # to the Cloudinary server.
    thumbnail = CloudinaryField(null=True, blank=True)

    # Read above.
    created_on = models.DateTimeField(auto_now_add=True)

    # Prepopulated on save (or update) by signals
    # living in topic/signals.py and initialized from
    # topic/apps.py when loaded into the settings.
    slug = models.SlugField(max_length=200, null=True, blank=True, unique=True)

    # Every Topic instance has to be created by an
    # Author instance but it is modeled exactly like
    # the relationship between an Article instance
    # and an Author - you NEED to have an Author to
    # create a Topic but you don't need to have one
    # to preserve it - it can be NULL in the database.
    author = models.ForeignKey(settings.AUTH_USER_MODEL,
                               on_delete=models.SET_NULL, null=True,
                               related_name='topics')

    # In case the Author doesn't want to upload a
    # file him/her-self to the Cloudinary server.
    thumbnail_url = models.URLField(default='https://picsum.photos/1900/1080')

    def get_thumbnail(self):
        """
        Checks for existence of thumbnail fields - either as a Cloudinary
        field or the thumbnail_url if the Author entered a URL instead of
        a thumbnail file.
        """
        if self.thumbnail:
            # noinspection PyUnresolvedReferences
            return self.thumbnail.url
        else:
            return self.thumbnail_url

    def get_articles(self):
        return self.articles.filter(draft=False)

    def get_absolute_url(self):
        return reverse('topic:detail', kwargs={'slug': self.slug})

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created_on', '-pk')
