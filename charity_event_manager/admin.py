from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User, Group
from django.utils.translation import gettext_lazy as _

# تنظیم مجدد پنل ادمین برای کاربران
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active', 'date_joined', 'last_login')
    list_filter = ('is_staff', 'is_superuser', 'is_active', 'groups')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('اطلاعات شخصی'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('دسترسی‌ها'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('تاریخ‌های مهم'), {'fields': ('last_login', 'date_joined')}),
    )
    
    filter_horizontal = ('groups', 'user_permissions',)

# جایگزینی UserAdmin پیش‌فرض با نسخه سفارشی
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

# تنظیم مجدد پنل ادمین برای گروه‌ها
class CustomGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'get_users_count')
    search_fields = ('name',)
    filter_horizontal = ('permissions',)
    
    def get_users_count(self, obj):
        return obj.user_set.count()
    get_users_count.short_description = 'تعداد کاربران'

# جایگزینی GroupAdmin پیش‌فرض با نسخه سفارشی
admin.site.unregister(Group)
admin.site.register(Group, CustomGroupAdmin)

# سفارشی‌سازی بخش ادمین
admin.site.site_header = 'پنل مدیریت سیستم رویدادهای خیریه'
admin.site.site_title = 'مدیریت سیستم'
admin.site.index_title = 'پنل مدیریت'
