# LDAP Configuration Setup Guide

This guide explains how to configure LDAP authentication using the database-driven approach (similar to the Next.js implementation).

## Overview

The system now supports two authentication modes:
- **LDAP (GTI)**: Authenticates against LDAP server using database-stored configuration
- **INTERNAL**: Authenticates using locally stored credentials

## Database Models

### LDAPConfiguration
Stores LDAP server configuration for different domains:

- `ConnectionName`: Unique identifier for the LDAP domain (e.g., 'GTI')
- `HostName`: LDAP server hostname or IP
- `Port`: LDAP server port (default: 389)
- `BaseDN`: Base Distinguished Name for the domain
- `BindDN`: DN for binding to LDAP (for admin operations)
- `BindPassword`: Password for binding
- `UserSearchBase`: Base for user searches
- `UserSearchFilter`: LDAP filter for finding users (default: `(uid=%(user)s)`)
- `UseSSL`: Use LDAPS (LDAP over SSL)
- `UseTLS`: Use STARTTLS
- `Active`: Whether this configuration is active

### WebLogin
Stores user credentials and authentication mode:

- `UserId`: Unique user identifier (username)
- `UserName`: Display name
- `Pwd`: Password (for INTERNAL mode) - **Note: Should be hashed in production**
- `AuthMode`: 'GTI' for LDAP, 'INTERNAL' for local auth
- `Active`: Whether user account is active
- `Email`: User email
- `Department`: User department
- `LastLogin`: Timestamp of last login

## Setup Steps

### 1. Run Migrations

```bash
python manage.py migrate
```

This will create the new tables: `authentication_ldapconfiguration` and `authentication_weblogin`.

### 2. Create LDAP Configuration

#### Option A: Using Django Admin

1. Access Django Admin: `http://your-server:8000/admin/`
2. Navigate to "Authentication" → "LDAP Configurations"
3. Click "Add LDAP Configuration"
4. Fill in the fields:
   - **ConnectionName**: GTI (or your domain name)
   - **HostName**: Your LDAP server IP (e.g., `10.40.10.100`)
   - **Port**: 389 (or 636 for LDAPS)
   - **BaseDN**: e.g., `dc=company,dc=com`
   - **BindDN**: e.g., `cn=admin,dc=company,dc=com`
   - **BindPassword**: Your LDAP admin password
   - **UserSearchBase**: e.g., `ou=users,dc=company,dc=com`
   - **UserSearchFilter**: `(uid=%(user)s)` or `(sAMAccountName=%(user)s)` for AD
   - **UseSSL**: True if using LDAPS
   - **UseTLS**: True if using STARTTLS
   - **Active**: Checked

#### Option B: Using Management Command

```bash
python manage.py setup_ldap
```

This creates a default configuration that you can then modify in the admin.

#### Option C: Using Django Shell

```python
from authentication.models import LDAPConfiguration

LDAPConfiguration.objects.create(
    ConnectionName='GTI',
    HostName='ldap.example.com',
    Port=389,
    BaseDN='dc=company,dc=com',
    BindDN='cn=admin,dc=company,dc=com',
    BindPassword='your-password',
    UserSearchBase='ou=users,dc=company,dc=com',
    UserSearchFilter='(uid=%(user)s)',
    UseSSL=False,
    UseTLS=False,
    Active=True
)
```

### 3. Add Users to WebLogin Table

#### Option A: Using Django Admin

1. Navigate to "Authentication" → "Web Logins"
2. Click "Add Web Login"
3. Fill in the fields:
   - **UserId**: The username (must match LDAP username for LDAP auth)
   - **UserName**: Display name
   - **Pwd**: Password (only for INTERNAL mode)
   - **AuthMode**: 'GTI' for LDAP, 'INTERNAL' for local
   - **Active**: Checked
   - **Email**: User email
   - **Department**: User department

#### Option B: Using Django Shell

```python
from authentication.models import WebLogin

# LDAP user
WebLogin.objects.create(
    UserId='john.doe',
    UserName='John Doe',
    Pwd='',  # Not used for LDAP
    AuthMode='GTI',
    Active=True,
    Email='john.doe@company.com',
    Department='IT'
)

# Internal user
WebLogin.objects.create(
    UserId='jane.smith',
    UserName='Jane Smith',
    Pwd='password123',  # Should be hashed in production
    AuthMode='INTERNAL',
    Active=True,
    Email='jane.smith@company.com',
    Department='HR'
)
```

### 4. Test Authentication

#### Test LDAP Authentication

