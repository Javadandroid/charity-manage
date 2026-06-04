from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Button, Div

from .models import Font, SystemSetting

class FontForm(forms.ModelForm):
    """فرم برای آپلود و ویرایش فونت"""
    
    class Meta:
        model = Font
        fields = ['name', 'description', 'font_file', 'font_type', 'is_active']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'font-form'
        self.helper.form_class = 'needs-validation'
        self.helper.form_enctype = 'multipart/form-data'
        
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6'),
                Column('font_type', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'description',
            'font_file',
            'is_active',
            Div(
                Submit('submit', _('ذخیره'), css_class='btn btn-primary me-2'),
                Button('cancel', _('انصراف'), css_class='btn btn-secondary', onclick="window.history.back()"),
                css_class='d-flex justify-content-end'
            )
        )

class SystemSettingForm(forms.ModelForm):
    """فرم برای مدیریت تنظیمات سیستم"""
    
    class Meta:
        model = SystemSetting
        fields = ['site_title', 'logo', 'primary_color', 'secondary_color', 'primary_font', 'items_per_page']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'settings-form'
        self.helper.form_enctype = 'multipart/form-data'
        
        # فیلتر کردن فونت‌های فعال
        self.fields['primary_font'].queryset = Font.objects.filter(is_active=True)
        
        self.helper.layout = Layout(
            'site_title',
            'logo',
            Row(
                Column('primary_color', css_class='form-group col-md-6'),
                Column('secondary_color', css_class='form-group col-md-6'),
                css_class='form-row'
            ),
            'primary_font',
            Row(
                Column('items_per_page', css_class='form-group col-md-6'),
                css_class='form-row mt-3'
            ),
            Div(
                Submit('submit', _('ذخیره تنظیمات'), css_class='btn btn-primary me-2'),
                css_class='d-flex justify-content-end mt-3'
            )
        )
