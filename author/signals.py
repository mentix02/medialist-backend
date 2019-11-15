"""
Signals that are called after an Author instance is created live here.
Actions that are not dependant on any user interaction directly should
also be implemented here. Stuff like Token creation or auto adding for any
new models that need to refer some User instance should be defined here;
even if it's not a Django model dispatch method.
"""
import uuid

from author.models import Author

from django.db import connection
from django.urls import reverse
from django.conf import settings
from django.dispatch import receiver
from django.utils.html import strip_tags
from django.template.loader import render_to_string
from django.db.models.signals import pre_save, post_save

from rest_framework.authtoken.models import Token

# noinspection PyUnusedLocal
@receiver(pre_save, sender=Author)
def create_author_secret_key_and_send_auth_email(sender, instance: Author, **kwargs):
    """
    Happens before an Author instance is saved - generates a secret key
    from uuid.uuid5's SHA1 hash with the namespace as a uuid1 generated
    from instance.pk and name as the username.

    TODO set up celery to send authentication email
         in the background so that the server can
         respond with something for the time being.
    """

    # Generate secret key.
    namespace = uuid.uuid1(instance.pk)
    secret_key = uuid.uuid5(namespace, instance.username)

    if not (instance.secret_key or connection.settings_dict['NAME'][:5] == 'test_'):
        # Since Author does not have a previous
        # secret key, it means that this is a new
        # user and hence has to be sent an email
        # with the confirmation link to be verified.
        # The second half of this is for testing
        # purposes - you don't want to email all
        # the fake authors that are created during testing.
        # This is also why the secret_key is generated
        # outside of this if clause because we NEED the
        # secret_key field to be populated regardless.

        subject, from_email, to = 'Welcome To The Medialist', settings.EMAIL_HOST_USER, instance.email
        html_content = render_to_string('email/email-confirmation.html', {
            'activation_url': 'http://' + 'localhost:8000' + reverse('author:verify', kwargs={
                'secret_key': str(secret_key)
            })
        })
        text_content = strip_tags(html_content)

        instance.email_user(subject, text_content, from_email, html_message=html_content)

    instance.secret_key = secret_key


# noinspection PyUnusedLocal
@receiver(post_save, sender=Author)
def create_user_token(sender, instance: Author, created: bool = False, **kwargs):
    """
    Create an Authtoken model right after a new Author model is saved.
    """
    if created:
        Token.objects.create(user=instance)
