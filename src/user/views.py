from django.contrib.auth import login,logout,authenticate
from django.shortcuts import render,redirect
from django.views import View
from .forms import LoginForm
from django.contrib import messages
from django.conf import settings
from .forms import SignupForm
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
# Create your views here.
def login_required(request):
    '''
    需要登陆访问
    根据/?next=,登陆跳转
    '''
    home_page_urlname = 'time_clock:index'
    get_full_path = request.get_full_path()
    try:
        if '?next=' in get_full_path : 
            get_full_urlnames = settings.NEXT_URLNAMES # 获取需要登陆的页面列表
            get_urlnames = [name.split(':') for name in get_full_urlnames] # 分开app_name和urlname
            index_next = get_full_path.find('next=') # 获取该索引位
            next_url = get_full_path[index_next:] # 获取next=到最后的字符
            get_url_name = next_url.split('/')[1] # 获取urlname
            # 只获取 urlname一致的list
            full_urlname_list = [fullname for fullname in get_urlnames if get_url_name == fullname[1]]
            one_full_onelist = full_urlname_list.pop() # 取消嵌套
            # 拼接成完整且唯一的url
            unique_url = '{appname}:{name}'.format(appname=one_full_onelist[0],name=one_full_onelist[1])
            return unique_url
    except Exception as e:
            print(e)
    return home_page_urlname

class Login_View(View):
    def get(self,request,*args,**kwargs):
        form = LoginForm()
        context = {}
        context['form'] = form
        context['title'] = '登陆'
        context['submit_text'] = 'Sign in'
        context['content_title'] = 'User Login'
        return render(request,'user/login.html',context)

    def post(self,request,*args,**kwargs):
        
        form = LoginForm(request.POST)
        context = {}
        context['form'] = form
        context['title'] = '登陆'
        context['submit_text'] = 'Sign in' 
        context['content_title'] = 'User Login' 
        if not form.is_valid():
            # 验证不通过，渲染同样模版
            return render(request, 'user/login.html',context)
        username = form.cleaned_data.get('username','')
        password = form.cleaned_data.get('password','')
        user = authenticate(username=username,password=password)
        if user.is_active:
            login(request,user)
            request.session['username'] = username
            messages.info(request, 'You Login Sucess')
            # 要求登陆
            get_next_urlname = login_required(self.request)
            if get_next_urlname:
                return redirect(get_next_urlname)
            return redirect('time_clock:index')       
        return render(request, 'user/login.html',context)
def auth_logout(request):
    logout(request)
    messages.success(request, 'You Logout Sucess')
    return redirect('user:login')
    
class Signup_View(CreateView):
    template_name = 'user/signup.html'
    form_class = SignupForm
    success_url = reverse_lazy('time_clock:index')

    def form_valid(self,form):
        result = super().form_valid(form)
        cleaned_data = form.cleaned_data
        user = authenticate(username=cleaned_data['username'],
                            password=cleaned_data['password1'])
        
        login(self.request, user)
        messages.info(self.request, 'You are a frist Login Sucess')
        return result
    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = '注册'
        context['submit_text'] = 'Register' 
        context['content_title'] = 'User Signup' 
        return context
        
