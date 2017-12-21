# _author:"gang"
# date: 2017/12/14
from django.conf.urls import url
from django.shortcuts import HttpResponse, render, redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
from django.http import QueryDict
from django.db.models import Q
import copy

# 组合筛选的条件类
class FilterOption(object):
    def __init__(self, field_name, multi=False, condition=None, is_choice=False):
        '''
        组合筛选限制条件的类，可以限制是否是单选或者是否要在前端显示
        :param field_name:
        :param multi:
        :param condition:
        :param is_choice:
        '''
        self.field_name = field_name
        self.multi = multi
        self.condition = condition
        self.is_choice = is_choice

    def get_queryset(self, _field):
        '''
        根据condition获取前端要显示的数据字段
        :param _field:
        :return:
        '''
        if self.condition:
            return _field.rel.to.objects.filter(**self.condition)
        return _field.rel.to.objects.all()

    def get_choices(self, _field):
        '''
        如果配置是单选的话，调用这个方法
        :param _field:
        :return:
        '''
        return _field.choices

# 生成组合查询的单选或者多选的url
class FilterRow(object):
    def __init__(self,option, data, request):
        self.data = data
        self.option = option
        # request.GET
        self.request = request


    def __iter__(self):
        # 对QueryDict进行修改
        params = copy.deepcopy(self.request.GET)
        params._mutable = True
        # 获取当前的id与多选的id_list
        current_id = params.get(self.option.field_name) # 3
        current_id_list = params.getlist(self.option.field_name) # [1,2,3]

        if self.option.field_name in params:
            # 如果要选择的字段在url在选择删除
            # del params[self.option.field_name]
            origin_list = params.pop(self.option.field_name)
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe('<a href="{0}">全部</a>'.format(url))
            params.setlist(self.option.field_name,origin_list)
        else:
            url = "{0}?{1}".format(self.request.path_info, params.urlencode())
            yield mark_safe('<a class="active" href="{0}">全部</a>'.format(url))
        # ( (1,男),(2,女)  )
        # 循环获得的数据
        for val in self.data:
            # 判断是否是单选，从配置文件中判断,获取id与值
            if self.option.is_choice:
                pk,text = str(val[0]),val[1]
            else:
                pk,text = str(val.pk), str(val)
            # 当前URL？option.field_name
            # 当前URL？gender=pk
            # self.request.path_info # http://127.0.0.1:8005/arya/crm/customer/?gender=1&id=2
            # self.request.GET['gender'] = 1 # &id=2gender=1
            if not self.option.multi:
                # 单选
                params[self.option.field_name] = pk
                url = "{0}?{1}".format(self.request.path_info,params.urlencode())
                if current_id == pk:
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url,text))
                else:
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))
            else:
                # 多选 current_id_list = ["1","2"]
                _params = copy.deepcopy(params)
                id_list = _params.getlist(self.option.field_name)

                if pk in current_id_list:
                    id_list.remove(pk)
                    _params.setlist(self.option.field_name, id_list)
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))
                else:
                    id_list.append(pk)
                    # params中被重新赋值
                    _params.setlist(self.option.field_name,id_list)
                    # 创建新增的URL
                    url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                    yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))


