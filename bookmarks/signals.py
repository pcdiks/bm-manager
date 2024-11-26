from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Collection, Category, Bookmark

@receiver(post_save, sender=User)
def create_default_collection(sender, instance, created, **kwargs):
    if created:  # Trigger only when a new user is created
        collection = Collection.objects.create(
            name="Default",
            description="This is your default collection.",
            owner=instance,
        )
        # Add a default category
        category = Category.objects.create(
            name="General",
            collection=collection,
        )
        # Add a default bookmark
        Bookmark.objects.create(
            url="https://github.com",
            display_name="Github",
            notes="",
            category=category,
        )        