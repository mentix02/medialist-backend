from django.contrib import admin

from article.models import Article


class ArticleAdmin(admin.ModelAdmin):
    list_display_links = ('title',)
    list_display = ('id', 'title', 'author', 'created_on', 'draft')
    prepopulated_fields = {
        'slug': ('title',)
    }


admin.site.register(Article, ArticleAdmin)
