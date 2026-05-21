import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

print("Users:")
for u in User.objects.all():
    print(f"  {u.username}: {u.get_full_name() or u.username}")

print("\nGroups:")
for g in Group.objects.all():
    print(f"  {g.name} (ID: {g.conversation.id})")

print("\nConversations for s20330:")
for c in Conversation.objects.filter(participants__username='s20330'):
    try:
        if c.group:
            print(f"  {c.id}: {c.conversation_type} - {c.group.name}")
        else:
            other = c.participants.exclude(username='s20330').first()
            print(f"  {c.id}: {c.conversation_type} - Individual with {other.username if other else 'Unknown'}")
    except:
        print(f"  {c.id}: {c.conversation_type} - No group")

print("\nConversations for 250479:")
for c in Conversation.objects.filter(participants__username='250479'):
    try:
        if c.group:
            print(f"  {c.id}: {c.conversation_type} - {c.group.name}")
        else:
            other = c.participants.exclude(username='250479').first()
            print(f"  {c.id}: {c.conversation_type} - Individual with {other.username if other else 'Unknown'}")
    except:
        print(f"  {c.id}: {c.conversation_type} - No group")
