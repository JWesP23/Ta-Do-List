from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.dispatch import receiver
from tasktracker.models import TaskGroup

# Assign a TaskGroup to every new user called "General"
@receiver(post_save, sender=User)
def create_general_group(sender, instance, created, **kwargs):
    if created:
        TaskGroup.objects.create(user=instance, title="General", description= "A default, non-specific group for organizing tasks.")