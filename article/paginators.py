from rest_framework.pagination import PageNumberPagination


class RecentArticleListAPIPaginator(PageNumberPagination):
    page_size = 12
