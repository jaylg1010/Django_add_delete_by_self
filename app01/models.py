from django.db import models

# Create your models here.

class UserInfo(models.Model):
    name = models.CharField(verbose_name="用户名称",max_length=32)

    def __str__(self):
        return self.name

class Role(models.Model):
    name= models.CharField(verbose_name="角色名称",max_length=32)

    def __str__(self):
        return self.name