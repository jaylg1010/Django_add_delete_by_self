#_author:"gang"
#date: 2017/12/20
from . import models
from lug.service import lg

class UserInfoConfig(lg.LgConfig):

    def display_gender(self,obj=None,is_header=False):
        if is_header:
            return '性别'

        # return obj.gender
        # 从数据库的choice中拿对应的中文
        return obj.get_gender_display()

    def display_depart(self,obj=None,is_header=False):
        if is_header:
            return '部门'
        return obj.depart.caption

    def display_roles(self,obj=None,is_header=False):
        if is_header:
            return '角色'

        html = []
        role_list = obj.roles.all()
        for role in role_list:
            html.append(role.title)

        return ",".join(html)

    list_display = ['id', 'name', 'email', display_gender, display_depart, display_roles]
    comb_filter = [
        lg.FilterOption('gender',is_choice=True),
        lg.FilterOption('depart'),
        lg.FilterOption('roles')
    ]

    show_action = True

    search_fields = ['name__contains', 'email__contains']
    show_search_form = True


lg.site.register(models.UserInfo,UserInfoConfig)
lg.site.register(models.Department)
lg.site.register(models.Role)
