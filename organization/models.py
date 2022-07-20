from django.db import models
from django.contrib.auth.models import AbstractUser, Group
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Classes(models.Model):
    name = models.CharField(unique=True, max_length=25, default="非本系")

    class Meta:
        verbose_name = "class"
        verbose_name_plural = "classes"
        db_table = "classes"

    def __str__(self):
        return self.name


class User(AbstractUser):
    # Django枚举类
    class UserRole(models.TextChoices):
        TEACHER = 'TEC', _('老师')
        STUDENT = 'STU', _('学生')

    class UserAdmin(models.TextChoices):
        REGULAR_USER = 'RU', _("普通用户")
        ADMIN = 'AM', _("管理员")
        SUPER_ADMIN = 'SA', _("超级管理员")

    user_id = models.CharField("工号/学号", max_length=13, unique=True)
    user_role = models.CharField("用户角色", max_length=3, choices=UserRole.choices)
    user_admin = models.CharField("用户管理角色", max_length=2, choices=UserAdmin.choices)
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE, null=True, related_name="users")
    solved_problems = models.JSONField("解决的问题", default=dict)
    avatar = models.TextField(default=f"{settings.AVATAR_URI_PREFIX}/default.png")

    commit_num = models.IntegerField("提交次数", default=0)
    accept_num = models.IntegerField("通过的提交", default=0)
    solved_num = models.IntegerField("已解决题数", default=0)

    def add_cnum(self):
        self.commit_num += 1

    def add_anum(self):
        self.accept_num += 1

    def add_snum(self):
        self.solved_num += 1

    def __str__(self):
        return self.get_full_name()

    class Meta:
        db_table = "user"
