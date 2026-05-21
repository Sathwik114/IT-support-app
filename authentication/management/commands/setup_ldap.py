from django.core.management.base import BaseCommand
from authentication.models import LDAPConfiguration, WebLogin


class Command(BaseCommand):
    help = 'Setup initial LDAP configuration and test users'

    def handle(self, *args, **options):
        self.stdout.write('Setting up LDAP configuration...')
        
        # Create LDAP Configuration
        ldap_config, created = LDAPConfiguration.objects.get_or_create(
            ConnectionName='GTI',
            defaults={
                'HostName': 'ldap.example.com',
                'Port': 389,
                'BaseDN': 'dc=example,dc=com',
                'BindDN': 'cn=admin,dc=example,dc=com',
                'BindPassword': 'password',
                'UserSearchBase': 'ou=users,dc=example,dc=com',
                'UserSearchFilter': '(uid=%(user)s)',
                'UseSSL': False,
                'UseTLS': False,
                'Active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created LDAP configuration: {ldap_config.ConnectionName}'))
        else:
            self.stdout.write(self.style.WARNING(f'LDAP configuration already exists: {ldap_config.ConnectionName}'))
        
        # Create test users
        test_users = [
            {
                'UserId': 'testuser1',
                'UserName': 'Test User One',
                'Pwd': 'password123',
                'AuthMode': 'GTI',
                'Email': 'testuser1@example.com',
                'Department': 'IT',
            },
            {
                'UserId': 'testuser2',
                'UserName': 'Test User Two',
                'Pwd': 'password123',
                'AuthMode': 'INTERNAL',
                'Email': 'testuser2@example.com',
                'Department': 'HR',
            },
        ]
        
        for user_data in test_users:
            user, created = WebLogin.objects.get_or_create(
                UserId=user_data['UserId'],
                defaults=user_data
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created test user: {user.UserName}'))
            else:
                self.stdout.write(self.style.WARNING(f'Test user already exists: {user.UserName}'))
        
        self.stdout.write(self.style.SUCCESS('\nSetup complete!'))
        self.stdout.write('\nNext steps:')
        self.stdout.write('1. Update LDAP configuration in Django Admin: /admin/')
        self.stdout.write('2. Add users to WebLogin table via Admin or database')
        self.stdout.write('3. Test login with the configured users')
