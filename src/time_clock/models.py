from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime,time,timedelta
from django.conf import settings
# from django.contrib import messages
# from django.utils import timezone
# Create your models here.
# User activity
# 获取延迟时间
get_activity_timedelta = getattr(settings,'TIME_DELTA_MIN',1)
get_pass_checkin = getattr(settings,'PASS_CHECKIN',True)
get_check_intoday = getattr(settings,'CHECK_IN_TODAY',False)
def instance_type(**kwargs):
    for key,value in kwargs.items():
        if key == 'TIME_DELTA_MIN' and not isinstance(value,int):
            raise TypeError("The param %s should be %s,but it's %s now!"%(key,'int',type(value)))
        if key == 'PASS_CHECKIN' and not isinstance(value,bool):
            raise TypeError("The param %s should be %s,but it's %s now!"%(key,'bool',type(value)))
        if key == 'CHECK_IN_TODAY' and not isinstance(value,bool):
            raise TypeError("The param %s should be %s,but it's %s now!"%(key,'bool',type(value)))    
instance_type(
            TIME_DELTA_MIN=get_activity_timedelta,
            PASS_CHECKIN=get_pass_checkin,
            CHECK_IN_TODAY=get_check_intoday)

USER_ACTIVITY_CHOICES =[
    ('checkin','签到'),
    ('checkout','签出')
]
class UserActivityQuerySet(models.query.QuerySet):
    '''
    模型查询集:自定义查询集
    '''
    def filter_date(self,*args,**kwagrs):
        '''
        days=0 filter today
        days=1 filter yesterday
        days=-1 filter yesterday
        if days = +-2 filter within 2 days  ex.days=7 filter within a week
        '''
        # print(args,kwagrs)
        days = kwagrs.get('days',None)
        if days is None:
            raise TypeError('filter_date() takes 1 keywords arguments:days')
        if days < 0 :
            days =  -days
        days_delta = timedelta(days=days) #时间轴
        now_date = timezone.localdate() #　当天的日期
        start_date = now_date - days_delta # 起始日
        # print('可选日期：',start_date)
        datetime_start = timezone.make_aware(datetime.combine(start_date,time.min))# 起始时间
        datetime_end = timezone.make_aware(datetime.combine(start_date,time.max))
        if days >=2 : # 范围内可选
            datetime_end = timezone.make_aware(datetime.combine(now_date,time.max))
        return self.filter(timestamp__gte=datetime_start).filter(timestamp__lte=datetime_end)
    def current_set(self,user=None):
        if user is None:
            return None
        current = self.filter(user=user).order_by('-timestamp').first()
        return current
class UserActivityManager(models.Manager):
    '''
    模型管理器:自定义模型对象操作，例如查询和保存
    '''
    def get_queryset(self,*args,**kwagrs):
        return UserActivityQuerySet(self.model,using=self._db)
    def current(self,user=None):
        if user == None:
            return None
        current_obj = self.get_queryset().current_set(user=user)
        return current_obj
    def toggle(self,user=None):
        if user == None:
            return None
        # 检测今天是否已经签到
        check_in_today = get_check_intoday # True表示今日签出不给再签到
        today_queryset = self.today(user=user)
        msg = 'You have been checked out in this day'
        # 初始上次对象的活动
        get_current_activity = None
        # 默认动作
        action_activity = 'checkin'
        # 起始计数
        init_count = 1
        get_current = self.current(user=user)   
        if get_current:
            # 上次对象的活动类型
            get_current_activity = get_current.activity
            # 上次对象的活动计数
            get_current_activity_count = get_current.activity_count
            # 计数加一
            next_count = get_current_activity_count + 1 
        if get_current_activity == 'checkin':
            action_activity = 'checkout'
        if today_queryset.exists() and today_queryset.first().activity == 'checkout' and check_in_today:
            return msg
        
        new_obj = self.model(user=user,
                            activity=action_activity,
                            activity_count=next_count if get_current else init_count)
        new_obj.save()
        return new_obj
    def checkout_dely_toggle(self,user=None):
        pass_checkin = get_pass_checkin # True不需要延迟
        recent_obj = self.current(user=user)
        if recent_obj != None:
            recent_obj_timestamp = recent_obj.timestamp
            delta = timedelta(minutes=get_activity_timedelta)
            # 下次action 时间
            action_time = recent_obj_timestamp + delta
            now = timezone.now()
            diff_time = action_time - now
            if recent_obj.activity == 'checkout' and pass_checkin :
                return self.toggle(user=user)
            if now < action_time:
                # print('{:.1f}分钟'.format(diff_time.seconds/60))
                diff_time_shift = '{:.0f}秒'.format(diff_time.seconds)
                msg = 'Must wait {time}'.format(time=diff_time_shift)
                return msg
            # return self.toggle(user=user)
        return self.toggle(user=user)
    # 日期范围快捷函数
    def get_daterange(self,days=0,user=None):
        if user is None:
            return self.get_queryset().filter_date(days=days)
        return self.get_queryset().filter(user=user).filter_date(days=days)
    def today(self,days=0,user=None):
        return self.get_daterange(user=user,days=days)
    def yesterday(self,days=1,user=None):
        return self.get_daterange(user=user,days=days)
    def within_week(self,days=7,user=None):
        return self.get_daterange(user=user,days=days)
class UserActivity(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE,verbose_name='用户')
    activity = models.CharField(max_length=20,default='checkin',choices=USER_ACTIVITY_CHOICES,verbose_name='状态')
    timestamp = models.DateTimeField(auto_now_add=True,verbose_name='记录时间')
    activity_count = models.IntegerField(blank=True,verbose_name='操作次数')
    objects = UserActivityManager()
    class Meta:
        verbose_name='打卡记录'
        verbose_name_plural=verbose_name
        ordering = ['-timestamp']

    def __str__(self):
        return self.user.username

    def clean(self,*args,**kwargs):
        if self.user:
            user_activitys = UserActivity.objects.filter(user=self.user).order_by('-timestamp')    
            # print([ac.activity for ac in user_activitys])
            if user_activitys.exists():
                recent = user_activitys.first()
                # print(recent.activity)
                if self.activity == recent.activity:
                    message = '无效操作:你已经%s过' %(self.get_activity_display())
                    raise ValidationError(message)
            else:
                if self.activity != 'checkin':
                    message = '无效操作:第一次不能%s' %(self.get_activity_display())
                    raise ValidationError(message)
        return super(UserActivity,self).clean(*args,**kwargs)

    def next_activity(self):
        next = '签到'
        if self.activity == 'checkin':
            next = '签出'
        return next
    @property
    def current_activity_display(self):
        show = '签到'
        if self.activity == 'checkout':
            show = '签出'
        return show
    def today_is_checked(self,user):
        msg ='今日已经打卡了'
        today_objs = self.objects.today(user=user)
        if today_objs:
            obj_activity = today_objs.first().activity
            if  obj_activity == 'checkout':
                return msg
        return self.objects.checkout_dely_toggle(user=user)
            
