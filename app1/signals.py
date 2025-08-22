from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from .models import Profile

@receiver(post_save, sender=User)
def create_or_update_user_profile(sender, instance, created, **kwargs):
    if created:
        # Only create a profile, don't set image here
        Profile.objects.create(user=instance)
    else:
        # Just save existing profile
        instance.profile.save()