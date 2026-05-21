# LAN Chat System

A WhatsApp-like chat management system for LAN environments using Django, Django Channels, Redis, and LDAP authentication.

## Features

- **LDAP Authentication**: Secure login using company directory
- **Real-time Messaging**: Instant messages via WebSockets
- **One-to-One & Group Chats**: Create individual conversations or groups
- **Media Support**: Send images, videos, and files
- **Message Status**: Track sent, delivered, and seen status
- **Typing Indicators**: Real-time typing notifications
- **Online/Offline Status**: See user availability
- **Search**: Find users, chats, and messages
- **Delete Options**: Delete for me or delete for everyone
- **Desktop App**: Electron wrapper for Windows executable

## Tech Stack

- **Backend**: Django 4.2
- **Real-time**: Django Channels 4.0
- **WebSocket Broker**: Redis
- **Authentication**: LDAP (python-ldap)
- **Database**: SQLite (default) or PostgreSQL
- **Frontend**: HTML/CSS/JavaScript
- **Desktop App**: Electron.js

## Prerequisites

- Python 3.9 or higher
- Redis Server
- LDAP Server (for authentication)
- Node.js 16+ (for building desktop app)

## Installation

### 1. Clone the Repository

```bash
cd chat
```

### 2. Create Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your settings:

```env
DEBUG=True
SECRET_KEY=your-secret-key
ALLOWED_HOSTS=10.40.10.125,localhost,127.0.0.1

# LDAP Configuration
LDAP_AUTH_URL=ldap://your-ldap-server:389
LDAP_BASE_DN=dc=company,dc=com
LDAP_BIND_DN=cn=admin,dc=company,dc=com
LDAP_BIND_PASSWORD=your-ldap-password
LDAP_USER_SEARCH_BASE=ou=users,dc=company,dc=com
LDAP_USER_SEARCH_FILTER=(uid=%(user)s)

# Redis Configuration
REDIS_HOST=127.0.0.1
REDIS_PORT=6379
```

### 5. Run Migrations

```bash
python manage.py migrate
```

### 6. Collect Static Files

```bash
python manage.py collectstatic
```

### 7. Create Superuser (Optional)

```bash
python manage.py createsuperuser
```

## Running the Application

### Option 1: Using Daphne (Recommended for Production)

```bash
daphne -b 0.0.0.0 -p 8000 chat_system.asgi:application
```

### Option 2: Using Uvicorn

```bash
python run_asgi.py
```

### Option 3: Using the Deployment Script (Windows)

```bash
deploy.bat
```

The application will be available at `http://0.0.0.0:8000` or `http://10.40.10.125:8000` (your LAN IP).

## Redis Setup

### Windows

1. Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
2. Install and start Redis Server
3. Or use WSL2 to run Redis on Windows

### Linux

```bash
sudo apt-get install redis-server
sudo systemctl start redis-server
sudo systemctl enable redis-server
```

### Verify Redis is Running

```bash
redis-cli ping
# Should return: PONG
```

## LDAP Configuration

The system now uses a database-driven LDAP configuration approach (similar to the Next.js implementation). This allows you to manage LDAP settings and users through the Django Admin interface.

### Database Models

**LDAPConfiguration**: Stores LDAP server settings for different domains
- ConnectionName, HostName, Port, BaseDN
- BindDN, BindPassword for admin operations
- UserSearchBase, UserSearchFilter
- SSL/TLS options

**WebLogin**: Stores user credentials and authentication mode
- UserId, UserName, Pwd (for internal auth)
- AuthMode: 'GTI' (LDAP) or 'INTERNAL'
- Active status, Email, Department

### Setup LDAP Configuration

#### 1. Run Migrations
```bash
python manage.py migrate
```

#### 2. Create LDAP Configuration via Django Admin

1. Access Django Admin: `http://your-server:8000/admin/`
2. Navigate to Authentication → LDAP Configurations
3. Add configuration with:
   - ConnectionName: 'GTI' (or your domain name)
   - HostName: Your LDAP server IP
   - Port: 389 (or 636 for LDAPS)
   - BaseDN: e.g., `dc=company,dc=com`
   - UserSearchBase: e.g., `ou=users,dc=company,dc=com`
   - UserSearchFilter: `(uid=%(user)s)` or `(sAMAccountName=%(user)s)` for AD

