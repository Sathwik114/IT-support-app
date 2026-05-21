#!/usr/bin/env python
"""
Find the source of "Conversation has no group" error
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
from messaging.views import send_message
import json
import traceback

User = get_user_model()

def debug_error_source():
    print("Finding Source of 'Conversation has no group' Error")
    print("=" * 60)
    
    # Get admin user and individual conversation
    admin_user = User.objects.filter(username='admin').first()
    individual_conv = Conversation.objects.filter(id=49).first()
    
    if admin_user and individual_conv:
        print(f"Testing with user: {admin_user.username}")
        print(f"Individual conversation: {individual_conv.id}")
        print(f"Conversation type: {individual_conv.conversation_type}")
        
        # Test data
        test_data = {
            'conversation_id': individual_conv.id,
            'content': 'Test message from API',
            'message_type': 'text'
        }
        
        # Create request factory
        factory = RequestFactory()
        
        # Create POST request
        request = factory.post(
            '/api/messaging/messages/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Set user
        request.user = admin_user
        
        try:
            # Call view with detailed traceback
            print("Calling send_message view...")
            response = send_message(request)
            print(f"Response status: {response.status_code}")
            
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                print(f"Response content: {content}")
                
        except Exception as e:
            print(f"Exception occurred: {e}")
            print("Full traceback:")
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("DEBUG COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    debug_error_source()
