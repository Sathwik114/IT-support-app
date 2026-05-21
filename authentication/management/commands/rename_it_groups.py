from django.core.management.base import BaseCommand
from messaging.models import Group, Conversation


class Command(BaseCommand):
    help = 'Rename IT groups to remove IT prefix'

    def handle(self, *args, **options):
        # Mapping of old names to new names
        name_mapping = {
            'IT Sathya Sathwik Pushpagiri': 'Sathya Sathwik Pushpagiri',
            'IT Parusu Rajesh': 'Rajesh',
        }
        
        for old_name, new_name in name_mapping.items():
            try:
                group = Group.objects.get(name=old_name)
                group.name = new_name
                group.save()
                self.stdout.write(self.style.SUCCESS(f'Renamed "{old_name}" to "{new_name}"'))
            except Group.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'Group "{old_name}" not found'))
        
        self.stdout.write(self.style.SUCCESS('Group renaming completed!'))
