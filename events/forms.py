from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, Div
from .models import Event

class EventForm(forms.ModelForm):
    """فرم ایجاد و ویرایش رویداد"""
    class Meta:
        model = Event
        fields = ['name', 'description', 'start_date', 'end_date', 'location', 'image', 'is_active']
        widgets = {
            'start_date': forms.TextInput(attrs={'class': 'form-control persian-datepicker event-date', 'dir': 'ltr', 'autocomplete': 'off'}),
            'end_date': forms.TextInput(attrs={'class': 'form-control persian-datepicker event-date', 'dir': 'ltr', 'autocomplete': 'off'}),
            'description': forms.Textarea(attrs={'rows': 3}),
        }
        
    def clean(self):
        """اعتبارسنجی فرم"""
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # بررسی تاریخ شروع و پایان
        if start_date and end_date and end_date < start_date:
            self.add_error('end_date', 'تاریخ پایان نمی‌تواند قبل از تاریخ شروع باشد.')
        
        return cleaned_data
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-sm-2'
        self.helper.field_class = 'col-sm-10'
        
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='form-group col-md-6 mb-0'),
                Column('location', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('start_date', css_class='form-group col-md-6 mb-0'),
                Column('end_date', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'description',
            'image',
            'is_active',
            Div(
                Submit('submit', 'ذخیره', css_class='btn btn-primary'),
                css_class='text-center mt-4'
            )
        )
