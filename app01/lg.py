#_author:"gang"
#date: 2017/12/14

from app01 import models
from lug.service import lg


class UserInfoConfig(lg.LgConfig):
    list_display=["id","name"]

lg.site.register(models.UserInfo,UserInfoConfig)



class RoleInfoConfig(lg.LgConfig):
    list_display = ['id','name']

lg.site.register(models.Role)