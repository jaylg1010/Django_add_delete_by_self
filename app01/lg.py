#_author:"gang"
#date: 2017/12/14

from app01 import models
from lug.service import lg
from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect


class UserInfoConfig(lg.LgConfig):
    list_display=["id","name","email"]

    show_search_form = True
    search_fields = ['name__contains','email__contains']

    show_add_btn = True

    def extra_url(self):
        url_list = [
            url(r'^report/$', self.report_view, ),
        ]
        return url_list
    def report_view(self,request):
        return HttpResponse("OK")

    def delete_view(self,request,nid,*args,**kwargs):
        if request.method == "GET":
            return render(request,'my_delete.html')
        else:
            self.model_class.objects.filter(pk=nid).delete()
            return redirect(self.get_list_url())

    def multi_del(self,request):
        pk_list = request.POST.getlist('pk')
        print("pk_list",pk_list)
        self.model_class.objects.filter(id__in=pk_list).delete()
    multi_del.short_desc = '批量删除'

    show_action = True
    actions = [multi_del]
lg.site.register(models.UserInfo,UserInfoConfig)



class RoleInfoConfig(lg.LgConfig):
    list_display = ['id','name']

lg.site.register(models.Role)