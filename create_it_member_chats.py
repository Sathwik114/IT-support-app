import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation
from authentication.models import User

# Get all IT members
it_members = User.objects.filter(username__in=['s20330', '250479', '230022', '140287', '111075'])

print("Creating individual chats between IT members...")

# Create individual chats between each pair of IT members
for i, member1 in enumerate(it_members):
    for member2 in it_members[i+1:]:
        # Check if individual chat already exists
        existing_chat = Conversation.objects.filter(
            conversation_type='individual'
        ).filter(participants=member1).filter(participants=member2).first()
        
        if not existing_chat:
            # Create individual chat
            chat = Conversation.objects.create(conversation_type='individual')
            chat.participants.add(member1, member2)
            print(f"Created chat between {member1.get_full_name() or member1.username} and {member2.get_full_name() or member2.username}")
        else:
            print(f"Chat between {member1.get_full_name() or member1.username} and {member2.get_full_name() or member2.username} already exists")

print("\nDone!")
