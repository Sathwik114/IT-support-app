#!/usr/bin/env python
"""
Test message sending API endpoint
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

User = get_user_model()

def test_message_api():
    print("Testing Message Sending API")
    print("=" * 60)
    
    # Get admin user and individual conversation
    admin_user = User.objects.filter(username='admin').first()
    individual_conv = Conversation.objects.filter(id=49).first()
    
    if admin_user and individual_conv:
        print(f"Testing with user: {admin_user.username}")
        print(f"Individual conversation: {individual_conv.id}")
        
        # Create request factory
        factory = RequestFactory()
        
        # Test data
        test_data = {
            'conversation_id': individual_conv.id,
            'content': 'Test message from API',
            'message_type': 'text'
        }
        
        # Create POST request
        request = factory.post(
            '/api/messaging/messages/',
            data=json.dumps(test_data),
            content_type='application/json'
        )
        
        # Set user
        request.user = admin_user
        
        try:
            # Call the view
            response = send_message(request)
            print(f"  - Response status: {response.status_code}")
            
            # Parse response
            if hasattr(response, 'content'):
                content = response.content.decode('utf-8')
                print(f"  - Response content: {content}")
            
            # Check if message was created
            messages = individual_conv.messages.all()
            print(f"  - Total messages after API call: {messages.count()}")
            
            for msg in messages.order_by('-created_at')[:2]:
                print(f"    - {msg.sender.username}: {msg.content[:50]} ({msg.created_at})")
                
        except Exception as e:
            print(f"  - Error calling API: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("TEST COMPLETE!")
    print("=" * 60)

if __name__ == "__main__":
    test_message_api()
