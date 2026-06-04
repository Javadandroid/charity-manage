from django.contrib import admin
from .models import Font, SystemSetting

@admin.register(Font)
class FontAdmin(admin.ModelAdmin):
    list_display = ('name', 'font_type', 'is_active')

@admin.register(SystemSetting)
class SystemSettingAdmin(admin.ModelAdmin):
    list_display = ('site_title',)

    def has_add_permission(self, request):
        if self.model.objects.exists():
            return False
        return super().has_add_permission(request)
