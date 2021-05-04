from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from users.views import password_reset_for_new_user
from users.models import Profile


@receiver(post_save, sender=User)
def user_created(sender, instance, created, **kwargs):
    if created:
        password_reset_for_new_user(instance.email)
        Profile.objects.create(user=instance)


def init_signals():
    pass