```bash
curl -X POST http://your-server:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "john.doe", "password": "ldap-password"}'
```

#### Test Internal Authentication

```bash
curl -X POST http://your-server:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "jane.smith", "password": "password123"}'
```

## LDAP DN Format

The system uses the format: `CN=username,BaseDN` (similar to the Next.js implementation).

Examples:
- User: `john.doe` with BaseDN `dc=company,dc=com` → `CN=john.doe,dc=company,dc=com`
- User: `jsmith` with BaseDN `ou=users,dc=company,dc=com` → `CN=jsmith,ou=users,dc=company,dc=com`

If your LDAP uses a different format (e.g., `uid=username` instead of `CN=username`), modify the `authenticate_ldap` method in `authentication/models.py`:

```python
# Change this line:
user_dn = f"CN={username},{ldap_config.BaseDN}"

# To this (for uid format):
user_dn = f"uid={username},{ldap_config.BaseDN}"
```

## Active Directory Configuration

For Active Directory, use these settings:

- **HostName**: Your AD server IP
- **Port**: 389 (or 636 for LDAPS)
- **BaseDN**: e.g., `dc=corp,dc=company,dc=com`
- **UserSearchBase**: e.g., `ou=users,dc=corp,dc=company,dc=com`
- **UserSearchFilter**: `(sAMAccountName=%(user)s)`  ← Important for AD
- **UseSSL**: True for production
- **UseTLS**: False if using SSL, True for STARTTLS

## OpenLDAP Configuration

For OpenLDAP:

- **HostName**: Your OpenLDAP server IP
- **Port**: 389
- **BaseDN**: e.g., `dc=example,dc=com`
- **UserSearchBase**: e.g., `ou=people,dc=example,dc=com`
- **UserSearchFilter**: `(uid=%(user)s)`
- **UseSSL**: True for production
- **UseTLS**: False if using SSL

## Security Notes

⚠️ **Important Security Considerations:**

1. **Password Hashing**: The `Pwd` field in `WebLogin` is currently stored in plain text. In production, you should hash passwords using Django's `make_password()`:

```python
from django.contrib.auth.hashers import make_password

WebLogin.objects.create(
    UserId='user',
    UserName='User Name',
    Pwd=make_password('password123'),  # Hash the password
    AuthMode='INTERNAL',
    Active=True
)
```

2. **LDAP Credentials**: Store LDAP bind credentials securely. Consider using environment variables or Django's encrypted fields.

3. **SSL/TLS**: Always use SSL/TLS in production for LDAP connections.

4. **Environment Variables**: For sensitive data like LDAP passwords, consider using Django-environ:

```python
# In models.py
import os
from django.conf import settings

class LDAPConfiguration(models.Model):
    # ... other fields ...
    BindPassword = models.CharField(max_length=255, blank=True)
    
    def get_bind_password(self):
        # Override to use environment variable
        return os.environ.get(f'LDAP_PASSWORD_{self.ConnectionName}', self.BindPassword)
```

## Troubleshooting

### "LDAP domain not configured"
- Ensure an active `LDAPConfiguration` exists with `ConnectionName` matching the user's `AuthMode`
- Check the `Active` field is checked

### "LDAP authentication failed"
- Verify LDAP server is accessible from the Django server
- Check the HostName and Port are correct
- Verify the BaseDN and UserSearchBase are correct
- Test LDAP connection using `ldapsearch` command
- Check if the user exists in LDAP directory

### "User not found or inactive"
- Ensure the user exists in `WebLogin` table
- Check the `Active` field is checked
- Verify the `UserId` matches the login username

### "Invalid credentials"
- For LDAP: Verify the password is correct in LDAP
- For INTERNAL: Verify the password matches the `Pwd` field in `WebLogin`

## Migration from Environment Variables

If you were previously using environment variables for LDAP configuration:

1. Run migrations to create the new tables
2. Create an `LDAPConfiguration` entry with your environment variable values
3. Create `WebLogin` entries for your users
4. The system will now use the database configuration instead of environment variables

## Testing LDAP Connection

You can test LDAP connectivity using the `ldapsearch` command:

```bash
ldapsearch -x -H ldap://your-server:389 \
  -D "cn=admin,dc=company,dc=com" \
  -W \
  -b "ou=users,dc=company,dc=com" \
  "(uid=username)"
```

## Support

For issues or questions:
1. Check Django logs for detailed error messages
2. Verify LDAP server logs
3. Test with `ldapsearch` command-line tool
4. Check the authentication models in `authentication/models.py`
