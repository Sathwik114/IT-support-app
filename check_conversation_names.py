import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

print("Checking all conversations for admin references...")

# Check all groups
groups = Group.objects.all()
print(f"\nGroups ({groups.count()}):")
for group in groups:
    if 'admin' in group.name.lower():
        print(f"  FOUND 'admin' in group: {group.name}")
    else:
        print(f"  {group.name}")

# Check all conversations
conversations = Conversation.objects.all()
print(f"\nConversations ({conversations.count()}):")

for conv in conversations:
    if conv.conversation_type == 'group' and conv.group:
        if 'admin' in conv.group.name.lower():
            print(f"  FOUND 'admin' in group conversation: {conv.group.name}")
    else:
        # Individual conversation - check participant names
        participants = conv.participants.all()
        names = [p.get_full_name() or p.username for p in participants]
        for name in names:
            if 'admin' in name.lower():
                print(f"  FOUND 'admin' in individual conversation participants: {', '.join(names)}")
                break

print("\nDone!")
