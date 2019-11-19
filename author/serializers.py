"""
Generic serializers for Author model.
"""
from author.models import Author

from rest_framework import serializers


class AuthorListSerializer(serializers.ModelSerializer):
    """
    Used for serializing instances where a lot of Author data isn't
    needed such as a popover data for quick view at an author's
    information or something along those lines. Will almost be used in
    AuthorListAPIView for admin purposes and when a new Author signs up.
    """

    class Meta:

        model = Author
        fields = ('pk', 'username', 'first_name')


class AuthorDetailSerializer(serializers.ModelSerializer):
    """
    User for serializing all fields of Author model instance except
    the password - also provides HyperLinkedIdentityField urls for
    Topic and Article instances created by a particular Author instance.

    TODO implement the HyperLinkedIdentityFields for articles and topics
    """

    class Meta:

        model = Author
        fields = ('pk', 'username', 'bio', 'first_name')
