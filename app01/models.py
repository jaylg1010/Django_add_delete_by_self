from django.db import models

# Create your models here.

class UserInfo(models.Model):
    name = models.CharField(verbose_name="用户名称",max_length=32)
    email = models.EmailField(verbose_name='邮箱', max_length=32)
    pwd = models.CharField(verbose_name='密码', max_length=32)
    ut = models.ForeignKey(verbose_name='用户类型', to="UserType")
    def __str__(self):
        return self.name

class Role(models.Model):
    name= models.CharField(verbose_name="角色名称",max_length=32)

    def __str__(self):
        return self.name

class UserType(models.Model):
    name = models.CharField(max_length=32,verbose_name="类型名称")

    def __str__(self):
        return self.name