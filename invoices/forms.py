from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from .models import Invoice, InvoiceItem

class InvoiceForm(forms.ModelForm):
    """فرم ایجاد و ویرایش فاکتور"""
    donation_amount = forms.DecimalField(
        label=_('مبلغ همت عالی (تومان)'),
        required=False,
        initial=None,
        min_value=0,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 10000'})
    )
    
    description = forms.CharField(
        label=_('توضیحات'),
        required=False,
        widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
    )
    
    discount_amount = forms.DecimalField(
        label=_('درصد تخفیف'),
        required=False,
        initial=None,
        min_value=0,
        max_value=100,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'مثال: 10'})
    )
    
    payment_method = forms.ChoiceField(
        label=_('روش پرداخت'),
        required=True,
        choices=Invoice.PAYMENT_METHODS,
        initial='card',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = Invoice
        fields = ['booth', 'customer_name', 'customer_phone', 'donation_amount', 'discount_amount', 
                 'description', 'payment_method']
        widgets = {
            'customer_name': forms.TextInput(attrs={'placeholder': 'به صورت خودکار پر می‌شود', 'required': False}),
            'customer_phone': forms.TextInput(attrs={'placeholder': 'اختیاری'}),
        }
    
    def __init__(self, *args, user=None, booth=None, **kwargs):
        self.default_booth = booth
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_id = 'invoice-form'
        
        # صریحا فیلد نام مشتری را غیر اجباری می‌کنیم (برای مرورگر)
        self.fields['customer_name'].required = False
        
        # اگر کاربر معین شده باشد، غرفه‌های در دسترس را فیلتر کنید
        if user:
            from booths.models import Booth
            if user.is_staff or user.is_superuser:
                # برای کاربران ادمین تمام غرفه‌های فعال را نمایش دهید
                self.fields['booth'].queryset = Booth.objects.filter(is_active=True)
            else:
                # برای کاربران عادی فقط غرفه‌های خودشان را نمایش دهید
                managed_booths = Booth.objects.filter(manager=user, is_active=True)
                staff_booths = Booth.objects.filter(staff=user, is_active=True)
                self.fields['booth'].queryset = (managed_booths | staff_booths).distinct()
            
            # اگر غرفه از قبل تعیین شده باشد، آن را به عنوان مقدار پیش‌فرض قرار دهید
            if booth:
                self.fields['booth'].initial = booth
                # مخفی کردن فیلد غرفه از فرم و استفاده از فیلد مخفی
                self.fields['booth'].widget = forms.HiddenInput()
            # اگر فقط یک غرفه موجود باشد، آن را به عنوان پیش‌فرض انتخاب کنید
            elif self.fields['booth'].queryset.count() == 1:
                self.fields['booth'].initial = self.fields['booth'].queryset.first()
    
    def clean_customer_name(self):
        """اگر نام مشتری خالی باشد، آن را با 'بدون نام' پر می‌کند"""
        customer_name = self.cleaned_data.get('customer_name', '').strip()
        if not customer_name:
            return "بدون نام"
        return customer_name
                
    def save(self, commit=True):
        """ذخیره فاکتور با تنظیم غرفه در صورت نیاز"""
        invoice = super().save(commit=False)
        
        # اگر غرفه از قبل تعیین شده باشد، آن را تنظیم کن
        if self.default_booth and not invoice.booth_id:
            invoice.booth = self.default_booth
        
        # اگر نام مشتری خالی باشد، عبارت "بدون نام" را قرار بده
        if not invoice.customer_name or invoice.customer_name.strip() == '':
            invoice.customer_name = "بدون نام"
        
        if commit:
            invoice.save()
        
        return invoice


class InvoiceItemForm(forms.ModelForm):
    """فرم آیتم‌های فاکتور"""
    class Meta:
        model = InvoiceItem
        fields = ['product', 'quantity', 'price', 'is_delivered']
