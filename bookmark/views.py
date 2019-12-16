from article.models import Article
from bookmark.models import Bookmark
from bookmark.serializers import BookmarkSerializer

from django.db.models import QuerySet
from django.core.exceptions import ObjectDoesNotExist

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.parsers import FormParser, MultiPartParser


class BookmarkAPIView(APIView):
    """
    A generic view for either creating or destroying a Bookmark instance
    based on it's existence - if a bookmark by the authenticated author
    exists (identified by the article_id), then it's deleted - if it doesn't,
    it's created.
    """

    permission_classes = (IsAuthenticated,)
    parser_classes = (FormParser, MultiPartParser)

    @staticmethod
    def post(request) -> Response:

        article_id = request.POST.get('article_id')

        if not article_id:
            return Response({
                'detail': "Field 'article_id' not provided."
            }, status=422)

        author = request.user

        try:
            article = Article.objects.get(id=article_id, draft=False)
        except ObjectDoesNotExist:
            return Response({
                'detail': 'Article does not exist.'
            }, status=404)
        else:
            bookmark, created = Bookmark.objects.get_or_create(author=author, article=article)

            if not created:
                # If a bookmark wasn't created, i.e. it already existed,
                # then delete it and send appropriate response.
                bookmark.delete()
                return Response({
                    'detail': {
                        'action': 'deleted'
                    }
                })
            else:
                return Response({
                    'detail': {
                        'action': 'created'
                    }
                }, status=201)


class ArticleSortedByBookmarksAPIView(ListAPIView):
    """
    A list type API view for getting all the articles that
    an Author bookmarks.
    """

    serializer_class = BookmarkSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self) -> QuerySet:
        author = self.request.user
        return Bookmark.objects.filter(author=author)


class ArticleIDsSortedByAuthorBookmarkAPIView(APIView):
    """
    An APIView that returns a list of all the primary keys
    of articles that the logged in user has bookmarked.
    """

    permission_classes = (IsAuthenticated,)

    @staticmethod
    def get(request):
        author = request.user
        pks = [
            b.article.pk for b in Bookmark.objects.filter(author=author)
        ]
        return Response(pks)
