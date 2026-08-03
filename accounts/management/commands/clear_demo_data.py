from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Purge all pre-seeded demo accounts to leave a clean production environment'

    def handle(self, *args, **options):
        demo_emails = [
            'student@eduverse.ai',
            'parent@eduverse.ai',
            'teacher@eduverse.ai',
            'admin@eduverse.ai',
            'google_user@eduverse.ai'
        ]
        
        deleted_count, _ = User.objects.filter(email__in=demo_emails).delete()
        self.stdout.write(self.style.SUCCESS(f'Successfully purged {deleted_count} demo account records. Database is clean for real user registration!'))
