from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


# Create your models here.


class UserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email):
        if not email:
            raise ValueError('email is required...!')

        user = self.model(email=self.normalize_email(email))
        user.set_password(email)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password):
        user = self.create_user(email=self.normalize_email(email))
        user.set_password(password)
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser):
    uid = models.CharField(max_length=100, unique=True, blank=True, null=True, help_text='Google provider uid')
    email = models.EmailField(max_length=255, unique=True, blank=False, null=False)
    password = models.CharField(max_length=128)
    _nickname = models.CharField(max_length=100, null=True, blank=True, unique=True, db_column='nickname')
    picture = models.CharField(max_length=255, blank=True, null=True, help_text='Google Profile Thumbnail')
    locale = models.CharField(max_length=4, default='ko', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        db_table = 'accounts'
        verbose_name_plural = '사용자'

    def __str__(self):
        return self.email

    @staticmethod
    def has_perm(perm, obj=None):
        return True

    @staticmethod
    def has_module_perms(app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

    @property
    def is_superuser(self):
        return self.is_admin

    @property
    def nickname(self):
        if self._nickname:
            return self._nickname
        return self.email.split("@")[0]

    @nickname.setter
    def nickname(self, value):
        self._nickname = value

    def save(self, *args, **kwargs):
        if not self.password:
            self.set_password(self.email)
        super().save(*args, **kwargs)


class RefreshTokens(models.Model):
    refresh_token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'refresh_tokens'
        verbose_name_plural = 'Refresh Tokens'
