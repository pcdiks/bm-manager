from django.db import models
from django.contrib.auth.models import User

class Collection(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=100)
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='categories')

    def __str__(self):
        return self.name

class Bookmark(models.Model):
    url = models.URLField()
    display_name = models.CharField(max_length=200)
    notes = models.TextField(blank=True, null=True)
    tags = models.CharField(max_length=200, blank=True, null=True)  # Comma-separated tags
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='bookmarks')

    def __str__(self):
        return self.display_name