import datetime
from django.shortcuts import render
from django.shortcuts import get_object_or_404, redirect, render
from django.views import View
from django.contrib import messages
from django.contrib.auth import get_user_model
from .models import UserActivity,UserActivityManager
from django.urls import reverse
from django.conf import settings
from .models import UserActivity
from django.views.generic.list import ListView
from .utils import current_page_round
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.db.models.query_utils import Q

# from django.contrib.auth.decorators import login_required
# from django.http import HttpResponseRedirect
# from django.utils import timezone
# from datetime import timedelta,time
# Create your views here.
Users = get_user_model()
class UserActivity_View(View):
    def get(self,request,*args,**kwargs):
        context = {}
        recent_obj = None
        if request.user.is_authenticated:
            recent_obj = UserActivity.objects.current(user=request.user)
        context['recent_obj'] = recent_obj
        context['title'] = '打卡'
        return render(request,'time_clock/index.html',context)

    def post(self,request,*args,**kwargs):
        '''
        1.使用签出延迟请使用
        UserActivity.objects.checkout_dely_toggle(request.user)
        2.不使用延迟
        UserActivity.objects.toggle(request.user)
        '''
        if request.user.is_authenticated:
            # if UserActivity.objects.today(user=request.user).first().activity == 'checkout':
            #     messages.error(request,'You have been checked out in this day')
            #     return redirect('time_clock:index')
            result = UserActivity.objects.checkout_dely_toggle(user=request.user)
            
            # print(result)
            if isinstance(result,str):
                messages.error(request,result)
        return redirect('time_clock:index')

class UserActivity_ListView(LoginRequiredMixin,ListView):
    login_url = '/user/login/'
    template_name = 'time_clock/history.html'
    # model = UserActivity
    context_object_name = 'user_activity_list'
    paginate_by = 8
    history_type = None
    q = None
    def dispatch(self, request, *args, **kwargs):
        self.history_type = self.kwargs.get('datetype','全部')
        self.q = request.GET.get('datetime') # 搜索
        return super().dispatch(request,*args,**kwargs)
    def get_history_type(self):
        history_type = self.history_type
        if history_type == 'today':
            return '今天'   
        if history_type == 'yesterday':
            return '昨天'    
        if history_type == 'aweek':
            return '一周内'
        return history_type
    def check_q(self):
        # 搜索
        if self.q:
            try:
                queryset = []
                if self.q.find('-') == -1 or self.q.count('-') !=2 :
                    messages.error(self.request,'Search error: Format must be like year-mon-day')
                    return queryset
                check_q_format = self.q.replace('-','')
                if not check_q_format.isdigit():
                    messages.error(self.request,'Search error:only number input')
                    return queryset
                datetime_list = self.q.split('-')
                datetime_int = tuple(map(int,datetime_list)) # 改为元组
                year , mon , day = datetime_int
                queryset = UserActivity.objects.filter(user=self.request.user,timestamp__date=datetime.date(year,mon,day))
                return queryset
            except Exception as e:
                # print(e)
                messages.error(self.request,'Search error')
                return queryset
    def get_queryset(self):
        # 搜索
        if self.q:
            return self.check_q()
        # 快速选择记录类型
        history_type = self.history_type
        if history_type == 'today':
            return UserActivity.objects.today(user=self.request.user)
        if history_type == 'yesterday':
            return UserActivity.objects.yesterday(user=self.request.user)
        if history_type == 'aweek':
            return UserActivity.objects.within_week(user=self.request.user)
        return UserActivity.objects.filter(user=self.request.user)
    def get_context_data(self,*args,**kwargs):
        context = super().get_context_data(**kwargs)
        page_obj = context.get('page_obj',None) # 获取page对象
        # 填充上下文context
        context['history_type'] = self.get_history_type()
        context['history_type_dict'] = {'today':'今天','yesterday':'昨天','aweek':'一周内'}
        context['title'] = '历史记录'
        context['current_page_round'] = current_page_round(page_obj)
        return context

