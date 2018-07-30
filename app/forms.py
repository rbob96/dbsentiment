from django import forms

class UrlForm(forms.Form):
    analyse = forms.CharField(label='URL', max_length=1000)