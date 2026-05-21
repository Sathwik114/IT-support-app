#!/usr/bin/env python
"""
Revert all changes made today back to original state
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from django.contrib.auth import get_user_model
from messaging.models import Conversation, Group, ConversationParticipant

User = get_user_model()

def revert_project():
    print("Reverting Project to Original State")
    print("=" * 50)
    
    # 1. Remove all custom groups created today
    print("1. Removing custom groups...")
    
    groups_to_remove = ['GTI members', 'IT help desk', 'IT Dept personal', 'normal messages']
    
    for group_name in groups_to_remove:
        group_conv = Conversation.objects.filter(group__name=group_name).first()
        if group_conv:
            print(f"  - Removing {group_name} group")
            group_conv.delete()
        else:
            print(f"  - {group_name} group not found")
    
    # 2. Create original IT group
    print("\n2. Creating original IT group...")
    all_users = User.objects.all()
    creator = User.objects.filter(username='s20330').first()
    
    it_conv = Conversation.objects.create(
        conversation_type='group',
        updated_at=django.utils.timezone.now()
    )
    
    Group.objects.create(
        conversation=it_conv,
        name='IT',
        description='IT group',
        created_by=creator
    )
    
    # Add all users to IT group
    for user in all_users:
        ConversationParticipant.objects.create(
            user=user, conversation=it_conv
        )
    
    print(f"  ✓ IT group created with {all_users.count()} members")
    
    # 3. Revert views.py to original state
    print("\n3. Reverting views.py...")
    
    views_file = 'messaging/views.py'
    if os.path.exists(views_file):
        print("  ✓ views.py exists - you may need to manually revert IT usernames")
        print("  - Change IT usernames back to: ['s20330', '250479', '230022', '140287', '111075']")
        print("  - Remove any GTI/Helpdesk group references")
    
    # 4. Clean up created files
    print("\n4. Cleaning up created files...")
    
    files_to_remove = [
        'create_groups_directly.py',
        'fix_it_helpdesk_all_users.py', 
        'create_normal_messages_group.py',
        'create_required_groups.py',
        'create_it_dept_personal.py',
        'debug_message_error.py',
        'fix_missing_groups.py',
        'add_all_users_to_helpdesk.py',
        'check_visible_groups.py'
    ]
    
    for file_name in files_to_remove:
        file_path = file_name
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
                print(f"  ✓ Removed {file_name}")
            except:
                print(f"  - Could not remove {file_name}")
        else:
            print(f"  - {file_name} not found")
    
    print("\n" + "=" * 50)
    print("PROJECT REVERTED TO ORIGINAL STATE!")
    print("=" * 50)
    print("\nNext steps:")
    print("1. Manually check views.py for any remaining changes")
    print("2. Restart Django server")
    print("3. Test original IT group functionality")

if __name__ == "__main__":
    revert_project()
