
# Add this to your messaging/models.py or signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model

User = get_user_model()

@receiver(post_save, sender=User)
def add_user_to_it_helpdesk(sender, instance, created, **kwargs):
    """Automatically add new users to IT help desk group"""
    if created:
        from messaging.models import Conversation, Group, ConversationParticipant
        
        # Get IT help desk group
        helpdesk_group = Conversation.objects.filter(
            conversation_type='group',
            group__name='IT help desk'
        ).first()
        
        if helpdesk_group:
            # Add new user to IT help desk group
            ConversationParticipant.objects.get_or_create(
                user=instance,
                conversation=helpdesk_group
            )
            print(f"Added {instance.username} to IT help desk group")
