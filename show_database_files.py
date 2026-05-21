#!/usr/bin/env python
"""
Script to show how files are stored in the database
"""
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')
django.setup()

from messaging.models import Message, Conversation
from django.core.files.storage import default_storage

def show_file_storage():
    print("=" * 60)
    print("DATABASE FILE STORAGE ANALYSIS")
    print("=" * 60)
    
    # Get all messages with files
    file_messages = Message.objects.exclude(media_file__isnull=True).exclude(media_file='')
    
    print(f"\nTotal messages with files: {file_messages.count()}")
    print("\n" + "=" * 60)
    
    for message in file_messages.order_by('-created_at')[:10]:  # Show last 10
        print(f"\nMessage ID: {message.id}")
        print(f"Sender: {message.sender.username}")
        print(f"Conversation: {message.conversation}")
        print(f"Message Type: {message.message_type}")
        print(f"File Name: {message.file_name}")
        print(f"File Size: {message.file_size} bytes")
        print(f"Created: {message.created_at}")
        
        # Show file path
        if message.media_file:
            print(f"File Path: {message.media_file.name}")
            print(f"File URL: {message.media_file.url}")
            
            # Check if file exists
            if default_storage.exists(message.media_file.name):
                print(f"File Exists: YES")
                print(f"File Size on Disk: {default_storage.size(message.media_file.name)} bytes")
            else:
                print(f"File Exists: NO")
        
        print("-" * 40)
    
    print("\n" + "=" * 60)
    print("FILE STORAGE LOCATION")
    print("=" * 60)
    print(f"Media Root: {settings.MEDIA_ROOT}")
    print(f"Media URL: {settings.MEDIA_URL}")
    
    # Show upload directory structure
    print("\nUpload Directory Structure:")
    if os.path.exists(settings.MEDIA_ROOT):
        for root, dirs, files in os.walk(settings.MEDIA_ROOT):
            level = root.replace(settings.MEDIA_ROOT, '').count(os.sep)
            indent = ' ' * 2 * level
            print(f"{indent}{os.path.basename(root)}/")
            subindent = ' ' * 2 * (level + 1)
            for file in files[:5]:  # Show max 5 files per directory
                print(f"{subindent}{file}")
            if len(files) > 5:
                print(f"{subindent}... and {len(files) - 5} more files")
    else:
        print("Media directory does not exist")

if __name__ == "__main__":
    show_file_storage()
