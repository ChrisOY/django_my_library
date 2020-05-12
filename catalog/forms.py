# // /catalog/forms.py
# //p9a> create form for books to renew
import datetime
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy as _

# //p9-m2> model form
from django.forms import ModelForm
from catalog.models import BookInstance


# //m2> using ModelForm
class RenewBookModelForm(ModelForm):
    def clean_due_back(self):
        data = self.cleaned_data['due_back']
        
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
        
        return data
    
    class Meta:
        model = BookInstance
        fields = ['due_back']
        labels = {'due_back': _('New renewal date')}
        help_texts = {'due_back': _('Enter a date between now and 4 weeks (default 3).')}


# //m1> using Form
class RenewBookForm(forms.Form):
    renewal_date = forms.DateField(help_text="Enter a date between now and 4 weeks (default 3).")
    
    def clean_renewal_date(self):
        data = self.cleaned_data['renewal_date']
        
        # // check if a date is not in the past
        if data < datetime.date.today():
            raise ValidationError(_('Invalid date - renewal in past'))
        
        # // check if a date is in the aloowed range
        if data > datetime.date.today() + datetime.timedelta(weeks=4):
            raise ValidationError(_('Invalid date - renewal more than 4 weeks ahead'))
        
        # // return cleaned data
        return data
    

