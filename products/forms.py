from django import forms
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div
from .models import Product, UnitOfMeasure

class UnitOfMeasureForm(forms.ModelForm):
    """فرم ایجاد و ویرایش واحد اندازه‌گیری"""
    class Meta:
        model = UnitOfMeasure
        fields = ['name', 'symbol']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('symbol', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Div(
                Submit('submit', _('ذخیره'), css_class='btn btn-primary'),
                css_class='text-center mt-4'
            )
        )

class ProductForm(forms.ModelForm):
    """فرم ایجاد و ویرایش محصول"""
    class Meta:
        model = Product
        fields = ['code', 'name', 'description', 'booth', 'price', 'unit', 'image', 'is_available']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, booth=None, **kwargs):
        self.booth = booth
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        # اگر غرفه‌ای از قبل تعیین شده باشد، آن را به عنوان مقدار پیش‌فرض قرار دهید
        if booth:
            self.fields['booth'].initial = booth
            # مخفی کردن فیلد غرفه از فرم و استفاده از فیلد مخفی
            self.fields['booth'].widget = forms.HiddenInput()
    
    def save(self, commit=True):
        """ذخیره محصول با تنظیم غرفه در صورت نیاز"""
        product = super().save(commit=False)
        
        # اگر غرفه از قبل تعیین شده باشد، آن را تنظیم کن
        if self.booth and not product.booth_id:
            product.booth = self.booth
        
        if commit:
            product.save()
        
        return product

class ProductBulkUploadForm(forms.Form):
    """فرم آپلود گروهی محصولات از طریق CSV"""
    file = forms.FileField(
        label=_('فایل CSV'),
        help_text=_('فایل CSV باید شامل ستون‌های: کد، نام، توضیحات، قیمت، واحد باشد.')
    )
    booth = forms.ModelChoiceField(
        queryset=None,
        label=_('غرفه')
    )
    
    def __init__(self, *args, **kwargs):
        from booths.models import Booth
        super().__init__(*args, **kwargs)
        self.fields['booth'].queryset = Booth.objects.filter(is_active=True)
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        
        self.helper.layout = Layout(
            'booth',
            'file',
            Div(
                Submit('submit', _('آپلود و پردازش'), css_class='btn btn-primary'),
                css_class='text-center mt-4'
            )
        )
