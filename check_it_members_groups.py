#!/usr/bin/env python
"""
Check if IT members can see IT help desk group
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

def check_it_members_groups():
    print("Checking IT Members Groups")
    print("=" * 50)
    
    # IT member usernames
    it_usernames = ['s20330', '250479', '230022', '140287', '111075']
    
    # Get IT help desk group
    helpdesk_group = Conversation.objects.filter(group__name='IT help desk').first()
    
    if not helpdesk_group:
        print("✗ IT help desk group not found!")
        return
    
    print(f"✓ IT help desk group found (ID: {helpdesk_group.id})")
    
    # Check each IT member
    for username in it_usernames:
        user = User.objects.filter(username=username).first()
        if user:
            # Check if user is participant in IT help desk group
            is_participant = ConversationParticipant.objects.filter(
                user=user, conversation=helpdesk_group
            ).exists()
            
            if is_participant:
                print(f"✓ {username} is in IT help desk group")
            else:
                print(f"✗ {username} is NOT in IT help desk group")
                
                # Add them if they're not in the group
                ConversationParticipant.objects.create(
                    user=user, conversation=helpdesk_group
                )
                print(f"  + Added {username} to IT help desk group")
        else:
            print(f"✗ User {username} not found")
    
    # Final check
    print("\nFinal IT help desk group participants:")
    participants = ConversationParticipant.objects.filter(conversation=helpdesk_group)
    for p in participants:
        print(f"  - {p.user.username}")
    
    print(f"\nTotal participants: {participants.count()}")
    
    print("\n" + "=" * 50)
    print("IT MEMBERS GROUPS CHECKED!")
    print("=" * 50)

if __name__ == "__main__":
    check_it_members_groups()
