from topic.models import Topic
from article.models import Article
from article.serializers import (
    ArticleListSerializer,
    ArticleDetailSerializer
)

from django.utils.text import slugify
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, RetrieveAPIView


class RecentArticleListAPIView(ListAPIView):
    """
    Gets the last N number of articles to display in a list. Used
    for getting recently written Articles that aren't drafts.
    """
    pagination_class = None
    serializer_class = ArticleListSerializer

    def get_queryset(self):
        N = self.request.GET.get('N', 12)
        articles = Article.objects.filter(draft=False)[:N]
        return articles


class ArticleDetailAPIView(RetrieveAPIView):
    """
    Simply queries the database for a matching slug with the slug
    provided in the url and returns Serializer data as response.
    """
    lookup_field = 'slug'
    lookup_url_kwarg = 'slug'
    serializer_class = ArticleDetailSerializer
    queryset = Article.objects.filter(draft=False)


class ArticleCreateAPIView(APIView):

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def post(request):

        # Get data
        data = request.POST

        # Check if an article with the same title exists.
        title = data.get(key='title')

        if not title:
            return Response({
                'detail': "Field 'title' not provided."
            }, status=422)

        slug = slugify(title)

        try:
            # Checks for slug uniqueness and topic existence
            Article.objects.get(slug__iexact=slug)
        except Article.DoesNotExist:
            try:
                article_data = {
                    'title': title,
                    'content': data['content'],
                    'topic_id': data['topic_id'],
                    'author_id': request.user.id,
                    'draft': (True if data.get('draft') else False),
                }
                tags = data['tags']
            except KeyError as field:
                return Response({
                    'detail': f"Field {str(field)} not provided."
                }, status=422)
            else:
                if not (data.get('thumbnail_url') or request.FILES.get('thumbnail')):
                    return Response({
                        'detail': 'Either provide a url for an article thumbnail or an image upload.'
                    }, status=422)
                else:
                    article_data['thumbnail'] = data.get('thumbnail')
                    article_data['thumbnail_url'] = data.get('thumbnail_url')

                try:
                    Topic.objects.get(pk=article_data['topic_id'])
                except ObjectDoesNotExist:
                    return Response({
                        'detail': 'Topic not found.'
                    }, status=404)

                article = Article.objects.create(**article_data)
                article.set_tags_from_string(tags)
                article.save()

                return Response(ArticleDetailSerializer(article).data, status=201)
        else:
            return Response({
                'detail': f"Article with title '{title}' exists."
            }, status=409)
