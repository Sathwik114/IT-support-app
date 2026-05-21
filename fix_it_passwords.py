import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from authentication.models import User

print("Updating IT member passwords to 123456...")

# IT member usernames
it_usernames = ['s20330', '250479', '230022', '140287', '111075']

for username in it_usernames:
    try:
        user = User.objects.get(username=username)
        user.set_password('123456')
        user.save()
        print(f"✓ Updated password for {username}")
    except User.DoesNotExist:
        print(f"✗ User {username} not found")

print("\nPassword update complete!")
print("All IT members can now login with password: 123456")