# 把change_list方法封装到一个类中
class ChangeList(object):
    def __init__(self, config, queryset):
        self.config = config

        self.list_display = config.get_list_display()
        self.model_class = config.model_class
        self.request = config.request
        self.queryset = queryset
        self.show_add_btn = config.get_show_add_btn()

        # 组合搜索
        self.comb_filter = config.get_comb_filter()
        # actions
        self.actions = config.get_actions()
        self.show_actions = config.get_show_actions()

        # 搜索功能
        self.show_search_form = config.get_show_search_form()
        self.search_form_val = config.request.GET.get(config.search_key, '')
        # 显示分页功能
        current_page = self.request.GET.get('page', 1)
        total_count = queryset.count()
        from utils.pager import Pagination
        page_obj = Pagination(current_page, total_count, self.request.path_info, self.request.GET, per_page_count=2)

        self.page_obj = page_obj

        self.data_list = queryset[page_obj.start:page_obj.end]

    # 对actions中的函数进行修改，给前端只返回函数名，这样在前段只显示函数的名字
    def modify_actions(self):
        result = []
        for func in self.actions:
            temp = {'name': func.__name__, 'text': func.short_desc}
            result.append(temp)
        return result

    def add_url(self):
        return self.config.get_add_url()

    def head_list(self):
        # 处理表头
        head_list = []
        # 循环列表中的方法以及要显示的字符串
        for field_name in self.list_display:
            # 如果是字符串，则获取数据库表中的字段的verbose_name
            if isinstance(field_name, str):
                verbose_name = self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name = field_name(self.config, is_header=True)
            head_list.append(verbose_name)
        return head_list

    def body_list(self):
        # 处理表的内容
        data_list = self.data_list
        new_data_list = []
        for row in data_list:
            temp = []
            for field_name in self.list_display:
                if isinstance(field_name, str):
                    val = getattr(row, field_name)
                else:
                    val = field_name(self.config, row)
                temp.append(val)
            new_data_list.append(temp)
        return new_data_list

    # 拿到组合搜索的地段，以及数据库中的数据，返回到前端
    def gen_comb_filter(self):
        from django.db.models import ForeignKey, ManyToManyField
        for option in self.comb_filter:
            _field = self.model_class._meta.get_field(option.field_name)
            if isinstance(_field, ForeignKey):
                # 获取当前字段depart，关联的表 Department表并获取其所有数据
                # print(field_name,_field.rel.to.objects.all())
                row = FilterRow(option, option.get_queryset(_field), self.request)
            elif isinstance(_field, ManyToManyField):
                # print(field_name, _field.rel.to.objects.all())
                # data_list.append(  FilterRow(_field.rel.to.objects.all()) )
                row = FilterRow(option, option.get_queryset(_field), self.request)

            else:
                # print(field_name,_field.choices)
                # data_list.append(  FilterRow(_field.choices) )
                row = FilterRow(option, option.get_choices(_field), self.request)
            # 可迭代对象
            yield row


