from django.contrib import admin

from topic.models import Topic


class TopicAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_on')
    list_display_links = ('name',)
    prepopulated_fields = {
        'slug': ('name', )
    }


admin.site.register(Topic, TopicAdmin)
