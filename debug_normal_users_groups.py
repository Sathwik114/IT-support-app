#!/usr/bin/env python
"""
Debug why normal users cannot see GTI members and IT help desk groups
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

def debug_normal_users_groups():
    print("Debugging Normal Users Groups")
    print("=" * 50)
    
    # IT member usernames
    it_usernames = ['111075', '140287', '230022', '250479', 's20330']
    
    # Test with a normal user (not IT member)
    normal_user = User.objects.exclude(username__in=it_usernames).first()
    if not normal_user:
        print("✗ No normal user found for testing")
        return
    
    print(f"Testing with normal user: {normal_user.username}")
    
    # Check if groups exist
    gti_group = Conversation.objects.filter(group__name='GTI members').first()
    helpdesk_group = Conversation.objects.filter(group__name='IT help desk').first()
    
    print(f"\nGroup existence check:")
    print(f"  - GTI members group exists: {gti_group is not None}")
    print(f"  - IT help desk group exists: {helpdesk_group is not None}")
    
    if gti_group:
        print(f"    - GTI group ID: {gti_group.id}")
    if helpdesk_group:
        print(f"    - Helpdesk group ID: {helpdesk_group.id}")
    
    # Check if normal user is participant in groups
    print(f"\nParticipant check:")
    if gti_group:
        gti_participant = ConversationParticipant.objects.filter(
            user=normal_user, conversation=gti_group
        ).exists()
        print(f"  - User in GTI members group: {gti_participant}")
    
    if helpdesk_group:
        helpdesk_participant = ConversationParticipant.objects.filter(
            user=normal_user, conversation=helpdesk_group
        ).exists()
        print(f"  - User in IT help desk group: {helpdesk_participant}")
    
    # Simulate the normal user view logic from views.py
    print(f"\nSimulating normal user view logic:")
    
    is_it_member = normal_user.username in it_usernames
    print(f"  - Is IT member: {is_it_member}")
    
    if not is_it_member:
        # Get GTI members group
        gti_group_conv = Conversation.objects.filter(
            conversation_type='group',
            group__name='GTI members',
            participants=normal_user
        ).first()
        
        # Get IT help desk group
        helpdesk_group_conv = Conversation.objects.filter(
            conversation_type='group',
            group__name='IT help desk',
            participants=normal_user
        ).first()
        
        print(f"  - GTI group found: {gti_group_conv is not None}")
        print(f"  - Helpdesk group found: {helpdesk_group_conv is not None}")
        
        # Combine groups
        all_conversations = []
        if gti_group_conv:
            all_conversations.append(gti_group_conv)
        if helpdesk_group_conv:
            all_conversations.append(helpdesk_group_conv)
        
        print(f"  - Total conversations to show: {len(all_conversations)}")
        
        # Apply filtering
        conversations = Conversation.objects.filter(
            id__in=[conv.id for conv in all_conversations]
        ).exclude(
            participants__is_superuser=True
        ).filter(
            participants__isnull=False
        )
        
        print(f"  - After filtering: {conversations.count()} conversations")
        
        # Check if groups are being filtered out
        if gti_group_conv:
            in_final = conversations.filter(id=gti_group_conv.id).exists()
            print(f"  - GTI group in final list: {in_final}")
        
        if helpdesk_group_conv:
            in_final = conversations.filter(id=helpdesk_group_conv.id).exists()
            print(f"  - Helpdesk group in final list: {in_final}")
        
        # Check for superuser participants
        print(f"\nSuperuser participant check:")
        if gti_group_conv:
            gti_superusers = ConversationParticipant.objects.filter(
                conversation=gti_group_conv, user__is_superuser=True
            )
            print(f"  - GTI group superusers: {gti_superusers.count()}")
            for p in gti_superusers:
                print(f"    - {p.user.username}")
        
        if helpdesk_group_conv:
            helpdesk_superusers = ConversationParticipant.objects.filter(
                conversation=helpdesk_group_conv, user__is_superuser=True
            )
            print(f"  - Helpdesk group superusers: {helpdesk_superusers.count()}")
            for p in helpdesk_superusers:
                print(f"    - {p.user.username}")
    
    print("\n" + "=" * 50)
    print("DEBUG COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    debug_normal_users_groups()