class LgConfig(object):
    def __init__(self, model_class, site):
        self.model_class = model_class
        self.site = site

        self.request = None
        self._query_param_key = "_listfilter"
        self.search_key = "_q"

    # 给url加装饰器，使得增删改查函数具有request参数
    def wrap(self, view_func):
        def inner(request, *args, **kwargs):
            self.request = request
            return view_func(request, *args, **kwargs)

        return inner

    # 生成增删改查的url
    def get_urls(self):
        app_model_name = (self.model_class._meta.app_label, self.model_class._meta.model_name,)

        urlpatterns = [
            url(r'^$', self.wrap(self.changelist_view), name="%s_%s_changelist" % app_model_name),
            url(r'^add/$', self.wrap(self.add_view), name="%s_%s_add" % app_model_name),
            url(r'^(\d+)/delete/$', self.wrap(self.delete_view), name="%s_%s_delete" % app_model_name),
            url(r'^(\d+)/change/$', self.wrap(self.change_view), name="%s_%s_change" % app_model_name),
        ]
        urlpatterns.extend(self.extra_url())
        return urlpatterns

    # 定义额外的url
    def extra_url(self):
        return []

    @property
    def urls(self):
        return self.get_urls()

    # 获取url,点击编辑、添加、删除按钮时根据name的反向生成来走视图函数
    def get_change_url(self, nid):
        name = "lg:%s_%s_change" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        edit_url = reverse(name, args=(nid,))
        return edit_url

    def get_list_url(self):
        name = "lg:%s_%s_changelist" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        list_url = reverse(name)
        return list_url

    def get_add_url(self):
        name = "lg:%s_%s_add" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        add_url = reverse(name)
        return add_url

    def get_delete_url(self, nid):
        name = "lg:%s_%s_delete" % (self.model_class._meta.app_label, self.model_class._meta.model_name,)
        delete_url = reverse(name, args=(nid,))
        return delete_url

    # 定制页面显示列数
    def checkbox(self, obj=None, is_header=False):
        if is_header:
            return '选择'
        return mark_safe('<input type="checkbox" name="pk" value="%s">' % (obj.id,))

    # 前端显示的编辑按钮
    def edit(self, obj=None, is_header=False):
        if is_header:
            return '编辑'
        # 获取request条件
        query_str = self.request.GET.urlencode()  # page=2&nid=1
        if query_str:
            # 重新构造
            params = QueryDict(mutable=True)
            params[self._query_param_key] = query_str
            return mark_safe('<a href="%s?%s">编辑</a>' % (self.get_change_url(obj.id, ), params.urlencode()))
        else:
            return mark_safe('<a href="%s">编辑</a>' % (self.get_change_url(obj.id, )))

    # 前端显示的删除按钮
    def delete(self, obj=None, is_header=False):
        if is_header:
            return '删除'
        return mark_safe('<a href="%s">删除</a>' % (self.get_delete_url(obj.id)))

    # 获得前端显示的类中
    list_display = []

    def get_list_display(self):
        data = []
        if self.list_display:
            data.extend(self.list_display)
            data.append(LgConfig.edit)
            data.append(LgConfig.delete)
            data.insert(0, LgConfig.checkbox)
        return data

    # 是否显示添加按钮
    show_add_btn = False

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

    # 关键字搜索
    # 给前端返回条件，判断是否显示搜索框
    show_search_form = False

    def get_show_search_form(self):
        return self.show_search_form

    # 定义组合搜索的字段
    comb_filter = []

    def get_comb_filter(self):
        result = []
        if self.comb_filter:
            result.extend(self.comb_filter)
        return result

    # 定义要搜索的字段
    search_fields = []

    def get_search_fields(self):
        result = []
        if self.search_fields:
            result.extend(self.search_fields)
        return result

    # 获得前端搜索的关键字
    def get_search_condition(self):
        key_word = self.request.GET.get(self.search_key)
        search_fields = self.get_search_fields()
        condition = Q()
        condition.connector = 'or'
        if key_word and self.get_show_search_form():
            for field_name in search_fields:
                condition.children.append((field_name, key_word))
        return condition

    # action定制
    # 前段是否显示
    show_action = False

    def get_show_actions(self):
        return self.show_action

    # 显示哪些action
    actions = []

    def get_actions(self):
        result = []
        if self.actions:
            result.extend(self.actions)
        return result

    # 对显示界面中的数据表头与数据的处理
    def changelist_view(self, request, *args, **kwargs):
        if request.method == "POST" and self.get_show_actions():
            func_name_str = request.POST.get("list_action")
            action_func = getattr(self, func_name_str)
            ret = action_func(request)
            if ret:
                return ret

        # 联合搜索的条件
        comb_condition={}
        option_list = self.get_comb_filter()
        for key in request.GET.keys():
            value_list = request.GET.getlist(key)
            flag = False
            for option in option_list:
                if option.field_name == key:
                    flag = True
                    break
            if flag:
                comb_condition["%s__in"%key]=value_list
        queryset = self.model_class.objects.filter(self.get_search_condition()).filter(**comb_condition).distinct()
        cl = ChangeList(self, queryset)
        return render(request, 'changelist.html', {"cl": cl})

    # 增加视图函数
    def add_view(self, request, *args, **kwargs):
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class()
            return render(request, "add_view.html", {"form": form})
        else:
            form = model_form_class(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_list_url())
            return render(request, 'add_view.html', {"form": form})

    # 删除视图函数
    def delete_view(self, request, nid, *args, **kwargs):
        obj = self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_list_url())

    # 编辑视图函数
    def change_view(self, request, nid, *args, **kwargs):
        obj = self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_list_url())
        model_form_class = self.get_model_form_class()
        if request.method == "GET":
            form = model_form_class(instance=obj)
            return render(request, "change_view.html", {"form": form})
        else:
            form = model_form_class(instance=obj, data=request.POST)
            if form.is_valid():
                form.save()
                list_query_str = request.GET.get(self._query_param_key)
                list_url = "%s?%s" % (self.get_list_url(), list_query_str)
                return redirect(list_url)
            return render(request, 'change_view.html', {"form": form})


class LgSite(object):
    '''
    该类中把注册的类加入到_registry字典中，并且定义url方法
    匹配app名称以及注册的类的名称
    '''

    def __init__(self):
        self._registry = {}

    def register(self, model_class, lg_config_class=None):
        '''
        该函数的作用是：把注册的类加入到_registry字典中，并且把这个注册的类放到第三的参数关联的类中
        :param model_class: 注册的类名
        :param lg_config_class: 定义参数，与LgConfig类关联或者与注册时自定义的类关联
        :return:
        '''
        if not lg_config_class:
            lg_config_class = LgConfig
        self._registry[model_class] = lg_config_class(model_class, self)

    def get_urls(self):
        url_pattern = []
        for model_class, lg_config_obj in self._registry.items():
            app_name = model_class._meta.app_label
            model_name = model_class._meta.model_name

            curd_url = url(r'^%s/%s/' % (app_name, model_name), (lg_config_obj.urls, None, None))
            url_pattern.append(curd_url)
        return url_pattern

    @property
    def urls(self):
        '''
        该函数调用get_urls()函数，返回一个元组
        :return:
        '''
        return (self.get_urls(), None, 'lg')


site = LgSite()
