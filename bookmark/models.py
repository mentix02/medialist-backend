from django.db import models

from author.models import Author
from article.models import Article


class Bookmark(models.Model):

    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    article = models.ForeignKey(Article, on_delete=models.CASCADE)

    class Meta:
        ordering = ('-pk',)

    def get_article(self) -> Article:
        return self.article

    def __str__(self) -> str:
        return f'{self.article} {self.author}'
