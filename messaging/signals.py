"""
Signals for automatic user addition to IT help desk group
"""

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

IT_MEMBER_USERNAMES = ['s20330', '250479', '230022', '140287', '111075']
IT_MEMBER_GROUP_NAMES = [
    'Sathya Sathwik Pushpagiri',
    'Rajesh',
    'Shakeer',
    'Narasimha',
    'Masthan',
]


@receiver(post_save, sender=User)
def add_user_to_default_chats(sender, instance, created, **kwargs):
    """Automatically add new users to the default group and IT member chats."""
    if not created:
        return

    from .models import Conversation, ConversationParticipant

    default_group_names = ['GTI members', 'IT help desk']
    if instance.username not in IT_MEMBER_USERNAMES:
        default_group_names.extend(IT_MEMBER_GROUP_NAMES)

    default_group_conversations = Conversation.objects.filter(
        conversation_type='group',
        group__name__in=default_group_names,
    )

    for conversation in default_group_conversations:
        ConversationParticipant.objects.get_or_create(
            user=instance,
            conversation=conversation,
        )

    if instance.username in IT_MEMBER_USERNAMES:
        return

    it_members = User.objects.filter(username__in=IT_MEMBER_USERNAMES)
    for it_member in it_members:
        if it_member.id == instance.id:
            continue

        existing_chat = Conversation.objects.filter(
            conversation_type='individual',
            participants=instance,
        ).filter(
            participants=it_member,
        ).first()

        if not existing_chat:
            chat = Conversation.objects.create(conversation_type='individual')
            ConversationParticipant.objects.get_or_create(conversation=chat, user=instance)
            ConversationParticipant.objects.get_or_create(conversation=chat, user=it_member)
