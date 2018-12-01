from django.contrib import admin
from .models import UserActivity
# Register your models here.
class UserActivityModelAdmin(admin.ModelAdmin):
    list_display = ['user','activity','timestamp']
    list_filter = ['user','timestamp']
    search_fields = ['user__username','timestamp']
    class Meta:
        model = UserActivity
admin.site.register(UserActivity,UserActivityModelAdmin)