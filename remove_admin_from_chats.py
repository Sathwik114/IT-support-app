import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from authentication.models import User
from messaging.models import Conversation, Message

print("Removing admin from all conversations...")

# Find any user with 'admin' in username or display name
admin_users = User.objects.filter(username__icontains='admin')

for admin_user in admin_users:
    print(f"\nProcessing user: {admin_user.username}")
    
    # Get all conversations admin is part of
    conversations = Conversation.objects.filter(participants=admin_user)
    
    for conv in conversations:
        # Remove admin from participants
        conv.participants.remove(admin_user)
        print(f"  Removed from conversation ID: {conv.id}")
        
        # If conversation has no participants left, delete it
        if conv.participants.count() == 0:
            print(f"  Deleting empty conversation ID: {conv.id}")
            # Delete messages first
            Message.objects.filter(conversation=conv).delete()
            # Delete conversation
            if conv.group:
                conv.group.delete()
            else:
                conv.delete()

print("\nDone!")
