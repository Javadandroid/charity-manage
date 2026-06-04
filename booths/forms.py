from django import forms
from django.utils.translation import gettext_lazy as _
from django.contrib.auth.models import User
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div
from .models import Booth, POSDevice

class BoothForm(forms.ModelForm):
    """فرم ایجاد و ویرایش غرفه"""
    class Meta:
        model = Booth
        fields = ['name', 'description', 'event', 'manager', 'staff', 'image', 'is_active', 'show_in_kiosk']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
            'staff': forms.SelectMultiple(attrs={'class': 'select2 form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'
        
        # فیلتر کردن کاربران فعال با دسترسی مناسب برای مدیریت
        self.fields['manager'].queryset = User.objects.filter(is_active=True)
        self.fields['staff'].queryset = User.objects.filter(is_active=True)
        
        # اجازه تغییر نمایش در کیوسک فقط برای ادمین
        if not (user and user.is_staff):
            # پیش‌فرض غیرفعال است؛ برای غیرادمین‌ها قابل ویرایش نباشد
            self.fields['show_in_kiosk'].disabled = True

        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('event', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            Row(
                Column('manager', css_class='form-group col-md-6 mb-0'),
                Column('staff', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'image',
            Row(
                Column('is_active', css_class='form-group col-md-6 mb-0'),
                Column('show_in_kiosk', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', _('ذخیره'), css_class='btn btn-primary'),
                css_class='text-center mt-4'
            )
        )

class POSDeviceForm(forms.ModelForm):
    """فرم ایجاد و ویرایش دستگاه پوز"""
    
    class Meta:
        model = POSDevice
        fields = ['name', 'device_type', 'connection_type', 'bank', 
                 'ip_address', 'port', 'serial_port', 'baud_rate', 
                 'terminal_id', 'merchant_id', 'is_active', 'is_kiosk']
        widgets = {
            'ip_address': forms.TextInput(attrs={'placeholder': '192.168.1.100'}),
            'serial_port': forms.TextInput(attrs={'placeholder': 'COM1'}),
        }
    
    def __init__(self, *args, **kwargs):
        booth = kwargs.pop('booth', None)
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        # اگر غرفه از قبل تعیین شده باشد، فیلد غرفه را پنهان می‌کنیم
        if booth:
            self.instance.booth = booth
            
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-4 mb-0'),
                Column('device_type', css_class='form-group col-md-4 mb-0'),
                Column('bank', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('connection_type', css_class='form-group col-md-4 mb-0'),
                css_class='form-row'
            ),
            Div(
                Row(
                    Column('ip_address', css_class='form-group col-md-6 mb-0'),
                    Column('port', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                css_class='tcp-fields'
            ),
            Div(
                Row(
                    Column('serial_port', css_class='form-group col-md-6 mb-0'),
                    Column('baud_rate', css_class='form-group col-md-6 mb-0'),
                    css_class='form-row'
                ),
                css_class='serial-fields'
            ),
            Row(
                Column('terminal_id', css_class='form-group col-md-6 mb-0'),
                Column('merchant_id', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'is_active',
            'is_kiosk',
            Div(
                Submit('submit', _('ذخیره'), css_class='btn btn-primary'),
                css_class='text-center mt-4'
            )
        )

    def clean(self):
        cleaned = super().clean()
        is_kiosk = cleaned.get('is_kiosk')
        booth = self.instance.booth
        if is_kiosk and booth:
            from .models import POSDevice
            qs = POSDevice.objects.filter(booth=booth, is_kiosk=True)
            if self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                self.add_error('is_kiosk', _('برای هر غرفه فقط یک دستگاه کیوسک مجاز است.'))
        return cleaned
