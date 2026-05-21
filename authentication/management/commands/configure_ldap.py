from django.core.management.base import BaseCommand
from authentication.models import LDAPConfiguration, WebLogin


class Command(BaseCommand):
    help = 'Configure LDAP settings interactively'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=== LDAP Configuration Setup ===\n'))
        
        # Get LDAP configuration details
        connection_name = input('Connection Name (e.g., GTI): ').strip() or 'GTI'
        hostname = input('LDAP Hostname/IP: ').strip()
        port = input('LDAP Port (default 389): ').strip() or '389'
        base_dn = input('Base DN (e.g., dc=company,dc=com): ').strip()
        user_search_base = input('User Search Base (e.g., ou=users,dc=company,dc=com): ').strip() or base_dn
        use_ssl = input('Use SSL/LDAPS? (y/n, default n): ').strip().lower() == 'y'
        
        # Optional bind credentials
        self.stdout.write('\n--- Optional: Bind DN for admin operations ---')
        bind_dn = input('Bind DN (leave empty if not needed): ').strip()
        bind_password = input('Bind Password (leave empty if not needed): ').strip()
        
        # Create or update LDAP configuration
        ldap_config, created = LDAPConfiguration.objects.update_or_create(
            ConnectionName=connection_name,
            defaults={
                'HostName': hostname,
                'Port': int(port),
                'BaseDN': base_dn,
                'BindDN': bind_dn,
                'BindPassword': bind_password,
                'UserSearchBase': user_search_base,
                'UserSearchFilter': '(uid=%(user)s)',
                'UseSSL': use_ssl,
                'UseTLS': False,
                'Active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Created LDAP configuration: {connection_name}'))
        else:
            self.stdout.write(self.style.SUCCESS(f'\n✓ Updated LDAP configuration: {connection_name}'))
        
        # Ask if they want to add a test user
        self.stdout.write('\n--- Add Test User ---')
        add_user = input('Add a test user for LDAP authentication? (y/n): ').strip().lower()
        
        if add_user == 'y':
            user_id = input('User ID (username): ').strip()
            user_name = input('Display Name: ').strip()
            email = input('Email (optional): ').strip()
            department = input('Department (optional): ').strip()
            
            web_login, created = WebLogin.objects.update_or_create(
                UserId=user_id,
                defaults={
                    'UserName': user_name,
                    'Pwd': '',  # Not used for LDAP
                    'AuthMode': 'GTI',
                    'Active': True,
                    'Email': email,
                    'Department': department,
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Added LDAP user: {user_name} ({user_id})'))
            else:
                self.stdout.write(self.style.SUCCESS(f'✓ Updated LDAP user: {user_name} ({user_id})'))
        
        self.stdout.write(self.style.SUCCESS('\n=== Setup Complete ==='))
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Test login with your LDAP credentials')
        self.stdout.write('2. Access Django Admin to add more users: /admin/')
        self.stdout.write('3. Start the application: python manage.py runserver')
