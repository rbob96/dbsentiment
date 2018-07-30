from __future__ import unicode_literals
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import json
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render

from .forms import UrlForm

# Create your views here.

def index(request):

    template = loader.get_template('index.html')

    context = {}

    return HttpResponse(template.render(context,request))

def get_url(request):
    # if this is a POST request we need to process the form data
    if request.method == 'POST':
        # create a form instance and populate it with data from the request:
        form = UrlForm(request.POST)
        # check whether it's valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required
            # ...
            # redirect to a new URL:
            pass

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UrlForm()

    return render(request, 'index.html', {'form': form})