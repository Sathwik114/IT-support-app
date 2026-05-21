#!/usr/bin/env python
"""
Trace through send_message function step by step
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.test import RequestFactory
from messaging.models import Conversation, Message
import json
import traceback

User = get_user_model()

def trace_send_message():
    print("Tracing send_message function step by step")
    print("=" * 60)
    
    # Get admin user and individual conversation
    admin_user = User.objects.filter(username='admin').first()
    individual_conv = Conversation.objects.filter(id=49).first()
    
    if admin_user and individual_conv:
        print(f"Step 1: User and conversation loaded")
        print(f"  - User: {admin_user.username}")
        print(f"  - Conversation ID: {individual_conv.id}")
        print(f"  - Conversation type: {individual_conv.conversation_type}")
        
        # Check if conversation has group attribute
        print(f"Step 2: Checking conversation.group")
        try:
            group = individual_conv.group
            print(f"  - conversation.group: {group}")
        except Exception as e:
            print(f"  - Error accessing conversation.group: {e}")
        
        # Check if conversation has get_other_participant
        print(f"Step 3: Checking get_other_participant")
        try:
            other_user = individual_conv.get_other_participant(admin_user)
            print(f"  - Other participant: {other_user.username if other_user else 'None'}")
        except Exception as e:
            print(f"  - Error in get_other_participant: {e}")
            traceback.print_exc()
        
        # Check if user is participant
        print(f"Step 4: Checking participant status")
        try:
            is_participant = individual_conv.participants.filter(id=admin_user.id).exists()
            print(f"  - User is participant: {is_participant}")
        except Exception as e:
            print(f"  - Error checking participant: {e}")
        
        # Test creating message directly
        print(f"Step 5: Testing direct message creation")
        try:
            test_message = Message.objects.create(
                conversation=individual_conv,
                sender=admin_user,
                content="Direct test message",
                message_type='text'
            )
            print(f"  - Message created successfully: {test_message.id}")
        except Exception as e:
            print(f"  - Error creating message: {e}")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TRACE COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    trace_send_message()
