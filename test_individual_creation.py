#!/usr/bin/env python
"""
Test individual conversation creation between any users
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Max, Count, Q
from messaging.models import Conversation, Group, ConversationParticipant

User = get_user_model()

def test_individual_creation():
    print("Testing Individual Conversation Creation")
    print("=" * 60)
    
    # Get a normal user and IT member
    normal_user = User.objects.exclude(username__in=['s20330', '250479', '230022', '140287', '111075']).first()
    it_member = User.objects.filter(username='s20330').first()
    
    if normal_user and it_member:
        print(f"Normal user: {normal_user.username}")
        print(f"IT member: {it_member.username}")
        
        # Check if individual conversation exists
        existing_conv = Conversation.objects.filter(
            conversation_type='individual'
        ).filter(participants=normal_user).filter(participants=it_member).first()
        
        if existing_conv:
            print(f"  - Individual conversation exists: {existing_conv.id}")
        else:
            print(f"  - No individual conversation found between {normal_user.username} and {it_member.username}")
            
            # Create individual conversation
            new_conv = Conversation.objects.create(
                conversation_type='individual'
            )
            
            # Add participants
            ConversationParticipant.objects.create(
                conversation=new_conv,
                user=normal_user
            )
            ConversationParticipant.objects.create(
                conversation=new_conv,
                user=it_member
            )
            
            print(f"  - Created new individual conversation: {new_conv.id}")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_individual_creation()
