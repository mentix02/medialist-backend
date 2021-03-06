from django.db import models

from author.models import Author
from article.models import Article


class Bookmark(models.Model):

    article = models.ForeignKey(Article, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE, related_name='bookmarks')

    class Meta:
        ordering = ('-pk',)

    def __str__(self) -> str:
        return f'{self.article} {self.author}'
