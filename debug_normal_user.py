import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import HelpDeskContainer, Group
from authentication.models import User
from django.test import Client

print("Debugging Normal User View...")
print("=" * 50)

# Get normal user
normal_user = User.objects.filter(username='user1').first()
if not normal_user:
    print("❌ Normal user user1 not found")
    exit(1)

print(f"✅ Normal user: {normal_user.username}")

# Create a test client and login as normal user
client = Client()
client.force_login(normal_user)

# Test the help desk containers API for normal user
try:
    response = client.get('/api/messaging/helpdesk/containers/')
    print(f"API Response Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"✅ API Response successful")
        print(f"Is IT Member: {data.get('is_it_member')}")
        print(f"Containers count: {len(data.get('containers', []))}")
        
        # Show container details
        for container in data.get('containers', []):
            print(f"  Container #{container['container_id']}:")
            print(f"    - Status: {container['status']}")
            print(f"    - Requester: {container['requester']['username']}")
            print(f"    - Taken by: {container['taken_by']['username'] if container['taken_by'] else 'None'}")
            
        # Check if user should see containers
        user_containers = [c for c in data.get('containers', []) if c['requester']['username'] == normal_user.username]
        print(f"\nContainers for {normal_user.username}: {len(user_containers)}")
        
        if len(user_containers) == 0:
            print("❌ This user has no containers - should see 'Raise a Request' button and empty state")
        else:
            print("✅ This user has containers - should see their containers")
            
    else:
        print(f"❌ API Error: {response.content.decode()}")
        
except Exception as e:
    print(f"❌ API Test Error: {e}")

# Test conversation detail API
print("\n" + "=" * 30)
print("Testing Conversation Detail API...")
try:
    helpdesk_group = Group.objects.filter(name='IT help desk').first()
    if helpdesk_group:
        response = client.get(f'/api/messaging/conversations/{helpdesk_group.conversation.id}/')
        print(f"Conversation API Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            conv = data.get('conversation', {})
            print(f"Is Help Desk: {conv.get('is_help_desk')}")
            print(f"Can Send Messages: {conv.get('can_send_messages')}")
            print(f"Can Create Request: {conv.get('can_create_request')}")
            print(f"Help Desk Containers: {len(conv.get('helpdesk_containers', []))}")
        else:
            print(f"❌ Conversation API Error: {response.content.decode()}")
            
except Exception as e:
    print(f"❌ Conversation API Error: {e}")

print("\n" + "=" * 50)
print("EXPECTED NORMAL USER EXPERIENCE:")
print("✅ Should see help desk containers area")
print("✅ Should see 'Raise a Request' button")
print("✅ Should see their own containers (if any)")
print("✅ Should NOT see message input area")
