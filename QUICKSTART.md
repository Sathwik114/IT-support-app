# Quick Start Guide - LAN Chat System

This guide will help you get the LAN Chat System up and running quickly.

## Prerequisites Check

Before starting, ensure you have:
- [ ] Python 3.9+ installed
- [ ] Redis Server installed and running
- [ ] LDAP Server accessible (for authentication)
- [ ] LAN IP address of the server

## Step 1: Setup (5 minutes)

```bash
# Navigate to project directory
cd chat

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 2: Configuration (2 minutes)

```bash
# Copy environment template
copy .env.example .env  # Windows
# or
cp .env.example .env    # Linux/Mac
```

Edit `.env` file with your settings:

```env
DEBUG=True
ALLOWED_HOSTS=10.40.10.125,localhost,127.0.0.1

# Update with your LDAP server details
LDAP_AUTH_URL=ldap://your-ldap-server:389
LDAP_BASE_DN=dc=company,dc=com
LDAP_BIND_DN=cn=admin,dc=company,dc=com
LDAP_BIND_PASSWORD=your-password
LDAP_USER_SEARCH_BASE=ou=users,dc=company,dc=com
```

**Important**: Replace `10.40.10.125` with your actual LAN IP address.

## Step 3: Database Setup (1 minute)

```bash
# Run migrations
python manage.py migrate

# Collect static files
python manage.py collectstatic
```

## Step 4: Start Redis

```bash
# Windows (if using Redis for Windows)
redis-server

# Linux
sudo systemctl start redis-server

# Or run in foreground
redis-server
```

Verify Redis is running:
```bash
redis-cli ping
# Should return: PONG
```

## Step 5: Start the Application

### Option A: Using Daphne (Recommended)

```bash
daphne -b 0.0.0.0 -p 8000 chat_system.asgi:application
```

### Option B: Using Uvicorn

```bash
python run_asgi.py
```

### Option C: Using Deployment Script (Windows)

```bash
deploy.bat
```

## Step 6: Access the Application

Open your browser and navigate to:
```
http://10.40.10.125:8000
```

Replace `10.40.10.125` with your LAN IP.

## Step 7: Login

1. Enter your LDAP username and password
2. Click Login
3. You're now in the chat system!

## Building the Desktop App (Optional)

If you want to distribute as a Windows executable:

```bash
cd electron-app
npm install
npm run build-win
```

The executable will be in `electron-app/dist/`.

## Common Issues

### "Redis connection failed"
- Make sure Redis server is running
- Check Redis is accessible on localhost:6379

### "LDAP authentication failed"
- Verify LDAP server URL is correct
- Check LDAP credentials in .env
- Ensure user exists in LDAP directory

### "Static files not loading"
- Run: `python manage.py collectstatic`
- Check STATIC_ROOT directory permissions

### "WebSocket not connecting"
- Ensure Redis is running
- Make sure you're using Daphne or Uvicorn (not runserver)
- Check firewall settings

## Next Steps

- Add users to LDAP directory
- Create groups for team communication
- Build and distribute the desktop app
- Configure HTTPS for production (optional)

## Support

For detailed documentation, see `README.md`.
