from django.core.management.base import BaseCommand
from authentication.models import LDAPConfiguration, WebLogin


class Command(BaseCommand):
    help = 'Setup GTI LDAP configuration with specific settings'

    def handle(self, *args, **options):
        self.stdout.write('Setting up GTI LDAP configuration...\n')
        
        # Create LDAP configuration for GTI
        ldap_config, created = LDAPConfiguration.objects.update_or_create(
            ConnectionName='GTI',
            defaults={
                'HostName': '10.40.10.204',
                'Port': 389,
                'BaseDN': 'ou=GTI,DC=gti,DC=com',
                'BindDN': '',
                'BindPassword': '',
                'UserSearchBase': 'ou=GTI,DC=gti,DC=com',
                'UserSearchFilter': '(uid=%(user)s)',
                'UseSSL': False,
                'UseTLS': False,
                'Active': True,
            }
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS('✓ Created GTI LDAP configuration'))
        else:
            self.stdout.write(self.style.SUCCESS('✓ Updated GTI LDAP configuration'))
        
        self.stdout.write('\nConfiguration details:')
        self.stdout.write(f'  Connection Name: GTI')
        self.stdout.write(f'  Host: 10.40.10.204')
        self.stdout.write(f'  Port: 389')
        self.stdout.write(f'  Base DN: ou=GTI,DC=gti,DC=com')
        self.stdout.write(f'  User Search Base: ou=GTI,DC=gti,DC=com')
        
        self.stdout.write('\n' + '='*50)
        self.stdout.write('\nTo add LDAP users, use Django Admin or run:')
        self.stdout.write('python manage.py configure_ldap')
        self.stdout.write('\nOr add users directly in Django Admin at:')
        self.stdout.write('http://localhost:8000/admin/')
        self.stdout.write('\nAuthentication → Web Logins → Add Web Login')
        self.stdout.write('  - UserId: LDAP username')
        self.stdout.write('  - UserName: Display name')
        self.stdout.write('  - AuthMode: GTI')
        self.stdout.write('  - Active: Checked')
