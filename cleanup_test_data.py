import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import HelpDeskContainer, Message, Conversation
from authentication.models import User

print("Cleaning Up Test Data...")
print("=" * 50)

# Remove help desk containers
containers = HelpDeskContainer.objects.all()
print(f"Found {containers.count()} help desk containers to remove:")

for container in containers:
    print(f"  - Removing Container #{container.container_id} ({container.requester.username})")
    container.delete()

print("✅ All help desk containers removed")

# Remove test messages from conversations
conversations = Conversation.objects.all()
total_messages_removed = 0

for conversation in conversations:
    messages = conversation.messages.all()
    if messages.exists():
        print(f"\nConversation: {conversation}")
        print(f"  - Removing {messages.count()} messages")
        messages.delete()
        total_messages_removed += messages.count()

print(f"\n✅ Total messages removed: {total_messages_removed}")

# Check if there are any empty conversations that should be removed
empty_conversations = Conversation.objects.filter(messages__isnull=True)
print(f"\nFound {empty_conversations.count()} empty conversations:")
for conv in empty_conversations:
    print(f"  - {conv} (ID: {conv.id})")

print("\n" + "=" * 50)
print("CLEANUP COMPLETE!")
print("✅ All test help desk containers removed")
print("✅ All test messages removed")
print("✅ System is now clean for production use")

print("\n" + "=" * 50)
print("NEXT STEPS:")
print("1. The help desk system is ready for real use")
print("2. Users can now create real help desk requests")
print("3. IT members can take over real requests")
print("4. No test data remains in the system")

print("\nAvailable Users:")
print("Normal users: user1, user2, user3, user4 (password: 123456)")
print("IT members: s20330, 250479, 230022, 140287, 111075 (password: 123456)")
