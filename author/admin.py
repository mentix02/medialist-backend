from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from author.models import Author

admin.site.register(Author, UserAdmin)
