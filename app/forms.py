from django import forms

class ArticleForm(forms.Form):
    url = forms.CharField(label='Enter URL:', max_length=2083, widget=forms.TextInput(attrs={'class': 'form-control'}))

class CompanyForm(forms.Form):
    company = forms.CharField(label='Enter Company Name:', max_length=50, widget=forms.TextInput(attrs={'class': 'form-control'}))