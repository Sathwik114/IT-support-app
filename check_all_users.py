import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from authentication.models import User

print("All users in the system:")
for user in User.objects.all():
    print(f"  {user.username}: {user.get_full_name() or user.username} ({user.email})")
