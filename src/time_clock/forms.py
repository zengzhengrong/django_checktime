from django import forms
from django.contrib.auth import get_user_model

User = get_user_model()
class CheckRequired_PwForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput)
    password = forms.CharField(label='',widget=forms.PasswordInput(attrs={'class':'form-control','placeholder':'输入密码','type':'password','required':'true'}))
    def clean(self,*args,**kwagrs):
        cleaned_data = self.cleaned_data
        username = cleaned_data.get('username','')
        password = cleaned_data.get('password','')
        exist_user = User.objects.filter(username__iexact=username)
        message = '密码错误'
        # 存在这个用户但密码错误
        if exist_user.exists() and exist_user.count()==1:
            user = exist_user.first()
            check_password = user.check_password(password)
            if not check_password :
                raise forms.ValidationError(message,code='invalid')
        return cleaned_data
            
        
