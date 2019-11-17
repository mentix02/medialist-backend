"""
API Views for CRUD operations on the Author model live here.
Every view should be a class that either inherits from
either rest_framework's generics or a custom APIView. Views 
as functions will not be accepted.
"""
import re
import typing

from django.http import Http404
from django.http.request import HttpRequest
from django.contrib.auth import authenticate
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import redirect, get_object_or_404

from author import utils as u
from author.models import Author
from author.serializers import (
    AuthorListSerializer,
    AuthorDetailSerializer,
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import (
    IsAdminUser,
    IsAuthenticated
)
from rest_framework.generics import (
    ListAPIView,
    RetrieveAPIView,
)


class AuthorListAPIView(ListAPIView):
    """
    This view should never be accessible to the common public - only to Staff
    members (permissions defined in custom IsStaffUser). It's only used for
    statistics purposes and nothing else.
    """
    pagination_class = None
    queryset = Author.objects.all()
    permission_classes = (IsAdminUser,)
    serializer_class = AuthorListSerializer


class AuthorDetailAPIView(RetrieveAPIView):
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    queryset = Author.objects.all()
    serializer_class = AuthorDetailSerializer


class AuthorCreateAPIView(APIView):
    """
    Parses data from a POST request and fills Author model with relevant data.
    Returns serialized data with the newly created authtoken's key (generated
    in author.signals.create_user_token) in JSON format.

    Requires ->
        application/x-www-form-urlencoded data
        including ->
            bio: String
            email: String
            username: String
            password: String
            first_name: String

    Returns ->
        Echos data provided along with authtoken inside a JSON string.
    """

    @staticmethod
    def post(request: HttpRequest):

        # Get username and email from POST data.
        data = request.POST
        # noinspection PyArgumentList
        username, email = data.get(key='username'), data.get(key='email')

        if username:

            # Check if username and email are available and are valid.

            # Email verification.
            if email and u.is_valid_email(email):
                try:
                    Author.objects.get(email__iexact=email)
                    return Response({
                        'detail': f"Author with email '{email}' already exists."
                    }, status=409)
                except ObjectDoesNotExist:
                    pass
            else:
                return Response({'detail': f"Field 'email' not provided."}, 422)

            # Implements a sanity check for username format.
            expr = re.compile(r'^[\w.@+-]+$')
            if not expr.match(username) or len(username) > 150:
                return Response({
                    'detail': 'Requires 150 characters or fewer. Letters, digits and @/./+/-/_ only.'
                }, status=422)

            if u.is_available(username):
                # Get more data since username is not taken.
                try:
                    # Make a dictionary of data so that if
                    # there is any key missing, a KeyError
                    # raises a 422 (Unprocessable Entity),
                    # immediately signifying a missing
                    # required field. It can also be passed
                    # directly as fields in create_user method
                    # by using ** to populate named fields.
                    author_data: typing.Dict[str, str] = {
                        'bio': data['bio'],
                        'email': data['email'],
                        'password': data['password'],
                        'username': data['username'],
                        'first_name': data['first_name']
                    }

                    author = Author.objects.create_user(**author_data)

                    author_details = u.get_author_serialized_data(author, True)

                    return Response(author_details)
                except KeyError as field:
                    # Raised if a data field was not provided.
                    # Note - there aren't single quites around {str(field)}
                    # since apparently the KeyError already wraps it in them (quotes).
                    return Response({'detail': f"Field {str(field)} not provided."}, 422)
                except Exception as e:
                    # Raised if something else failed.
                    return Response({'detail': str(e)}, status=500)
            else:
                # Returned because username provided was not available.
                return Response({'detail': f"User '{username}' already exists."}, 409)
        else:
            # Returned if username field was not provided - a custom
            # check is implemented in the beginning so as to not go
            # over the entire code in one request - username has to
            # go through a uniqueness / validation check.
            # Why not do it as the first thing?
            return Response({'detail': f"Field 'username' not provided."}, 422)


class AuthorVerifyAPIView(APIView):
    """
    Takes in a GET request with the secret key as a part of the url and
    redirects to the homepage of The Medialist; to be decided if the user
    should be logged in or not - and how that will happen if at all. Baby steps first.
    """

    @staticmethod
    def get(request, secret_key):
        if u.is_valid_uuid(str(secret_key)):
            author = get_object_or_404(Author, secret_key__exact=secret_key)
            author.verify()
            return redirect('feed:index')
        else:
            raise Http404()


class AuthorUpdateAPIView(APIView):
    """
    Similar to AuthorCreateAPIView just instead of objects.create, it calls objects.update
    by de-serializing data from a dictionary into a key value pair arguments using kwargs.
    Read why this is done inside of the AuthorCreateAPIView. Note - this view does not handle
    changing of the password. That view remains to be written. It'll be separate for reusable
    purposes such as a ForgetPassword view. Further, I think allowing Authors to change their
    emails is not such a good idea either without some form of validation. Alright. So be it.
    Password and email fields will have their own separate views for updating.

    TODO write a view for updating an Author's password with some form of validation.

    TODO write a view for updating an Authors' email field with validation.

    Requires ->
        + application/x-www-form-urlencoded data
        including ->
            bio: String [OPTIONAL]
            username: String [OPTIONAL]
            first_name: String [OPTIONAL]

        + headers
        including ->
            Authorization: Token {valid token}
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def patch(request):

        author: Author = request.user

        # Get data with defaults as already
        # populated Author instance fields.

        data: typing.Dict[str, str] = {
            'bio': request.POST.get('bio', author.bio),
            'username': request.POST.get('username', author.username),
            'first_name': request.POST.get('first_name', author.first_name)
        }

        if data['username'] == author.username or u.is_available(data['username']):
            for field, value in data.items():
                if getattr(author, field) != value:
                    setattr(author, field, value)
            author.save()

            return Response(u.get_author_serialized_data(author, token=True))
        else:
            return Response({'detail': f"User '{data['username']}' already exists."}, 409)


class AuthorRetrieveTokenView(APIView):
    """
    Simply returns the authtoken in exchange for a username and password combo.
    Returns an error if credentials aren't provided; same for invalid ones.
    """

    @staticmethod
    def post(request):

        try:
            # Gather data.
            credentials = {
                'username': request.POST['username'],
                'password': request.POST['password']
            }
        except KeyError as field:
            # In case there wasn't a matching field in the
            # request.POST dictionary-like object.
            return Response({'detail': f"Field {str(field)} not provided."}, status=422)

        # Authenticate Author with credentials.
        author: Author = authenticate(**credentials)

        if author is not None:
            return Response({
                'token': author.get_key()
            })
        else:
            # If no Author was found with matching credentials.
            return Response({
                'detail': 'Invalid credentials.'
            }, status=401)
