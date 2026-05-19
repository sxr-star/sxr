from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates a superuser non-interactively'

    def handle(self, *args, **options):
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser(
                username='admin',
                email='',
                password='admin123'
            )
            self.stdout.write(self.style.SUCCESS('管理员账号已创建: admin / admin123'))
        else:
            self.stdout.write('管理员账号已存在')
