import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

print("Creating IT member personal chats...")

# Get IT members
it_members = User.objects.filter(username__in=['s20330', '250479', '230022', '140287', '111075'])

# Create IT personal group if it doesn't exist
it_personal_group = Group.objects.filter(name='IT personal').first()
if not it_personal_group:
    # Create conversation
    conversation = Conversation.objects.create(conversation_type='group')
    conversation.participants.add(*it_members)
    
    # Create group
    it_personal_group = Group.objects.create(
        conversation=conversation,
        name='IT personal',
        description='IT Members Personal Chat',
        created_by=it_members.first()
    )
    it_personal_group.admins.add(*it_members)
    
    print(f"✓ Created IT personal group with {it_members.count()} IT members")
else:
    print(f"✓ IT personal group already exists")

# Ensure all IT members are in the group
conv = it_personal_group.conversation
for member in it_members:
    if not conv.participants.filter(id=member.id).exists():
        conv.participants.add(member)
        print(f"✓ Added {member.username} to IT personal group")

print(f"\nIT Personal Group Participants: {conv.participants.count()}")
for participant in conv.participants.all():
    print(f"- {participant.username} ({participant.get_full_name()})")
