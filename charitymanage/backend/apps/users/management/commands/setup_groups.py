from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group

class Command(BaseCommand):
    help = 'Create default user groups'

    def handle(self, *args, **kwargs):
        Group.objects.get_or_create(name='Dashboard Viewers')
        Group.objects.get_or_create(name='Booth Managers')
        self.stdout.write(self.style.SUCCESS('Successfully created default groups.'))
