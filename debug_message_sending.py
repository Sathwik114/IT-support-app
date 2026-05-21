#!/usr/bin/env python
"""
Debug message sending for individual conversations
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db.models import Max, Count, Q
from messaging.models import Conversation, Group, ConversationParticipant, Message

User = get_user_model()

def debug_message_sending():
    print("Debugging Message Sending for Individual Conversations")
    print("=" * 60)
    
    # Get admin user and test individual conversation
    admin_user = User.objects.filter(username='admin').first()
    individual_conv = Conversation.objects.filter(id=49).first()
    
    if admin_user and individual_conv:
        print(f"Testing with user: {admin_user.username}")
        print(f"Individual conversation: {individual_conv.id}")
        
        # Check if user is participant
        is_participant = individual_conv.participants.filter(id=admin_user.id).exists()
        print(f"  - User is participant: {is_participant}")
        
        # Check conversation type
        print(f"  - Conversation type: {individual_conv.conversation_type}")
        
        # Check other participant
        other_user = individual_conv.get_other_participant(admin_user)
        if other_user:
            print(f"  - Other participant: {other_user.username}")
        
        # Test message creation
        try:
            test_message = Message.objects.create(
                conversation=individual_conv,
                sender=admin_user,
                content="Test message for debugging",
                message_type='text'
            )
            print(f"  - Test message created: {test_message.id}")
            print(f"  - Message content: {test_message.content}")
            print(f"  - Message sender: {test_message.sender.username}")
            
            # Update conversation timestamp
            individual_conv.save()
            print(f"  - Conversation timestamp updated")
            
        except Exception as e:
            print(f"  - Error creating message: {e}")
        
        # Check messages in conversation
        messages = individual_conv.messages.all()
        print(f"  - Total messages in conversation: {messages.count()}")
        
        for msg in messages.order_by('-created_at')[:3]:
            print(f"    - {msg.sender.username}: {msg.content[:50]} ({msg.created_at})")
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    debug_message_sending()
