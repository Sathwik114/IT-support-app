import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

print("Creating normal users and setting up IT help desk access...")

# Create some normal users for testing
normal_users_data = [
    {'username': 'user1', 'first_name': 'John', 'last_name': 'Doe'},
    {'username': 'user2', 'first_name': 'Jane', 'last_name': 'Smith'},
    {'username': 'user3', 'first_name': 'Bob', 'last_name': 'Wilson'},
    {'username': 'user4', 'first_name': 'Alice', 'last_name': 'Brown'},
]

normal_users = []
for user_data in normal_users_data:
    username = user_data['username']
    if User.objects.filter(username=username).exists():
        user = User.objects.get(username=username)
        print(f"✓ Normal user {username} already exists")
    else:
        user = User.objects.create_user(
            username=username,
            email=f'{username}@chat.com',
            password='123456',
            first_name=user_data.get('first_name', ''),
            last_name=user_data.get('last_name', '')
        )
        print(f"✓ Created normal user: {username}")
    normal_users.append(user)

# Get IT help desk group
helpdesk_group = Group.objects.filter(name='IT help desk').first()
if helpdesk_group:
    # Add all users (IT members + normal users) to IT help desk group
    all_users = User.objects.all()
    
    for user in all_users:
        # Skip admin user
        if user.username == 'admin':
            continue
            
        conv = helpdesk_group.conversation
        if not conv.participants.filter(id=user.id).exists():
            conv.participants.add(user)
            print(f"✓ Added {user.username} to IT help desk group")
    
    print(f"\n✓ IT help desk group now has {helpdesk_group.conversation.participants.count()} participants")
else:
    print("✗ IT help desk group not found!")

print("\nSetup complete!")
print("\nNormal Users (password: 123456):")
for user in normal_users:
    print(f"- {user.username} ({user.get_full_name()})")

print("\nIT Help Desk Group Participants:")
if helpdesk_group:
    participants = helpdesk_group.conversation.participants.all()
    for participant in participants:
        user_type = "IT Member" if participant.username in ['s20330', '250479', '230022', '140287', '111075'] else "Normal User"
        print(f"- {participant.username} ({user_type})")
