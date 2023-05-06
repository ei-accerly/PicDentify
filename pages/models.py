from django.db import models

# Create your models here.
from datetime import datetime
from django.utils import timezone
from django.contrib.auth.models import BaseUserManager
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

# Create your models here.

now = timezone.now()


class MyUserManager(BaseUserManager):
    def create_user(self, admin_id, username, user_key, password=None, **extra_fields):
        extra_fields.setdefault('is_superuser', False)
        user = self.model(admin_id=admin_id, username=username, user_key=user_key, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, admin_id, username, user_key, password, **extra_fields):
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(admin_id, username, user_key, password=password, **extra_fields)
    

class AdminUser(AbstractBaseUser, PermissionsMixin):
    admin_id = models.PositiveIntegerField(primary_key=True)
    username = models.CharField(max_length=30, unique=True)
    user_key = models.CharField(max_length=30, unique=True)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'

    class Meta:
        db_table = 'admin'

class AdminKey(models.Model):
    key_id = models.AutoField(primary_key=True, unique=True)
    admin_key = models.CharField(max_length=50, verbose_name='admin_key')

    class Meta:
        db_table = "admin_key"

class Topics(models.Model):
    topic_id = models.AutoField(primary_key=True, unique=True)
    topic_name = models.CharField(max_length=100, verbose_name='topic_name')
    owner = models.ForeignKey(AdminUser, on_delete=models.CASCADE)

    class Meta:
        db_table = "topics"
    
class Difficulty(models.Model):
    difficulty_id = models.AutoField(primary_key=True, unique=True)
    difficulty_name = models.CharField(max_length=20, verbose_name='difficulty')
    words = models.JSONField()
    topic = models.ForeignKey(Topics, on_delete=models.CASCADE)
    time_limit = models.IntegerField(blank=False, null=False)
    points_per_question = models.IntegerField(blank=False, null=False)
    maxpoints = models.IntegerField(blank=False, null=False)
    answered = models.IntegerField(blank=False, null=False)
    score = models.IntegerField(blank=False, null=False, default=0)
    class Meta:
        db_table = "difficulty"


    