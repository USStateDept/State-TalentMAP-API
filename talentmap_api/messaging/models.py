from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import ArrayField

from djchoices import DjangoChoices, ChoiceItem

class Notification(models.Model):
    '''
    This model represents an individual notification item
    '''

    message = models.TextField(null=False, help_text="The message for the notification")
    owner = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, null=False, related_name="notifications", help_text="The owner of the notification")
    tags = ArrayField(models.CharField(max_length=20), default=list, help_text="This notification's tags")

    is_read = models.BooleanField(default=False, help_text="Whether this notification has been read")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        ordering = ["date_updated"]


class Task(models.Model):
    '''
    This model represents a task object.
    '''
    class Priority(DjangoChoices):
        low = ChoiceItem(0)
        medium = ChoiceItem(1)
        high = ChoiceItem(2)

    owner = models.ForeignKey('user_profile.UserProfile', on_delete=models.CASCADE, null=False, related_name="tasks", help_text="The owner of the task")
    priority = models.IntegerField(default=Priority.low, choices=Priority.choices)
    tags = ArrayField(models.CharField(max_length=20), default=list, help_text="This task's tags")

    title = models.TextField(null=True)
    content = models.TextField(null=True)

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    date_due = models.DateTimeField(null=True)
    date_completed = models.DateTimeField(null=True)

    class Meta:
        managed = True
        ordering = ['priority', 'date_due']


class Sharable(models.Model):
    '''
    This model represents a shared item from one user to another. The field sharable_model
    is the string representation of the model, for example 'position.Position', and the
    sharable_id is the integer representation of the autofield primary key for that model
    '''
    sharing_user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, related_name="sent_shares")
    receiving_user = models.ForeignKey('user_profile.UserProfile', on_delete=models.DO_NOTHING, related_name="received_shares")

    # Sharable
    sharable_id = models.IntegerField(help_text="The ID of the model instance for this sharable")
    sharable_model = models.TextField(help_text="The string of the model")

    is_read = models.BooleanField(default=False, help_text="Whether this sharable has been read")

    date_created = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)

    class Meta:
        managed = True
        ordering = ["date_created"]


@receiver(post_save, sender=Sharable)
def post_sharable_save(sender, instance, created, **kwargs):
    '''
    This listener notifies the receiving user to notify them of their share.
    '''
    if created:
        # Create a new notification for the receiving user
        Notification.objects.create(owner=instance.receiving_user,
                                    tags=['share'],
                                    message=f"{instance.sharing_user} has shared a {instance.sharable_model.split('.')[-1]} with you")

        # TODO: Add e-mail here when e-mail implementation is determined
        pass
