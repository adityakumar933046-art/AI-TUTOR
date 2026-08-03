from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import StudentProfile, ParentProfile, TeacherProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Seed demo accounts for Student, Parent, Teacher, and Admin'

    def handle(self, *args, **options):
        # 1. Student Demo Account
        student, created = User.objects.get_or_create(
            email='student@eduverse.ai',
            defaults={
                'username': 'student_alex',
                'first_name': 'Alex',
                'last_name': 'Johnson',
                'role': 'Student',
                'email_verified': True
            }
        )
        if created:
            student.set_password('student123')
            student.save()
            StudentProfile.objects.get_or_create(user=student)
            self.stdout.write(self.style.SUCCESS('Created Demo Student: student@eduverse.ai / student123'))

        # 2. Parent Demo Account
        parent, created = User.objects.get_or_create(
            email='parent@eduverse.ai',
            defaults={
                'username': 'parent_sarah',
                'first_name': 'Sarah',
                'last_name': 'Johnson',
                'role': 'Parent',
                'email_verified': True
            }
        )
        if created:
            parent.set_password('parent123')
            parent.save()
            ParentProfile.objects.get_or_create(user=parent)
            self.stdout.write(self.style.SUCCESS('Created Demo Parent: parent@eduverse.ai / parent123'))

        # 3. Teacher Demo Account
        teacher, created = User.objects.get_or_create(
            email='teacher@eduverse.ai',
            defaults={
                'username': 'teacher_davis',
                'first_name': 'Davis',
                'last_name': 'Prof',
                'role': 'Teacher',
                'email_verified': True
            }
        )
        if created:
            teacher.set_password('teacher123')
            teacher.save()
            TeacherProfile.objects.get_or_create(user=teacher)
            self.stdout.write(self.style.SUCCESS('Created Demo Teacher: teacher@eduverse.ai / teacher123'))

        # 4. Admin Demo Account
        admin_user, created = User.objects.get_or_create(
            email='admin@eduverse.ai',
            defaults={
                'username': 'admin_super',
                'first_name': 'Super',
                'last_name': 'Admin',
                'role': 'Admin',
                'is_staff': True,
                'is_superuser': True,
                'email_verified': True
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.save()
            self.stdout.write(self.style.SUCCESS('Created Demo Admin: admin@eduverse.ai / admin123'))

        self.stdout.write(self.style.SUCCESS('Database seeding complete!'))
