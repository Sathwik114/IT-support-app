import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

print("Cleaning IT group - removing non-IT members...")

# Get IT group
it_group = Group.objects.filter(name='IT').first()

if it_group:
    print(f"Found IT group: {it_group.name}")
    
    # Get IT member usernames
    it_usernames = ['s20330', '250479', '230022', '140287', '111075']
    it_users = User.objects.filter(username__in=it_usernames)
    
    # Get current participants
    current_participants = it_group.conversation.participants.all()
    print(f"Current participants ({current_participants.count()}):")
    for p in current_participants:
        print(f"  - {p.username}: {p.get_full_name() or p.username}")
    
    # Remove non-IT members
    removed_count = 0
    for participant in current_participants:
        if participant.username not in it_usernames:
            it_group.conversation.participants.remove(participant)
            print(f"  Removed: {participant.username}")
            removed_count += 1
    
    # Add any missing IT members
    added_count = 0
    for it_user in it_users:
        if not it_group.conversation.participants.filter(id=it_user.id).exists():
            it_group.conversation.participants.add(it_user)
            print(f"  Added: {it_user.username}")
            added_count += 1
    
    print(f"\nSummary: Removed {removed_count} non-IT members, Added {added_count} missing IT members")
    
    # Show final participants
    final_participants = it_group.conversation.participants.all()
    print(f"\nFinal participants ({final_participants.count()}):")
    for p in final_participants:
        print(f"  - {p.username}: {p.get_full_name() or p.username}")
else:
    print("IT group not found")

print("\nDone!")
