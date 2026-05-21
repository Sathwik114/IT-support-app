#!/usr/bin/env python
"""
Debug why IT help desk group is not showing for IT members
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Q, Count, Max
from messaging.models import Conversation, Group, ConversationParticipant

User = get_user_model()

def debug_helpdesk_group():
    print("Debugging IT Help Desk Group")
    print("=" * 50)
    
    # Get IT help desk group
    helpdesk_group = Conversation.objects.filter(group__name='IT help desk').first()
    
    if not helpdesk_group:
        print("✗ IT help desk group not found!")
        return
    
    print(f"✓ IT help desk group found:")
    print(f"  - ID: {helpdesk_group.id}")
    print(f"  - Type: {helpdesk_group.conversation_type}")
    print(f"  - Group name: {helpdesk_group.group.name}")
    print(f"  - Updated: {helpdesk_group.updated_at}")
    
    # Check participants
    participants = ConversationParticipant.objects.filter(conversation=helpdesk_group)
    print(f"  - Participants: {participants.count()}")
    
    # Test with IT member
    test_user = User.objects.filter(username='s20330').first()
    if not test_user:
        print("✗ Test user not found")
        return
    
    print(f"\nTesting with user: {test_user.username}")
    
    # Check if user is participant
    is_participant = ConversationParticipant.objects.filter(
        user=test_user, conversation=helpdesk_group
    ).exists()
    print(f"  - Is participant: {is_participant}")
    
    # Check the filtering logic step by step
    print(f"\nChecking filtering logic:")
    
    # Step 1: Basic participant filter
    step1 = Conversation.objects.filter(participants=test_user)
    print(f"  - Step 1 (participants): {step1.count()} conversations")
    
    # Step 2: Exclude superusers
    step2 = step1.exclude(participants__is_superuser=True)
    print(f"  - Step 2 (exclude superusers): {step2.count()} conversations")
    
    # Step 3: Filter not null
    step3 = step2.filter(participants__isnull=False)
    print(f"  - Step 3 (not null): {step3.count()} conversations")
    
    # Check if helpdesk group is in each step
    print(f"  - Helpdesk in Step 1: {step1.filter(id=helpdesk_group.id).exists()}")
    print(f"  - Helpdesk in Step 2: {step2.filter(id=helpdesk_group.id).exists()}")
    print(f"  - Helpdesk in Step 3: {step3.filter(id=helpdesk_group.id).exists()}")
    
    # Check if helpdesk group has superuser participants
    superuser_participants = participants.filter(user__is_superuser=True)
    print(f"  - Superuser participants: {superuser_participants.count()}")
    for p in superuser_participants:
        print(f"    - {p.user.username}")
    
    # Check if any participants are null
    null_participants = participants.filter(user__isnull=True)
    print(f"  - Null participants: {null_participants.count()}")
    
    print("\n" + "=" * 50)
    print("DEBUG COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    debug_helpdesk_group()
