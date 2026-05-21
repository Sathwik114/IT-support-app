#!/usr/bin/env python
"""
Test what IT members actually see in their conversation list
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

def test_it_member_view():
    print("Testing IT Member View")
    print("=" * 50)
    
    # IT member usernames
    it_usernames = ['s20330', '250479', '230022', '140287', '111075']
    
    # Test with first IT member
    test_user = User.objects.filter(username='s20330').first()
    if not test_user:
        print("✗ Test user s20330 not found")
        return
    
    print(f"Testing with user: {test_user.username}")
    
    # Simulate the IT member view logic from views.py
    is_it_member = test_user.username in it_usernames
    print(f"Is IT member: {is_it_member}")
    
    if is_it_member:
        # IT members see all conversations (IT group + IT help desk + individual chats)
        # Exclude superusers and empty conversations
        conversations = Conversation.objects.filter(
            participants=test_user
        ).exclude(
            participants__is_superuser=True
        ).filter(
            participants__isnull=False
        ).annotate(
            last_message_time=Max('messages__created_at'),
            unread_count=Count(
                'messages',
                filter=Q(messages__status__in=['sent', 'delivered']) & ~Q(messages__sender=test_user) &
                       ~Q(messages__read_receipts__user=test_user)
            )
        ).order_by('-last_message_time')
        
        print(f"\nConversations found: {conversations.count()}")
        
        for conv in conversations:
            try:
                group_name = conv.group.name if conv.group else "Individual"
            except:
                group_name = "Individual"
            conv_type = conv.conversation_type
            print(f"  - {group_name} ({conv_type}) ID: {conv.id}")
    
    # Check specifically for IT help desk group
    helpdesk_group = Conversation.objects.filter(group__name='IT help desk').first()
    if helpdesk_group:
        is_participant = ConversationParticipant.objects.filter(
            user=test_user, conversation=helpdesk_group
        ).exists()
        print(f"\nIT help desk group check:")
        print(f"  - Group exists: Yes")
        print(f"  - User is participant: {is_participant}")
        print(f"  - Group ID: {helpdesk_group.id}")
        
        if is_participant:
            # Check if it's in the conversations list
            in_conversations = conversations.filter(id=helpdesk_group.id).exists()
            print(f"  - In conversations list: {in_conversations}")
    
    print("\n" + "=" * 50)
    print("IT MEMBER VIEW TEST COMPLETE!")
    print("=" * 50)

if __name__ == "__main__":
    test_it_member_view()
