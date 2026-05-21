import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from authentication.models import User

print("Creating admin superuser for admin purposes...")

# Create admin superuser
admin_username = 'admin'
admin_email = 'admin@chat.com'
admin_password = 'admin123'

# Check if admin user already exists
if User.objects.filter(username=admin_username).exists():
    print(f"Admin user '{admin_username}' already exists!")
else:
    # Create admin superuser
    admin_user = User.objects.create_user(
        username=admin_username,
        email=admin_email,
        password=admin_password,
        is_superuser=True,
        is_staff=True,
        first_name='Admin',
        last_name='User'
    )
    print(f"✓ Created admin superuser: {admin_username}")
    print(f"  Email: {admin_email}")
    print(f"  Password: {admin_password}")
    print(f"  This user can access Django admin but will be excluded from chat system")

print("\nAdmin superuser setup complete!")
print("This user can:")
print("- Access Django admin panel at /admin/")
print("- Manage database and system settings")
print("- Will NOT appear in any chat conversations")
print("- Cannot participate in chat system")