#### 3. Add Users via Django Admin

1. Navigate to Authentication → Web Logins
2. Add users with:
   - UserId: Username (must match LDAP username for LDAP auth)
   - UserName: Display name
   - AuthMode: 'GTI' for LDAP, 'INTERNAL' for local auth
   - Pwd: Password (only for INTERNAL mode)
   - Active: Checked

#### 4. Quick Setup Command

```bash
python manage.py setup_ldap
```

This creates a default configuration and test users that you can modify.

### Authentication Modes

**LDAP (GTI)**: Authenticates against LDAP server using database configuration
- User DN format: `CN=username,BaseDN`
- Supports SSL/TLS
- Pulls user attributes from LDAP

**INTERNAL**: Authenticates using locally stored credentials
- Password stored in WebLogin table
- Should be hashed in production

### OpenLDAP Setup Example

1. Install OpenLDAP:
```bash
sudo apt-get install slapd ldap-utils
```

2. Configure LDAP server during installation

3. Add users to LDAP directory

4. Configure LDAP Configuration in Django Admin

### Testing LDAP Connection

You can test LDAP connectivity using:

```bash
ldapsearch -x -H ldap://your-server:389 \
  -D "cn=admin,dc=company,dc=com" \
  -W \
  -b "ou=users,dc=company,dc=com" \
  "(uid=username)"
```

For detailed LDAP setup instructions, see `LDAP_SETUP.md`.

## LAN Deployment

### 1. Configure ALLOWED_HOSTS

In `.env` or `settings.py`:

```python
ALLOWED_HOSTS = ['10.40.10.125', 'localhost', '127.0.0.1']
```

Replace `10.40.10.125` with your server's LAN IP.

### 2. Start Redis Server

```bash
redis-server
```

### 3. Start Celery Worker (Optional, for background tasks)

```bash
celery -A chat_system worker -l info
```

### 4. Start the Application

```bash
daphne -b 0.0.0.0 -p 8000 chat_system.asgi:application
```

### 5. Access from Other Computers

Users can access the application at:
```
http://10.40.10.125:8000
```

Replace with your actual LAN IP.

## Building the Desktop App (Electron)

### Prerequisites

- Node.js 16+ installed
- npm or yarn

### Steps

1. Navigate to electron-app directory:
```bash
cd electron-app
```

2. Install dependencies:
```bash
npm install
```

3. Configure server URL in `main.js` or use Settings in the app

4. Build the executable:
```bash
# Build NSIS installer
npm run build-win

# Build portable executable
npm run build-portable
```

5. The executable will be in the `dist` directory

6. Distribute the `.exe` file to users

### Customizing the Desktop App

- **Change Icon**: Replace `electron-app/assets/icon.png` and `icon.ico`
- **Change App Name**: Edit `package.json` `productName` field
- **Change Default URL**: Edit `main.js` `SERVER_URL` constant

## Project Structure

```
chat/
├── chat_system/           # Django project settings
│   ├── settings.py       # Main settings
│   ├── urls.py           # URL routing
│   ├── asgi.py           # ASGI config for Channels
│   └── wsgi.py           # WSGI config
├── authentication/       # LDAP authentication app
│   ├── models.py         # User model
│   ├── views.py          # Auth views
│   └── urls.py           # Auth URLs
├── messaging/           # Messaging app
│   ├── models.py         # Message, Conversation, Group models
│   ├── views.py          # Messaging API views
│   ├── consumers.py      # WebSocket consumers
│   ├── routing.py        # WebSocket routing
│   └── urls.py           # Messaging URLs
├── notifications/        # Notifications app
│   ├── models.py         # Notification model
│   ├── views.py          # Notification views
│   └── urls.py           # Notification URLs
├── templates/           # HTML templates
│   ├── base.html
│   ├── index.html        # Main chat interface
│   └── login.html       # Login page
├── static/              # Static files
│   ├── css/
│   │   └── style.css     # Main stylesheet
│   ├── js/
│   │   └── app.js        # Frontend JavaScript
│   └── sounds/
│       └── notification.mp3
├── media/               # Uploaded media files
├── electron-app/        # Electron desktop app
│   ├── main.js          # Electron main process
│   ├── package.json     # Electron config
│   ├── settings.html    # Settings window
│   ├── about.html       # About window
│   └── assets/          # Icons and images
├── requirements.txt     # Python dependencies
├── run_asgi.py         # ASGI entry point
├── deploy.bat          # Windows deployment script
└── .env.example        # Environment variables template
```

