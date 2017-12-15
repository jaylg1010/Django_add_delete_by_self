#_author:"gang"
#date: 2017/12/14
from django.conf.urls import url
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm

class LgConfig(object):
    list_display = []
    def __init__(self,model_class,site):
        self.model_class = model_class
        self.site = site

    def get_urls(self):
        app_model_name = (self.model_class._meta.app_label,self.model_class._meta.model_name,)

        urlpatterns = [
            url(r'^$', self.changelist_view,name="%s_%s_changelist"%app_model_name),
            url(r'^add/$', self.add_view,name="%s_%s_add"%app_model_name),
            url(r'^(\d+)/delete/$', self.delete_view,name="%s_%s_delete"%app_model_name),
            url(r'^(\d+)/change/$', self.change_view,name="%s_%s_change"%app_model_name),
        ]
        urlpatterns.extend(self.extra_url())
        return urlpatterns

    def extra_url(self):
        return []
    @property
    def urls(self):
        return self.get_urls()

    # 获取url,点击编辑、添加、删除按钮时根据name的反向生成来走视图函数
    def get_change_url(self,nid):
        name = "lg:%s_%s_change"%(self.model_class._meta.app_label,self.model_class._meta.model_name,)
        edit_url=reverse(name,args=(nid,))
        return edit_url

    def get_list_url(self):
        name = "lg:%s_%s_changelist"%(self.model_class._meta.app_label,self.model_class._meta.model_name,)
        list_url = reverse(name)
        return list_url

    def get_add_url(self):
        name = "lg:%s_%s_add"%(self.model_class._meta.app_label,self.model_class._meta.model_name,)
        add_url = reverse(name)
        return add_url

    def get_delete_url(self,nid):
        name = "lg:%s_%s_delete"%(self.model_class._meta.app_label,self.model_class._meta.model_name,)
        delete_url = reverse(name,args=(nid,))
        return delete_url


    # 定制页面显示列数
    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s">'%(obj.id,))

    def edit(self,obj=None,is_header=False):
        if is_header:
            return '编辑'
        return mark_safe('<a href="%s">编辑</a>'%(self.get_change_url(obj.id,)))

    def delete(self,obj=None,is_header=False):
        if is_header:
            return '删除'
        return mark_safe('<a href="%s">删除</a>'%(self.get_delete_url(obj.id)))

    def get_list_display(self):
        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(LgConfig.edit)
            data.append(LgConfig.delete)
            data.insert(0,LgConfig.checkbox)
        return data


    # 是否显示添加按钮
    show_add_btn = True
    def get_show_add_btn(self):
        return self.show_add_btn

    # 创建ModelForm实现添加和编辑
    model_form_class = None

    def get_model_form_class(self):
        if self.model_form_class:
            return self.model_form_class
        class TestModelForm(ModelForm):
            class Meta:
                model = self.model_class
                fields = "__all__"
        return TestModelForm


    # 对显示界面中的数据表头与数据的处理
    def changelist_view(self,request,*args,**kwargs):
        # 处理表头
        head_list = []
        # 循环列表中的方法以及要显示的字符串
        for field_name in self.get_list_display():
            # 如果是字符串，则获取数据库表中的字段的verbose_name
            if isinstance(field_name,str):
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self,is_header=True)
            head_list.append(verbose_name)

        data_list = self.model_class.objects.all()
        new_data_list=[]
        for row in data_list:
            temp = []
            for field_name in self.get_list_display():
                if isinstance(field_name,str):
                    val = getattr(row,field_name)
                else:
                    val = field_name(self,row)
                temp.append(val)
            new_data_list.append(temp)
        return render(request,'changelist.html',{'data_list':new_data_list,'head_list':head_list,"show_add_btn":self.show_add_btn,"add_url":self.get_add_url()})

    def add_view(self,request,*args,**kwargs):
        model_form_class = self.get_model_form_class()
        if request.method=="GET":
            form = model_form_class()
            return render(request, "add_view.html", {"form":form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'add_view.html', {"form":form})

    def delete_view(self,request,nid,*args,**kwargs):
        obj = self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_list_url())


    def change_view(self,request,nid,*args,**kwargs):
        obj = self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_list_url())
        model_form_class=self.get_model_form_class()
        if request.method=="GET":
            form = model_form_class(instance=obj)
            return render(request,"change_view.html",{"form":form})
        else:
            form = model_form_class(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request,'change_view.html',{"form":form})




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
        if not lg_config_class:
            lg_config_class = LgConfig
        self._registry[model_class]=lg_config_class(model_class,self)

    def get_urls(self):
        url_pattern = []
        for model_class,lg_config_obj in self._registry.items():
            app_name = model_class._meta.app_label
            model_name = model_class._meta.model_name

            curd_url = url(r'^%s/%s/'%(app_name,model_name),(lg_config_obj.urls,None,None))
            url_pattern.append(curd_url)
        return url_pattern

    @property
    def urls(self):
        '''
        该函数调用get_urls()函数，返回一个元组
        :return:
        '''
        return (self.get_urls(),None,'lg')


site = LgSite()