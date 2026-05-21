import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group

# Remove individual IT member groups (keep only IT group)
groups_to_remove = ['Sathya Sathwik Pushpagiri', 'Rajesh', 'Shakeer', 'Narasimha', 'Masthan']

print("Removing individual IT member groups...")
for group_name in groups_to_remove:
    try:
        group = Group.objects.get(name=group_name)
        conv = group.conversation
        print(f"Removing group: {group_name} (ID: {conv.id})")
        group.delete()
        conv.delete()
    except Group.DoesNotExist:
        print(f"Group {group_name} not found")

print("\nDone! Only IT group remains.")
