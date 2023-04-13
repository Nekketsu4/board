import django.dispatch

from .models import Comment
from django.db.models.signals import post_save
from .utilities import send_activation_notification, send_new_comment_notification

user_registered = django.dispatch.Signal()


def user_registered_dispatcher(sender, **kwargs):
    send_activation_notification(kwargs['instance'])


user_registered.connect(user_registered_dispatcher)


def post_save_dispatcher(sender, **kwargs):
    author = kwargs['instance'].bboard.author
    if kwargs['created'] and author.send_messages:
        send_new_comment_notification(kwargs['instance'])


post_save.connect(post_save_dispatcher, sender=Comment)
