#!/usr/bin/env python
"""
Debug individual conversation display issues
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

def debug_individual_display():
    print("Debugging Individual Conversation Display")
    print("=" * 60)
    
    # Test with a normal user
    normal_user = User.objects.exclude(username__in=['s20330', '250479', '230022', '140287', '111075']).first()
    if normal_user:
        print(f"Testing with normal user: {normal_user.username}")
        
        # Get individual conversations
        individual_chats = Conversation.objects.filter(
            conversation_type='individual',
            participants=normal_user
        ).filter(
            participants__isnull=False
        ).annotate(
            last_message_time=Max('messages__created_at'),
            unread_count=Count(
                'messages',
                filter=Q(messages__status__in=['sent', 'delivered']) & ~Q(messages__sender=normal_user) &
                       ~Q(messages__read_receipts__user=normal_user)
            )
        ).order_by('-last_message_time')
        
        print(f"  - Individual chats found: {individual_chats.count()}")
        
        for chat in individual_chats:
            other_user = chat.get_other_participant(normal_user)
            if other_user:
                print(f"    - Chat with {other_user.username} (ID: {chat.id})")
                print(f"      Other user data: {other_user.get_full_name()}")
            else:
                print(f"    - Chat ID {chat.id}: No other participant found")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    debug_individual_display()
