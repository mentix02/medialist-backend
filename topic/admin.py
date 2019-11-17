from django.contrib import admin

from topic.models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display_links = ('name',)
    list_display = ('id', 'name', 'article_count')
    prepopulated_fields = {
        'slug': ('name', )
    }


admin.site.register(Topic, TopicAdmin)
