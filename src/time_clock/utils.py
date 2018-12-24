from django.conf import settings

CHECK_REQUIRED_PASSWORD = getattr(settings,'CHECK_REQUIRED_PASSWORD',False)
def check_password_form_get(request,context,form):
    return form(initial={'username':request.user})

def check_password_form_post(request,context,form):
    if len(request.POST) == 1:
        return None
    form = form(request.POST)
    if not form.is_valid():
        # 验证不通过，渲染同样模版
        context['title'] = '打卡'
        context['form'] = form
        return context
    return None

def check_password_form(request,context,form):
    if request.method == 'GET':
        return check_password_form_get(request,context,form)
    if request.method == 'POST':
        return check_password_form_post(request,context,form)
    raise TypeError('http method is not get or post')

def check_required_password(request,context,form,recent_obj=None):
    # bool类型
    if isinstance(CHECK_REQUIRED_PASSWORD,bool):
        if CHECK_REQUIRED_PASSWORD:
            return check_password_form(request,context,form)
        return None

    # dict类型
    if isinstance(CHECK_REQUIRED_PASSWORD,dict):

        checkin_required = CHECK_REQUIRED_PASSWORD.get('checkin')
        checkout_required = CHECK_REQUIRED_PASSWORD.get('checkout')
        
        # 两个都是True 或者 False
        if checkin_required and checkout_required:
            return check_password_form(request,context,form)

        if checkin_required==False and checkout_required==False:
            return None
        # 其中一个True另一个是False
        if checkin_required or checkout_required:
            if checkin_required and request.method == 'GET':
                if recent_obj is None:
                    return check_password_form_get(request,context,form)
                if recent_obj.activity == 'checkout':
                    return check_password_form_get(request,context,form)
            if checkout_required and request.method == 'GET':
                if recent_obj.activity == 'checkin':
                    return check_password_form_get(request,context,form)
            
            if checkin_required and request.method == 'POST':
                return check_password_form_post(request,context,form)   
            if checkout_required and request.method == 'POST':
                return check_password_form_post(request,context,form)

            return None
    raise TypeError('http method error')
    
def current_page_round(page_obj):
    '''
    1.当前页面的附近页
    2.保存当前页面的前后两页，以及第一页和最后一页，中间页码用省略号填充
    3.例如当前页为5,总页数为10
    则current_page_round=[1,...,3,4,5,6,7...,10]
    '''
    if page_obj is None:
        return None
    current_page = page_obj.number # 当前页面
    total_page = page_obj.paginator.num_pages # 总页数 
    # print('{} of {}'.format(current_page,total_page)) 
    # 例如current_page=4,total_page=7
    # current_page_round = [2,3,4,5,6]
    current_page_round = list(range(max(current_page-2,1),current_page))+\
    list(range(current_page,min(current_page+2,total_page)+1)) 
    
    # 添加省略号
    if current_page_round[0]-1 >= 2:
        current_page_round.insert(0,'...')
    if current_page_round[-1]-total_page <= -2:
        current_page_round.append('...')
    # 添加首页尾页
    if current_page_round[0] != 1 :
        current_page_round.insert(0,1) # 在0位置插入1
    if current_page_round[-1] != total_page :
        current_page_round.append(total_page)
    # print(current_page_round)
    return current_page_round