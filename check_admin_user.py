import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from authentication.models import User
from messaging.models import Conversation

print("Checking for admin user...")
admin_user = User.objects.filter(username='admin').first()

if admin_user:
    print(f"Found admin user: {admin_user.username}")
    print(f"Email: {admin_user.email}")
    print(f"Full name: {admin_user.get_full_name()}")
    
    # Check conversations admin is part of
    conversations = Conversation.objects.filter(participants=admin_user)
    print(f"\nAdmin is part of {conversations.count()} conversations:")
    for conv in conversations:
        if conv.group:
            print(f"  - Group: {conv.group.name}")
        else:
            other = conv.participants.exclude(username='admin').first()
            print(f"  - Individual with: {other.username if other else 'Unknown'}")
else:
    print("No admin user found")
