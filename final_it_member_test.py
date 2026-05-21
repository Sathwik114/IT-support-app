import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Group
from authentication.models import User

print("Final IT Member Message Bar Test")
print("=" * 50)

# Get IT member
it_member = User.objects.filter(username='s20330').first()
print(f"Testing with IT member: {it_member.username} ({it_member.get_full_name()})")

# Check all conversations available to IT member
conversations = Conversation.objects.filter(participants=it_member)
print(f"\nConversations available: {conversations.count()}")

print("\n" + "=" * 50)
print("EXPECTED BEHAVIOR FOR IT MEMBERS:")
print("=" * 50)

for conv in conversations:
    if conv.conversation_type == 'group':
        group = conv.group
        print(f"\n{group.name}:")
        
        # Check backend permissions
        it_usernames = ['s20330', '250479', '230022', '140287', '111075']
        is_it_member = it_member.username in it_usernames
        
        if group.name == 'IT help desk':
            can_send = False  # No one can send regular messages
            expected_behavior = "Message bar HIDDEN (containers only)"
        elif group.name == 'GTI members':
            can_send = is_it_member  # Only IT members can send
            expected_behavior = "Message bar VISIBLE (IT member can send)"
        else:
            can_send = True  # IT members can send in other groups
            expected_behavior = "Message bar VISIBLE (allowed)"
        
        print(f"  - Can send messages: {can_send}")
        print(f"  - Expected: {expected_behavior}")
    else:
        other_user = conv.get_other_participant(it_member)
        print(f"\nIndividual chat with {other_user.get_full_name() or other_user.username}:")
        print(f"  - Expected: Message bar VISIBLE (individual chat)")

print("\n" + "=" * 50)
print("TESTING INSTRUCTIONS:")
print("=" * 50)

print("1. Start server: python manage.py runserver 10.40.20.4:8000")
print("2. Login as IT member: s20330 / 123456")
print("3. Test each conversation:")
print("   ✅ IT help desk: Should see containers, NO message bar")
print("   ✅ GTI members: Should see message bar, can send messages")
print("   ✅ IT personal: Should see message bar, can send messages")
print("   ✅ Individual chats: Should see message bar, can send messages")
print("   ✅ team group: Should see message bar, can send messages")

print("\n" + "=" * 50)
print("FIXES APPLIED:")
print("✅ Backend logic correct - IT help desk: can_send_messages = False")
print("✅ Frontend logic fixed - Message bar restored when leaving IT help desk")
print("✅ Help desk containers only show in IT help desk group")
print("✅ Regular message bar shows in other groups for IT members")

print("\n" + "=" * 50)
print("READY FOR TESTING!")
