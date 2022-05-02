import imp
from django import forms
from .models import Customer

class CustomerForm(forms.ModelForm):
    

    class Meta:
        model = Customer

        exclude = ['joineddate','status','user','loginkey']
