import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import HelpDeskContainer, Group
from authentication.models import User
from django.test import Client

print("Testing API Response Format...")
print("=" * 50)

# Get IT member user
it_member = User.objects.filter(username='s20330').first()
if not it_member:
    print("❌ IT member s20330 not found")
    exit(1)

# Create a test client and login
client = Client()
client.force_login(it_member)

# Test the help desk containers API
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
            print(f"    - Should show button: {container['status'] == 'pending'}")
    else:
        print(f"❌ API Error: {response.content.decode()}")
        
except Exception as e:
    print(f"❌ API Test Error: {e}")

print("\n" + "=" * 50)
print("Expected Frontend Behavior:")
print("✅ IT members should see 'I will take over' button for pending containers")
print("✅ Normal users should see 'Raise a Request' button")
print("✅ Message bar should be hidden for normal users in help desk")
print("✅ Container #3 should show 'I will take over' button for IT members")
