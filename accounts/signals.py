from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserAvatar, UserProfile


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if not created:
        return

    UserProfile.objects.create(user=instance)
    UserAvatar.objects.create(user=instance)
