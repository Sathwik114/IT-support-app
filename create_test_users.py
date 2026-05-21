import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

print("Creating test users for enhanced help desk system...")

# Create normal users for testing
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
    # Add all users to IT help desk group
    all_users = User.objects.exclude(username='admin')
    
    for user in all_users:
        conv = helpdesk_group.conversation
        if not conv.participants.filter(id=user.id).exists():
            conv.participants.add(user)
            print(f"✓ Added {user.username} to IT help desk group")
    
    print(f"\n✓ IT help desk group now has {helpdesk_group.conversation.participants.count()} participants")
else:
    print("❌ IT help desk group not found!")

print("\nTest Users Created:")
for user in normal_users:
    print(f"- {user.username} ({user.get_full_name()}) - Password: 123456")

print("\nIT Members:")
it_members = User.objects.filter(username__in=['s20330', '250479', '230022', '140287', '111075'])
for member in it_members:
    print(f"- {member.username} ({member.get_full_name()}) - Password: 123456")
