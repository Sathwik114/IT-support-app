from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from messaging.models import Conversation, Group, ConversationParticipant

User = get_user_model()


class Command(BaseCommand):
    help = 'Create default IT team users and group'

    def handle(self, *args, **options):
        # Define IT team members
        it_members = [
            {
                'username': 's20330',
                'password': 'gtiit@s20330',
                'first_name': 'Sathya',
                'last_name': 'Sathwik',
                'display_name': 'IT Sathya Sathwik'
            },
            {
                'username': '250479',
                'password': 'gtiit@250479',
                'first_name': 'Rajesh',
                'last_name': '',
                'display_name': 'IT Rajesh'
            },
            {
                'username': '230022',
                'password': 'gtiit@230022',
                'first_name': 'Shakeer',
                'last_name': '',
                'display_name': 'IT Shakeer'
            },
            {
                'username': '140287',
                'password': 'gtiit@140287',
                'first_name': 'Narasimha',
                'last_name': '',
                'display_name': 'IT Narasimha'
            },
            {
                'username': '111075',
                'password': 'gtiit@11075',
                'first_name': 'Masthan',
                'last_name': '',
                'display_name': 'IT Masthan'
            },
        ]

        # Create users
        created_users = []
        for member in it_members:
            user, created = User.objects.get_or_create(
                username=member['username'],
                defaults={
                    'first_name': member['first_name'],
                    'last_name': member['last_name'],
                }
            )
            
            if created:
                user.set_password(member['password'])
                user.save()
                self.stdout.write(f'Created user: {member["display_name"]} ({member["username"]})')
            else:
                # Update password if user exists
                user.set_password(member['password'])
                user.save()
                self.stdout.write(f'Updated password for: {member["display_name"]} ({member["username"]})')
            
            created_users.append(user)

        # Create or get IT group conversation (main group with all members)
        it_group_conversation, created = Conversation.objects.get_or_create(
            conversation_type='group'
        )

        if created:
            # Create group details
            it_group = Group.objects.create(
                conversation=it_group_conversation,
                name='IT',
                description='Official IT Department Group',
                created_by=created_users[0]
            )
            it_group.admins.add(created_users[0])
            self.stdout.write('Created IT group')
        else:
            it_group = it_group_conversation.group
            self.stdout.write('IT group already exists')

        # Add all IT members to the main IT group
        for user in created_users:
            it_group_conversation.participants.add(user)
            self.stdout.write(f'Added {user.username} to IT group')

        # Create individual group chats for each IT member
        # Map usernames to display names
        display_name_map = {
            's20330': 'Sathya Sathwik Pushpagiri',
            '250479': 'Rajesh',
            '230022': 'Shakeer',
            '140287': 'Narasimha',
            '111075': 'Masthan',
        }
        
        for user in created_users:
            display_name = display_name_map.get(user.username, user.get_full_name() or user.username)
            
            # Create individual group conversation (unique per user)
            individual_conv, created = Conversation.objects.get_or_create(
                conversation_type='group',
                group__name=display_name
            )
            
            if created:
                # Create group details
                individual_group = Group.objects.create(
                    conversation=individual_conv,
                    name=display_name,
                    description=f'Individual chat for {display_name}',
                    created_by=user
                )
                individual_group.admins.add(user)
                self.stdout.write(f'Created individual group: {display_name}')
            else:
                individual_group = individual_conv.group
                self.stdout.write(f'Individual group already exists: {display_name}')
            
            # Add the IT member to their own group
            individual_conv.participants.add(user)
            self.stdout.write(f'Added {user.username} to their individual group')

        self.stdout.write(self.style.SUCCESS('IT team setup completed successfully!'))
