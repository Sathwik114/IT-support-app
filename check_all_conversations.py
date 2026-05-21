#!/usr/bin/env python
"""
Check all conversations for admin user
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

def check_all_conversations():
    print("Checking All Conversations for Admin User")
    print("=" * 60)
    
    # Test with admin user
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"Testing with admin user: {admin_user.username}")
        
        # Get all conversations
        all_conversations = Conversation.objects.filter(
            participants=admin_user
        ).filter(
            participants__isnull=False
        ).annotate(
            last_message_time=Max('messages__created_at'),
            unread_count=Count(
                'messages',
                filter=Q(messages__status__in=['sent', 'delivered']) & ~Q(messages__sender=admin_user) &
                       ~Q(messages__read_receipts__user=admin_user)
            )
        ).order_by('-last_message_time')
        
        print(f"  - Total conversations found: {all_conversations.count()}")
        
        for conv in all_conversations:
            if conv.conversation_type == 'group':
                print(f"    - Group: {conv.group.name} (ID: {conv.id})")
            else:
                other_user = conv.get_other_participant(admin_user)
                if other_user:
                    print(f"    - Individual: {other_user.username} (ID: {conv.id})")
                else:
                    print(f"    - Individual: No other participant (ID: {conv.id})")
        
        # Check conversation participants
        for conv in all_conversations:
            participants = conv.participants.all()
            print(f"Conversation {conv.id} participants:")
            for p in participants:
                print(f"  - {p.username}")
    
    print("\n" + "=" * 60)
    print("CHECK COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    check_all_conversations()
