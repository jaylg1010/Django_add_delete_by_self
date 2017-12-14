#_author:"gang"
#date: 2017/12/14
from django.conf.urls import url
from django.shortcuts import HttpResponse,render


class LgConfig(object):
    list_display = []
    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site

    def get_urls(self):
        app_model_name = (self.model_class._meta.app_label,self.model_class._meta.model_name,)

        urlpatterns = [
            url(r'^$', self.changelist_view,name="%s_%s_changelist"%app_model_name),
            url(r'add/^$', self.add_view,name="%s_%s_add"%app_model_name),
            url(r'^(\d+)/delete/$', self.delete_view,name="%s_%s_delete"%app_model_name),
            url(r'^(\d+)/change/$', self.change_view,name="%s_%s_change"%app_model_name),
        ]

        return urlpatterns

    @property
    def urls(self):
        return self.get_urls()

    def changelist_view(self,request,*args,**kwargs):
        data_list = self.model_class.objects.all()
        print("data_list_+_+_+_+",data_list)
        new_data_list=[]
        for row in data_list:
            temp = []
            for field_name in self.list_display:
                if isinstance(field_name,str):
                    val = getattr(row,field_name)
                else:
                    val = field_name(self,row)
                temp.append(val)
            new_data_list.append(temp)
        print(new_data_list)
        return render(request,'changelist.html',{'data_list':new_data_list})

    def add_view(self):
        pass

    def delete_view(self):
        pass

    def change_view(self):
        pass



class LgSite(object):
    '''
    该类中把注册的类加入到_registry字典中，并且定义url方法
    匹配app名称以及注册的类的名称
    '''
    def __init__(self):
        self._registry={}

    def register(self,model_class,lg_config_class=None):
        '''
        该函数的作用是：把注册的类加入到_registry字典中，并且把这个注册的类放到第三的参数关联的类中
        :param model_class: 注册的类名
        :param lg_config_class: 定义参数，与LgConfig类关联或者与注册时自定义的类关联
        :return:
        '''
        print("register",456)
        if not lg_config_class:
            lg_config_class = LgConfig
        self._registry[model_class]=lg_config_class(model_class,self)

    def get_urls(self):
        print("get_urls",123)
        print("self._registry",self._registry)
        url_pattern = []
        for model_class,lg_config_obj in self._registry.items():
            app_name = model_class._meta.app_label
            model_name = model_class._meta.model_name

            curd_url = url(r'^%s/%s/'%(app_name,model_name),(lg_config_obj.urls,None,None))
            url_pattern.append(curd_url)
        print(url_pattern)
        return url_pattern

    @property
    def urls(self):
        '''
        该函数调用get_urls()函数，返回一个元组
        :return:
        '''
        return (self.get_urls(),None,'lg')


site = LgSite()