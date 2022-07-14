from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class Classes(models.Model):
    name = models.CharField("班级名称", max_length=13)


class User(AbstractBaseUser):
    # Django枚举类
    class UserRole(models.TextChoices):
        TEACHER = 'TEC', _('老师')
        STUDENT = 'STU', _('学生')

    class UserAdmin(models.TextChoices):
        REGULAR_USER = 'RU', _("普通用户")
        ADMIN = 'AM', _("管理员")
        SUPER_ADMIN = 'SA', _("超级管理员")

    username = models.CharField("用户名", max_length=10)
    email = models.CharField("邮箱", max_length=30)
    first_name = models.CharField("名字", max_length=3)
    last_name = models.CharField("姓", max_length=2)
    user_id = models.CharField("工号/学号", max_length=13, unique=True)
    is_active = models.BooleanField("是否启用", default=True)
    user_role = models.CharField("用户角色", max_length=2, choices=UserRole.choices)
    user_admin = models.CharField("用户管理角色", max_length=2, choices=UserAdmin.choices)
    classes = models.ForeignKey(Classes, on_delete=models.CASCADE)
    solved_problems = models.JSONField("解决的问题", default=dict)
    avatar = models.TextField(default=f"{settings.AVATAR_URI_PREFIX}/default.png")

    commit_num = models.IntegerField("提交次数", default=0)
    accept_num = models.IntegerField("通过的提交", default=0)
    solved_num = models.IntegerField("已解决题数", default=0)

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'user_id'
    REQUIRED_FIELDS = []

    def get_full_name(self):
        return self.last_name + self.first_name

    def get_short_name(self):
        return self.first_name

    class Meta:
        db_table = "user"
