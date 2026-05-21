import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

# Get all IT users
it_users = User.objects.filter(username__in=['s20330', '250479', '230022', '140287', '111075'])

# Get all IT member groups
it_groups = Group.objects.filter(name__in=['Sathya Sathwik Pushpagiri', 'Rajesh', 'Shakeer', 'Narasimha', 'Masthan'])

print("Adding IT members to all IT member groups...")
for it_user in it_users:
    print(f"\nProcessing {it_user.username} ({it_user.get_full_name()})")
    for group in it_groups:
        # Don't add user to their own group
        if group.name != it_user.get_full_name():
            conv = group.conversation
            if not conv.participants.filter(id=it_user.id).exists():
                conv.participants.add(it_user)
                print(f"  Added to {group.name}")
            else:
                print(f"  Already in {group.name}")
        else:
            print(f"  Skipped own group: {group.name}")

print("\nDone!")
