from django.contrib import admin
from .models import Collection, Category, Bookmark

admin.site.register(Collection)
admin.site.register(Category)
admin.site.register(Bookmark)