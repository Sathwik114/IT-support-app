#!/usr/bin/env python
"""
Set up automatic addition of new users to IT help desk group
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Conversation, Group, ConversationParticipant

User = get_user_model()

def setup_auto_add_users():
    print("Setting Up Automatic User Addition")
    print("=" * 50)
    
    # Create signal handler code
    signal_code = '''
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
'''
    
    # Write signal handler to file
    with open('auto_add_signal.py', 'w') as f:
        f.write(signal_code)
    
    print("✓ Signal handler code created in 'auto_add_signal.py'")
    
    # Add signal to Django apps
    print("\nTo complete setup:")
    print("1. Add the signal code to your messaging/signals.py")
    print("2. Import signals in messaging/apps.py")
    print("3. Restart Django server")
    
    # Test with current users
    print("\nTesting with current users...")
    helpdesk_group = Conversation.objects.filter(
        conversation_type='group',
        group__name='IT help desk'
    ).first()
    
    if helpdesk_group:
        all_users = User.objects.all()
        group_participants = ConversationParticipant.objects.filter(conversation=helpdesk_group)
        
        print(f"✓ IT help desk group has {group_participants.count()} participants")
        print(f"✓ Total users in system: {all_users.count()}")
        
        # Check if any users are missing
        missing_users = []
        for user in all_users:
            if not ConversationParticipant.objects.filter(user=user, conversation=helpdesk_group).exists():
                missing_users.append(user)
        
        if missing_users:
            print(f"Adding {len(missing_users)} missing users...")
            for user in missing_users:
                ConversationParticipant.objects.create(
                    user=user, conversation=helpdesk_group
                )
            print(f"✓ Added {len(missing_users)} users to IT help desk group")
        else:
            print("✓ All users are already in IT help desk group")
    
    print("\n" + "=" * 50)
    print("AUTO ADD SETUP COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    setup_auto_add_users()
