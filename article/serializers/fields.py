from rest_framework import serializers


class TagListField(serializers.Field):
    """
    A custom serializer field for representing a list of tags as
    a JSON list of strings - works in conjunction with django-taggit.
    This was developed to remove dependencies from django-taggit-\
    serializer and have a simple internal method for doing this.
    """

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        if isinstance(value, list):
            return value
        else:
            return [tag.name for tag in value.all()]
