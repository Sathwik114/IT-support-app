from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from django.conf import settings


class LDAPConfiguration(models.Model):
    """Store LDAP configuration for different domains."""
    
    ConnectionName = models.CharField(max_length=100, unique=True)
    HostName = models.CharField(max_length=255)
    Port = models.IntegerField(default=389)
    BaseDN = models.CharField(max_length=255)
    BindDN = models.CharField(max_length=255, blank=True)
    BindPassword = models.CharField(max_length=255, blank=True)
    UserSearchBase = models.CharField(max_length=255, blank=True)
    UserSearchFilter = models.CharField(max_length=255, default='(uid=%(user)s)')
    UseSSL = models.BooleanField(default=False)
    UseTLS = models.BooleanField(default=False)
    Active = models.BooleanField(default=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'LDAP Configuration'
        verbose_name_plural = 'LDAP Configurations'
    
    def __str__(self):
        return self.ConnectionName


class WebLogin(models.Model):
    """Store user credentials and authentication mode."""
    
    AUTH_MODE_CHOICES = [
        ('GTI', 'LDAP (GTI)'),
        ('INTERNAL', 'Internal'),
    ]
    
    UserId = models.CharField(max_length=150, unique=True)
    UserName = models.CharField(max_length=255)
    Pwd = models.CharField(max_length=255)  # Should be hashed in production
    AuthMode = models.CharField(max_length=20, choices=AUTH_MODE_CHOICES, default='GTI')
    Active = models.BooleanField(default=True)
    Email = models.EmailField(blank=True)
    Department = models.CharField(max_length=100, blank=True)
    CreatedAt = models.DateTimeField(auto_now_add=True)
    UpdatedAt = models.DateTimeField(auto_now=True)
    LastLogin = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        verbose_name = 'Web Login'
        verbose_name_plural = 'Web Logins'
    
    def __str__(self):
        return f"{self.UserName} ({self.UserId})"


class User(AbstractUser):
    """Custom User model for LDAP authentication."""
    
    STATUS_CHOICES = [
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('away', 'Away'),
        ('busy', 'Busy'),
    ]
    
    username = models.CharField(max_length=150, unique=True)
    email = models.EmailField(blank=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    status_message = models.CharField(max_length=100, blank=True)
    last_seen = models.DateTimeField(auto_now=True)
    is_ldap_user = models.BooleanField(default=True)
    phone_number = models.CharField(max_length=20, blank=True)
    department = models.CharField(max_length=100, blank=True)
    section = models.CharField(max_length=100, blank=True)
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return self.username
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username
    
    @classmethod
    def authenticate_user(cls, username, password):
        """Authenticate user using LDAP or Internal authentication based on configuration."""
        from .models import WebLogin, LDAPConfiguration
        
        try:
            # Get user from WebLogin table
            web_login = WebLogin.objects.filter(
                UserId=username,
                Active=True
            ).first()
            
            # If user not in WebLogin, try LDAP authentication and auto-create
            if not web_login:
                # Try to find GTI LDAP configuration
                ldap_config = LDAPConfiguration.objects.filter(
                    ConnectionName='GTI',
                    Active=True
                ).first()
                
                if ldap_config:
                    # Try LDAP authentication
                    ldap_result = cls.authenticate_ldap(
                        username, 
                        password, 
                        ldap_config
                    )
                    
                    if ldap_result:
                        # Auto-create WebLogin entry
                        WebLogin.objects.create(
                            UserId=username,
                            UserName=ldap_result.get_full_name() or username,
                            Pwd='',  # Not used for LDAP
                            AuthMode='GTI',
                            Active=True,
                            Email=ldap_result.email,
                            Department=ldap_result.department,
                        )
                        return ldap_result, "LDAP login successful (auto-created user)"
                    else:
                        return None, "LDAP authentication failed"
                else:
                    return None, "User not found and LDAP not configured"
            
            # Check authentication mode
            if web_login.AuthMode == 'INTERNAL':
                # Internal authentication
                if web_login.Pwd == password:
                    # Get or create Django user
                    user, created = cls.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': web_login.Email,
                            'first_name': web_login.UserName.split()[0] if web_login.UserName else '',
                            'last_name': ' '.join(web_login.UserName.split()[1:]) if web_login.UserName and len(web_login.UserName.split()) > 1 else '',
                            'department': web_login.Department,
                            'is_ldap_user': False,
                        }
                    )
                    # Update last login
                    web_login.LastLogin = timezone.now()
                    web_login.save()
                    return user, "Internal login successful"
                else:
                    return None, "Incorrect password"
            
            elif web_login.AuthMode == 'GTI':
                # LDAP authentication
                ldap_config = LDAPConfiguration.objects.filter(
                    ConnectionName=web_login.AuthMode,
                    Active=True
                ).first()
                
                if not ldap_config:
                    return None, "LDAP domain not configured"
                
                # Authenticate against LDAP
                ldap_result = cls.authenticate_ldap(
                    username, 
                    password, 
                    ldap_config
                )
                
                if ldap_result:
                    # Update last login
                    web_login.LastLogin = timezone.now()
                    web_login.save()
                    return ldap_result, "LDAP login successful"
                else:
                    return None, "LDAP authentication failed"
            
            return None, "Invalid authentication mode"
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return None, str(e)
    
    @classmethod
    def authenticate_ldap(cls, username, password, ldap_config):
        """Authenticate user against LDAP using database configuration."""
        if not LDAP_AVAILABLE:
            print("Error: python-ldap not installed. Cannot perform LDAP authentication.")
            return None
        
        try:
            # Build LDAP URL
            protocol = 'ldaps' if ldap_config.UseSSL else 'ldap'
            ldap_url = f"{protocol}://{ldap_config.HostName}:{ldap_config.Port}"
            
            # Connect to LDAP server
            conn = ldap.initialize(ldap_url)
            conn.protocol_version = ldap.VERSION3
            conn.set_option(ldap.OPT_REFERRALS, 0)
            
            if ldap_config.UseTLS:
                conn.start_tls_s()
            
            # Build user DN - similar to Next.js: CN=username,BaseDN
            user_dn = f"CN={username},{ldap_config.BaseDN}"
            
            # Bind with user credentials
            conn.simple_bind_s(user_dn, password)
            
            # Search for user attributes
            search_base = ldap_config.UserSearchBase or ldap_config.BaseDN
            search_filter = ldap_config.UserSearchFilter % {'user': username}
            
            result = conn.search_s(
                search_base,
                ldap.SCOPE_SUBTREE,
                search_filter,
                ['cn', 'mail', 'givenName', 'sn', 'telephoneNumber', 'department']
            )
            
            if result:
                user_data = result[0][1]
                # Get or create user in Django DB
                user, created = cls.objects.get_or_create(
                    username=username,
                    defaults={
                        'email': user_data.get('mail', [b''])[0].decode('utf-8') if user_data.get('mail') else '',
                        'first_name': user_data.get('givenName', [b''])[0].decode('utf-8') if user_data.get('givenName') else '',
                        'last_name': user_data.get('sn', [b''])[0].decode('utf-8') if user_data.get('sn') else '',
                        'phone_number': user_data.get('telephoneNumber', [b''])[0].decode('utf-8') if user_data.get('telephoneNumber') else '',
                        'department': user_data.get('department', [b''])[0].decode('utf-8') if user_data.get('department') else '',
                        'is_ldap_user': True,
                    }
                )
                conn.unbind()
                return user
            
            conn.unbind()
            return None
            
        except ldap.INVALID_CREDENTIALS:
            return None
        except ldap.LDAPError as e:
            print(f"LDAP Error: {e}")
            return None
    
    @classmethod
    def get_all_ldap_users(cls):
        """Get all users from LDAP directory."""
        try:
            conn = ldap.initialize(settings.LDAP_AUTH_URL)
            conn.protocol_version = ldap.VERSION3
            conn.simple_bind_s(settings.LDAP_BIND_DN, settings.LDAP_BIND_PASSWORD)
            
            result = conn.search_s(
                settings.LDAP_USER_SEARCH_BASE,
                ldap.SCOPE_ONELEVEL,
                '(objectClass=person)',
                ['uid', 'cn', 'mail', 'givenName', 'sn']
            )
            
            users = []
            for dn, attrs in result:
                user_info = {
                    'username': attrs.get('uid', [b''])[0].decode('utf-8'),
                    'full_name': attrs.get('cn', [b''])[0].decode('utf-8'),
                    'email': attrs.get('mail', [b''])[0].decode('utf-8') if attrs.get('mail') else '',
                }
                users.append(user_info)
            
            conn.unbind()
            return users
            
        except ldap.LDAPError as e:
            print(f"LDAP Error: {e}")
            return []
