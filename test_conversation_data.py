#!/usr/bin/env python
"""
Test conversation data structure for frontend
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

def test_conversation_data():
    print("Testing Conversation Data Structure")
    print("=" * 60)
    
    # Test with admin user
    admin_user = User.objects.filter(username='admin').first()
    if admin_user:
        print(f"Testing with admin user: {admin_user.username}")
        
        # Simulate the conversation list API call
        it_usernames = ['s20330', '250479', '230022', '140287', '111075']
        it_members = User.objects.filter(username__in=it_usernames)
        
        # Get GTI members group
        gti_group_conv = Conversation.objects.filter(
            conversation_type='group',
            group__name='GTI members',
            participants=admin_user
        ).first()
        
        # Get IT help desk group
        helpdesk_group_conv = Conversation.objects.filter(
            conversation_type='group',
            group__name='IT help desk',
            participants=admin_user
        ).first()
        
        # Get all individual chats
        individual_chats = Conversation.objects.filter(
            conversation_type='individual',
            participants=admin_user
        ).annotate(
            last_message_time=Max('messages__created_at'),
            unread_count=Count(
                'messages',
                filter=Q(messages__status__in=['sent', 'delivered']) & ~Q(messages__sender=admin_user) &
                       ~Q(messages__read_receipts__user=admin_user)
            )
        ).order_by('-last_message_time')
        
        # Combine conversations
        all_conversations = []
        if gti_group_conv:
            all_conversations.append(gti_group_conv)
        if helpdesk_group_conv:
            all_conversations.append(helpdesk_group_conv)
        all_conversations.extend(individual_chats)
        
        # Annotate and order
        conversations = Conversation.objects.filter(
            id__in=[conv.id for conv in all_conversations]
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
        
        print(f"  - Total conversations: {conversations.count()}")
        
        # Test data structure for each conversation
        conversations_data = []
        for conv in conversations:
            conv_data = {
                'id': conv.id,
                'conversation_type': conv.conversation_type,
                'updated_at': conv.updated_at.isoformat(),
                'unread_count': conv.unread_count,
            }
            
            if conv.conversation_type == 'group':
                group = conv.group
                conv_data['name'] = group.name
                conv_data['group_picture'] = group.group_picture.url if group.group_picture else None
                conv_data['description'] = group.description
                
                # Check if user can send messages in this group
                is_it_member = admin_user.username in it_usernames
                
                # GTI members group - only IT members can send messages
                if group.name == 'GTI members':
                    conv_data['can_send_messages'] = is_it_member
                else:
                    conv_data['can_send_messages'] = True
            else:
                other_user = conv.get_other_participant(admin_user)
                if other_user:
                    conv_data['name'] = other_user.get_full_name() or other_user.username
                    conv_data['username'] = other_user.username
                    conv_data['profile_picture'] = other_user.profile_picture.url if other_user.profile_picture else None
                    conv_data['status'] = other_user.status
            
            # Get last message
            last_message = conv.messages.last()
            if last_message:
                conv_data['last_message'] = {
                    'content': last_message.content[:50] if last_message.message_type == 'text' else f'[{last_message.message_type}]',
                    'sender': last_message.sender.username,
                    'created_at': last_message.created_at.isoformat(),
                    'message_type': last_message.message_type,
                }
            
            conversations_data.append(conv_data)
            
            # Print conversation details
            if conv.conversation_type == 'group':
                print(f"    - Group: {conv_data['name']}")
            else:
                print(f"    - Individual: {conv_data.get('name', 'Unknown')} (username: {conv_data.get('username', 'Unknown')})")
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_conversation_data()