## API Endpoints

### Authentication

- `POST /api/auth/login/` - LDAP login
- `GET /api/auth/profile/` - Get current user profile
- `GET /api/auth/users/` - Get all users
- `POST /api/auth/status/` - Update user status
- `POST /api/auth/logout/` - Logout
- `POST /api/auth/update-profile/` - Update profile

### Messaging

- `GET /api/messaging/conversations/` - Get all conversations
- `GET /api/messaging/conversations/<id>/` - Get conversation details
- `POST /api/messaging/conversations/create/` - Create conversation
- `POST /api/messaging/conversations/<id>/add-participants/` - Add to group
- `POST /api/messaging/conversations/<id>/remove-participant/` - Remove from group
- `POST /api/messaging/upload-media/` - Upload media file
- `GET /api/messaging/search/` - Search users, chats, messages
- `POST /api/messaging/mark-read/` - Mark messages as read
- `GET /api/messaging/online-users/` - Get online users

### Notifications

- `GET /api/notifications/` - Get notifications
- `GET /api/notifications/unread-count/` - Get unread count
- `POST /api/notifications/<id>/mark-read/` - Mark as read
- `POST /api/notifications/mark-all-read/` - Mark all as read
- `DELETE /api/notifications/<id>/delete/` - Delete notification

### WebSocket Endpoints

- `ws://host/ws/chat/<conversation_id>/` - Chat WebSocket
- `ws://host/ws/typing/` - Typing indicator WebSocket
- `ws://host/ws/notifications/` - Notifications WebSocket

## Security Considerations

1. **Change SECRET_KEY**: Generate a secure random key for production
2. **HTTPS**: Use HTTPS in production (configure SSL certificate)
3. **LDAP Security**: Use LDAPS (LDAP over SSL) for secure authentication
4. **File Upload**: File size limits are enforced (50MB max)
5. **CSRF Protection**: CSRF middleware is enabled
6. **CORS**: Configure CORS settings appropriately for your network

## Troubleshooting

### Redis Connection Error

```
Error connecting to Redis
```

**Solution**: Ensure Redis server is running:
```bash
redis-cli ping
```

### LDAP Authentication Failed

```
Invalid credentials
```

**Solution**: 
- Verify LDAP server URL and credentials
- Check LDAP user search base and filter
- Test LDAP connection using ldapsearch

### WebSocket Not Connecting

```
WebSocket connection failed
```

**Solution**:
- Ensure Redis is running
- Check CHANNEL_LAYERS configuration
- Verify ASGI server is running (Daphne/Uvicorn)

### Static Files Not Loading

**Solution**:
```bash
python manage.py collectstatic
```

### Media Upload Failed

**Solution**:
- Check MEDIA_ROOT directory permissions
- Verify file size limits
- Ensure sufficient disk space

## Performance Optimization

1. **Use PostgreSQL**: For better performance with many users
2. **Redis Cluster**: For high availability
3. **Load Balancing**: Use Nginx as reverse proxy
4. **CDN**: Serve static files via CDN
5. **Database Indexing**: Add indexes to frequently queried fields

## Monitoring

### Logs

Logs are stored in the `logs/` directory:
- `django.log` - Django application logs
- `celery.log` - Celery worker logs

### Health Check

Add a health check endpoint:
```python
# urls.py
from django.http import JsonResponse

def health_check(request):
    return JsonResponse({'status': 'healthy'})
```

## Backup

### Database Backup

```bash
# SQLite
cp db.sqlite3 backup/db.sqlite3

# PostgreSQL
pg_dump chatdb > backup/chatdb.sql
```

### Media Backup

```bash
cp -r media backup/media
```

## License

MIT License

## Support

For issues and questions, please contact your system administrator.
