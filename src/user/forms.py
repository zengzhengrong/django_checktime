import re
from django import forms 
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
User = get_user_model()

class LoginForm(forms.Form):
    username = forms.CharField(label='账号',widget=forms.TextInput(attrs={'class':'form-control','placeholder':'输入账号','required':'true'}))
    password = forms.CharField(label='密码',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'输入密码','type':'password','required':'true'}))

    def clean(self,*args,**kwagrs):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username','')
        password = cleaned_data.get('password','')
        exist_user = User.objects.filter(username__iexact=username)
        message = '账号或者密码错误'
        # 不存在这个用户
        if not exist_user.exists() or exist_user.count() != 1:
            raise forms.ValidationError(message,code='invalid')
        # 存在这个用户但密码错误
        if exist_user.exists() and exist_user.count()==1:
            user = exist_user.first()
            check_password = user.check_password(password)
            if not check_password :
                raise forms.ValidationError(message,code='invalid')
        return cleaned_data

class SignupForm(UserCreationForm):
    username = forms.CharField(
        label='账号',
        widget=forms.TextInput(attrs={'class':'form-control','placeholder':'输入账号，不能含有中文','required':'true'})
        )
    password1 = forms.CharField(
        label="密码",
        strip=False,
        widget=forms.PasswordInput(attrs={'placeholder':'输入密码,包含字母+数字组合，不少于8位','type':'password','required':'true'}),
    )
    password2 = forms.CharField(
        label="确认密码",
        widget=forms.PasswordInput(attrs={'placeholder':'再次输入密码','type':'password','required':'true'}),
        strip=False,
        # help_text=_("Enter the same password as before, for verification."),
    )
    def clean_username(self):
        username = self.cleaned_data.get("username")
        zh_pattern = re.compile(u'[\u4e00-\u9fa5]+')
        result = zh_pattern.search(username)
        if result:
            raise forms.ValidationError(('账号不能含有中文'),code = 'invalid')
        return username