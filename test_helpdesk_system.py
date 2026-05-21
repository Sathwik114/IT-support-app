import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group, HelpDeskRequest
from authentication.models import User

print("Testing Help Desk Request System...")
print("=" * 50)

# Get test users
normal_user = User.objects.filter(username='user1').first()
it_member = User.objects.filter(username='s20330').first()

if not normal_user:
    print("❌ Normal user 'user1' not found")
    exit(1)
if not it_member:
    print("❌ IT member 's20330' not found")
    exit(1)

print(f"✓ Normal user: {normal_user.username} ({normal_user.get_full_name()})")
print(f"✓ IT member: {it_member.username} ({it_member.get_full_name()})")

# Check IT help desk group
helpdesk_group = Group.objects.filter(name='IT help desk').first()
if not helpdesk_group:
    print("❌ IT help desk group not found")
    exit(1)

print(f"✓ IT help desk group found with {helpdesk_group.conversation.participants.count()} participants")

# Test 1: Check if normal user can access IT help desk
helpdesk_conv = Conversation.objects.filter(
    conversation_type='group',
    group__name='IT help desk',
    participants=normal_user
).first()

if helpdesk_conv:
    print(f"✓ Normal user can access IT help desk group")
else:
    print("❌ Normal user cannot access IT help desk group")

# Test 2: Check existing requests
requests = HelpDeskRequest.objects.filter(conversation=helpdesk_conv)
print(f"✓ Current help desk requests: {requests.count()}")

for req in requests:
    print(f"  - Request {req.id}: {req.requester.username} - {req.status}")

# Test 3: Create a test request
print("\nCreating test help desk request...")
test_request = HelpDeskRequest.objects.create(
    conversation=helpdesk_conv,
    requester=normal_user,
    request_message="Test request: My computer is not working properly",
    status='pending'
)

print(f"✓ Created test request #{test_request.id}")

# Test 4: Take the request
print(f"\nIT member taking over request #{test_request.id}...")
test_request.take_request(it_member)
print(f"✓ Request taken by {it_member.username}")

# Test 5: Check final status
updated_request = HelpDeskRequest.objects.get(id=test_request.id)
print(f"✓ Final request status: {updated_request.status}")
print(f"✓ Taken by: {updated_request.taken_by.username if updated_request.taken_by else 'None'}")

print("\n" + "=" * 50)
print("Help Desk System Test Complete! ✅")
print("\nAPI Endpoints Available:")
print("- POST /api/messaging/helpdesk/request/ - Create request (normal users)")
print("- POST /api/messaging/helpdesk/request/<id>/take/ - Take request (IT members)")
print("- GET /api/messaging/helpdesk/requests/ - List all requests")

print("\nLogin Credentials:")
print("Normal user: user1 / 123456")
print("IT member: s20330 / 123456")
