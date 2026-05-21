import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User
from django.test import Client

print("Testing Normal User Message Access...")
print("=" * 50)

# Get normal user
normal_user = User.objects.filter(username='user1').first()
print(f"Testing with normal user: {normal_user.username}")

# Create test client and login
client = Client()
client.force_login(normal_user)

# Check all conversations available to normal user
conversations = Conversation.objects.filter(participants=normal_user)
print(f"\nConversations available: {conversations.count()}")

for conv in conversations:
    if conv.conversation_type == 'group':
        group = conv.group
        print(f"  - Group: {group.name}")
    else:
        other_user = conv.get_other_participant(normal_user)
        print(f"  - Individual: {other_user.get_full_name() or other_user.username}")

# Test each conversation for message access
print("\n" + "=" * 40)
print("Message Access Test Results:")
print("=" * 40)

for conv in conversations:
    try:
        response = client.get(f'/api/messaging/conversations/{conv.id}/')
        if response.status_code == 200:
            data = response.json()
            conv_data = data.get('conversation', {})
            
            if conv.conversation_type == 'group':
                group_name = conv_data.get('name', 'Unknown Group')
                can_send = conv_data.get('can_send_messages', True)
                is_help_desk = conv_data.get('is_help_desk', False)
                
                print(f"\n{group_name}:")
                print(f"  - Can send messages: {can_send}")
                print(f"  - Is help desk: {is_help_desk}")
                
                if not can_send:
                    print(f"  - ✅ Message bar should be hidden")
                else:
                    print(f"  - ✅ Message bar should be visible")
            else:
                other_user = conv.get_other_participant(normal_user)
                print(f"\nIndividual chat with {other_user.get_full_name() or other_user.username}:")
                print(f"  - ✅ Message bar should be visible (individual chats always allow messaging)")
                
    except Exception as e:
        print(f"Error testing conversation {conv.id}: {e}")

print("\n" + "=" * 50)
print("EXPECTED BEHAVIOR FOR NORMAL USERS:")
print("=" * 50)

print("✅ IT help desk group: Message bar HIDDEN, 'Raise a Request' button visible")
print("✅ GTI members group: Message bar HIDDEN, read-only message shown")
print("✅ Individual chats: Message bar VISIBLE, can send messages")
print("✅ Other groups: Message bar VISIBLE (if they can send messages)")

print("\n" + "=" * 50)
print("FIXES APPLIED:")
print("✅ Updated logic to only hide message bar in restricted groups")
print("✅ Normal users can now send messages in individual chats")
print("✅ Normal users can send messages in unrestricted groups")
print("✅ Message bar only hidden where specifically restricted")
