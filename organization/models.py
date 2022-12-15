from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.contrib.auth.hashers import make_password
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    def _create_user(self, username, email, password, **extra_fields):
        if not username:
            raise ValueError('The given username must be set')
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.password = make_password(password)
        user.save()
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        if extra_fields.get('user_role', None) == 'TEC':
            extra_fields.setdefault('is_staff', True)
            extra_fields.setdefault('user_permission', 'SELF')
        else:
            extra_fields.setdefault('user_role', 'STU')
            extra_fields.setdefault('is_staff', False)
            extra_fields.setdefault('user_permission', 'NONE')
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        extra_fields.setdefault('user_role', 'TEC')
        extra_fields.setdefault('user_permission', 'ALL')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self._create_user(username, email, password, **extra_fields)


class Group(models.Model):
    name = models.CharField(unique=True, max_length=25)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "group"
        verbose_name_plural = "groups"
        db_table = "group"
        ordering = ['id']


class User(AbstractBaseUser):
    username_validator = UnicodeUsernameValidator()

    # Django枚举类
    class UserRole(models.TextChoices):
        TEACHER = 'TEC', _('Teacher')
        STUDENT = 'STU', _('Student')

    class Permission(models.TextChoices):
        NONE = 'NONE', _("No permission")
        SELF = 'SELF', _("Self permission")
        ALL = 'ALL', _("All permission")

    username = models.CharField(
        _('User ID'),
        max_length=13,
        unique=True,
        primary_key=True,
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    nickname = models.CharField(_('nickname'), max_length=25)
    is_staff = models.BooleanField(_('staff status'), default=False, )
    is_active = models.BooleanField(_('active'), default=True, )
    is_superuser = models.BooleanField(_('superuser status'), default=False)
    first_name = models.CharField(_('first name'), max_length=10)
    last_name = models.CharField(_('last name'), max_length=5)
    email = models.EmailField(_('email address'))
    user_role = models.CharField("user role", max_length=3, choices=UserRole.choices)
    user_permission = models.CharField("user permission", max_length=4, choices=Permission.choices)
    date_joined = models.DateTimeField(_('date joined'), auto_now_add=True)

    objects = CustomUserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    def get_full_name(self):
        full_name = '%s %s' % (self.last_name, self.first_name)
        return full_name.strip()

    def get_short_name(self):
        return self.first_name

    def __str__(self):
        return self.get_full_name()

    class Meta:
        db_table = "user"
        verbose_name = 'user'
        verbose_name_plural = 'users'
        ordering = ['username']


class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    group = models.ForeignKey(Group, on_delete=models.PROTECT, related_name="users")
    '''
    {
        "commit": 20,
        "accepted": 17,
        ...
    }
    '''
    statistics = models.JSONField("problem statistics", default=dict)
    avatar = models.ImageField(upload_to='avatar/', default=f"avatar/default.jpg", null=True)
    bio = models.CharField(_('bio'), max_length=50, blank=True, null=True)

    def __str__(self):
        return self.user.get_full_name

    class Meta:
        db_table = "userprofile"
        ordering = ['id']
