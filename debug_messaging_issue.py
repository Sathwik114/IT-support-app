#!/usr/bin/env python
"""
Debug why individual messaging is not working
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

def debug_messaging_issue():
    print("Debugging Individual Messaging Issue")
    print("=" * 60)
    
    # Check all users
    all_users = User.objects.all()
    print(f"Total users: {all_users.count()}")
    
    # Check admin user specifically
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"\nChecking admin user: {admin_user.username}")
        
        # Get all conversations for admin
        admin_conversations = Conversation.objects.filter(
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
        
        print(f"  - Admin conversations: {admin_conversations.count()}")
        
        for conv in admin_conversations:
            if conv.conversation_type == 'group':
                print(f"    - Group: {conv.group.name}")
            else:
                other_user = conv.get_other_participant(admin_user)
                if other_user:
                    print(f"    - Individual: {other_user.username}")
                else:
                    print(f"    - Individual: No other participant")
        
        # Check if the individual conversation we created exists
        test_conv = Conversation.objects.filter(id=49).first()
        if test_conv:
            print(f"\nTest conversation 49 exists:")
            print(f"  - Type: {test_conv.conversation_type}")
            participants = test_conv.participants.all()
            print(f"  - Participants: {participants.count()}")
            for p in participants:
                print(f"    - {p.username}")
        else:
            print(f"\nTest conversation 49 does not exist")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    debug_messaging_issue()
