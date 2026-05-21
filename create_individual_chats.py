import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

# Get IT members and normal users
it_members = User.objects.filter(username__in=['s20330', '250479', '230022', '140287', '111075'])
normal_users = User.objects.exclude(username__in=['s20330', '250479', '230022', '140287', '111075'])

print("Creating individual chats for normal users...")

for normal_user in normal_users:
    print(f"\nProcessing {normal_user.username} ({normal_user.get_full_name() or normal_user.username})")
    
    for it_member in it_members:
        # Check if individual chat already exists
        existing_chat = Conversation.objects.filter(
            conversation_type='individual'
        ).filter(participants=normal_user).filter(participants=it_member).first()
        
        if not existing_chat:
            # Create individual chat
            chat = Conversation.objects.create(conversation_type='individual')
            chat.participants.add(normal_user, it_member)
            print(f"  Created chat with {it_member.get_full_name() or it_member.username}")
        else:
            print(f"  Chat with {it_member.get_full_name() or it_member.username} already exists")

print("\nDone!")
