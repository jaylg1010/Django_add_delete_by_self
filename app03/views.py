from django.shortcuts import render

# Create your views here.


HOST_LIST = []
for i in range(1, 104):
    HOST_LIST.append("c%s.com" % i)


def hosts(request):

    try:
        current_page = int(request.GET.get('page',1))
    except Exception as e:
        current_page=1
    per_count_num = 10

    start = (current_page - 1)*per_count_num
    end = current_page * per_count_num
    host_list = HOST_LIST[start:end]

    total_count = len(HOST_LIST)

    max_page_num,div = divmod(total_count,per_count_num)
    if div:
        max_page_num+=1
    page_html_list=[]

    for i in (1,max_page_num+1):
        if i==current_page:
            temp='<a class="active" href="/hosts/?page=%s">%s</a>'%(i,i,)
        else:
            temp='<a href="/hosts/?page=%s">%s</a>'%(i,i,)
        page_html_list.append(temp)

    page_html=''.join(page_html_list)
    return render(request,"host.html",{"host_list":host_list,"page_html":page_html})


