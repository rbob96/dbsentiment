from django import forms

from django import forms

class UrlForm(forms.Form):
    url = forms.CharField(label='URL', max_length=1000)
