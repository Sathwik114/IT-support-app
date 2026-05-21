#!/usr/bin/env python
"""
ASGI entry point for running Django with Daphne or Uvicorn.
"""

import os
import sys
import django

from django.core.asgi import get_asgi_application

# Set the default settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'chat_system.settings')

# Setup Django
django.setup()

# Get the ASGI application
application = get_asgi_application()

if __name__ == '__main__':
    import uvicorn
    # Run with Uvicorn
    # To run: python run_asgi.py
    # Or with specific host/port: python run_asgi.py --host 0.0.0.0 --port 8000
    uvicorn.run(
        'chat_system.asgi:application',
        host='0.0.0.0',
        port=8000,
        reload=True,
        log_level='info'
    )
