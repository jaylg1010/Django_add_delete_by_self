#_author:"gang"
#date: 2017/12/14

from app01 import models
from lug.service import lg
from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect


class UserInfoConfig(lg.LgConfig):
    list_display=["id","name"]

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


lg.site.register(models.UserInfo,UserInfoConfig)



class RoleInfoConfig(lg.LgConfig):
    list_display = ['id','name']

lg.site.register(models.Role)