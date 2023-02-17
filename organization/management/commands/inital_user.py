from django.core.management.base import BaseCommand

from organization.models import Group, User, UserProfile


class Command(BaseCommand):
    help = "初始化一个超级管理员"

    def handle(self, *args, **options):
        admin = User.objects.create_superuser(username="10010110", real_name="root admin",
                                              password="admin", email="admin@moorlands.cn")
        admin_group = Group.objects.create(name="管理组")
        UserProfile.objects.create(user=admin, group=admin_group)
