"""
CRUD views for the Topic model.
"""
from author.models import Author

from topic.models import Topic
from topic.serializers import (
    TopicListSerializer,
    TopicDetailSerializer
)

from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView


class TopicListAPIView(ListAPIView):
    """
    Returns a paginated JSON response containing all Topic entries
    inside of the database. Clean, plain, and simple.
    """
    queryset = Topic.objects.all()
    serializer_class = TopicListSerializer


class TopicDetailAPIView(RetrieveAPIView):
    """
    Queries all Topic instances in database according to the slug
    provided in the url and returns serialized JSON object. Slug
    lookups, I'm assuming, are slower than primary key queries but
    it's good for search engine optimization, especially for Google.
    """
    lookup_url_kwarg = 'slug'
    lookup_field = 'slug__iexact'
    queryset = Topic.objects.all()
    serializer_class = TopicDetailSerializer


class TopicDeleteAPIView(APIView):

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def delete(request, slug):
        author: Author = request.user

        topic: Topic = get_object_or_404(Topic, slug__iexact=slug)

        # Check if topic belongs to author
        if topic.author_id == author.id:
            topic.delete()
            return Response({'detail': 'Deleted successfully.'}, status=204)
        else:
            return Response({'detail': 'Deletion is not authorized.'}, status=401)


class TopicCreateAPIView(APIView):
    """
    Parses data from a POST request and fills a Topic model with relevant data.
    Returns serialized data echoing what was provided along a primary key.
    Authentication is required - either via authtoken or via session handling.

    Requires ->

        + application/x-www-form-urlencoded data
        including ->
            name: String
            description: String
            thumbnail: Image [OPTIONAL]
            thumbnail_url: String [OPTIONAL]

        + headers
        including ->
            Authorization: Token {valid token}
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):

        author: Author = request.user

        data = request.POST

        # First check if name provided.
        name = data.get('name')

        # Now check if name is unique.
        if name:
            try:
                Topic.objects.get(name__iexact=name)
                return Response({
                    'detail': f"Topic '{name}' already exists."
                }, status=409)
            except ObjectDoesNotExist:
                pass
        else:
            return Response({'detail': "Field 'name' not provided."}, status=422)

        try:
            # Aggregate data in a dictionary so that it can be
            # unpacked as kwargs in objects.create method and if
            # there's a key missing, it can raise a field error.
            topic_data = {
                'name': name,
                'author': author,
                'description': data['description'],
            }

            # Check whether thumbnail OR thumbnail_url was provided
            if not (data.get('thumbnail_url') or request.FILES.get('thumbnail')):
                return Response({'detail': 'Either provide a url for a thumbnail or an image upload.'}, status=422)
            else:
                topic_data['thumbnail'] = data.get('thumbnail')
                topic_data['thumbnail_url'] = data.get('thumbnail_url')

            topic = Topic.objects.create(**topic_data)

            return Response(TopicListSerializer(topic).data, status=201)

        except KeyError as field:
            return Response({'detail': f"Field {str(field)} not provided."}, status=422)
        except Exception as e:
            return Response({'detail': str(e)}, status=500)
