#_author:"gang"
#date: 2017/12/18

"""
分页实现的逻辑：
（1）获取所有的数据的个数
（2）每页要显示的个数
（3）总共要显示多少页
（4）每页最开始显示的页码数跟最后显示的页码数
（5）返回的a标签
"""

class Pagination(object):
    def __init__(self,current_page,total_count,base_url,params, per_page_count=10,max_page_count=11):
        """

        :param current_page: 当前的页码数
        :param total_count: 总共有多少条数据
        :param base_url: 拼接的url
        :param params: 原先的url中的条件
        :param per_page_count: 每页要显示的数据个数
        :param max_page_count: 每页要显示的翻页的页码个数
        """

        # 获取当前的页码数，并做判断，默认为1
        try:
            current_page = int(current_page)
        except Exception as e:
            current_page = 1
        if current_page <= 0:
            current_page = 1
        self.current_page = current_page

        # 获取数据的总条数
        self.total_count = total_count

        # url前缀
        self.base_url = base_url

        # 获取原先的url中的筛选条件，为实现跳转,默认获得的get数据没办法修改，设置_mutable。并且要copy出来修改，防止其他应用也修改url时，出现重和
        import copy
        params = copy.deepcopy(params)
        params._mutable = True
        self.params = params

        # 获取每页要显示的个数
        self.per_page_count = per_page_count

        # 要显示的最大的页码数
        max_page_num,div = divmod(total_count,per_page_count)
        if div:
            max_page_num+=1
        self.max_page_num = max_page_num

        # 页面默认显示的11个页面,并且当前页面在中间
        self.max_page_count=max_page_count
        self.half_max_page_count = int((max_page_count - 1)/2)

    # 定义要显示的数据的个数
    @property
    def start(self):
        return (self.current_page - 1) * self.per_page_count

    @property
    def end(self):
        return self.current_page * self.per_page_count

    # 返回前端的a标签
    def page_html(self):
        # 如果总的页数小于每页翻页的个数11的话，固定分页开头就是1,分页末尾是最大的总页数
        if self.max_page_num <= self.max_page_count:
            pager_start = 1
            pager_end = self.max_page_num
        # 如果大于每页翻页的个数11的话
        else:
            # 如果当前页<=half_max_page_count（每页标记的最中间的页码数）,固定开头为1
            if self.current_page <= self.half_max_page_count:
                pager_start = 1
                pager_end = self.max_page_count
            else:
                if (self.current_page + self.half_max_page_count) > self.max_page_num:
                    pager_end = self.max_page_num
                    pager_start = self.max_page_num - self.max_page_count + 1
                else:
                    pager_start = self.current_page - self.half_max_page_count
                    pager_end = self.current_page + self.half_max_page_count

        page_html_list=[]
        # 设置首页
        first_page = '<li><a href="%s?page=1">首页</a></li>'%(self.base_url)
        page_html_list.append(first_page)

        #上一页
        if self.current_page == 1:
            previous_page = '<li><a href="#">上一页</a></li>'
        else:
            previous_page = '<li><a href="%s?page=%s">上一页</a></li>'%(self.base_url,self.current_page - 1)
        page_html_list.append(previous_page)

        for i in range(pager_start,pager_end+1):
            if i == self.current_page:
                temp = '<li class="active"><a href="%s?page=%s">%s</a></li>'%(self.base_url,i,i)
            else:
                temp = '<li><a href="%s?page=%s">%s</a></li>' % (self.base_url, i, i)
            page_html_list.append(temp)

        # 下一页
        if self.current_page == self.max_page_num:
            next_page = '<li><a href="#">下一页</a></li>'
        else:
            next_page = '<li><a href="%s?page=%s">下一页</a></li>'%(self.base_url,self.current_page + 1)
        page_html_list.append(next_page)

        # 设置尾页
        last_page = '<li><a href="%s?page=%s">尾页</a></li>'%(self.base_url,self.max_page_num)
        page_html_list.append(last_page)

        return ''.join(page_html_list)