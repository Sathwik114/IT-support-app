import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import HelpDeskContainer
from authentication.models import User

print("Debugging Help Desk Containers...")
print("=" * 50)

# Check all containers
containers = HelpDeskContainer.objects.all()
print(f"Total containers: {containers.count()}")

for container in containers:
    print(f"Container #{container.container_id}:")
    print(f"  - Requester: {container.requester.username}")
    print(f"  - Status: {container.status}")
    print(f"  - Taken by: {container.taken_by.username if container.taken_by else 'None'}")
    print(f"  - Created: {container.created_at}")
    print()

# Check if we have any pending containers
pending_containers = HelpDeskContainer.objects.filter(status='pending')
print(f"Pending containers: {pending_containers.count()}")

if pending_containers.count() == 0:
    print("❌ No pending containers found! This is why 'I will take over' buttons are not showing.")
    print("Creating a test pending container...")
    
    # Get a normal user and IT help desk conversation
    normal_user = User.objects.filter(username='user1').first()
    from messaging.models import Group
    helpdesk_group = Group.objects.filter(name='IT help desk').first()
    
    if normal_user and helpdesk_group:
        # Create a pending container
        new_container = HelpDeskContainer.objects.create(
            conversation=helpdesk_group.conversation,
            requester=normal_user,
            problem_description="Test pending request - This should show 'I will take over' button",
            status='pending'
        )
        print(f"✓ Created pending container #{new_container.container_id}")
        print("Now IT members should see the 'I will take over' button!")
else:
    print("✅ Pending containers found - buttons should be visible for IT members")
