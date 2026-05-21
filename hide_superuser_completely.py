import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Conversation, Message
from authentication.models import User

print("Completely hiding superuser from chat system...")

# Find admin superuser
admin_user = User.objects.filter(username='admin').first()

if admin_user:
    print(f"Found admin user: {admin_user.username}")
    
    # Remove from all conversations
    conversations = Conversation.objects.filter(participants=admin_user)
    print(f"Removing from {conversations.count()} conversations...")
    
    for conv in conversations:
        conv.participants.remove(admin_user)
        print(f"  - Removed from conversation {conv.id}")
        
        # Delete empty conversations
        if conv.participants.count() == 0:
            conv.delete()
            print(f"    ✓ Deleted empty conversation")
    
    # Delete all messages sent by admin
    messages = Message.objects.filter(sender=admin_user)
    print(f"Deleting {messages.count()} messages sent by admin...")
    messages.delete()
    
    print("✓ Admin user completely removed from chat system")
else:
    print("No admin user found")

# Check for any undefined or problematic conversations
print("\nChecking for undefined/empty conversations...")
all_conversations = Conversation.objects.all()
problematic_convs = []

for conv in all_conversations:
    # Check if conversation has no participants
    if conv.participants.count() == 0:
        problematic_convs.append(conv)
        print(f"  - Found empty conversation {conv.id}")
    
    # Check if conversation has only superuser participants
    non_superuser_participants = conv.participants.filter(is_superuser=False)
    if non_superuser_participants.count() == 0:
        problematic_convs.append(conv)
        print(f"  - Found conversation {conv.id} with only superuser participants")

# Delete problematic conversations
for conv in problematic_convs:
    conv.delete()
    print(f"  ✓ Deleted problematic conversation {conv.id}")

print("\nDone! Superuser is completely hidden from chat system.")
