from __future__ import unicode_literals
from django.http import HttpResponse
from django.template import loader
from django.shortcuts import render
import newspaper
from newspaper import Article
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
import json
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.shortcuts import render
from .forms import UrlForm

# Create your views here.

def get_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article

def get_sentiment(text):
    analyzer = SentimentIntensityAnalyzer()
    text_sentences = sent_tokenize(text)
    sum = 0
    for sentence in text_sentences:
        sum += analyzer.polarity_scores(sentence)['compound']
    return sum/len(text_sentences)
#ft_paper = newspaper.build('https://www.ft.com/?edition=uk', memoize_articles = False)
def interpret(score):
    if (score >= 0.5):
        return "positive"
    elif (score > -0.5 and score < 0.5):
        return "neutral"
    elif (score <= -0.5):
        return "negative"
    else:
        return "score out of bounds"

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
        url = request.POST.get('textfield','None')
        article = get_article(url)
        sentiment = get_sentiment(article.text)
        interpretation = interpret(sentiment)
        return render(request, 'result.html', {'sentiment': sentiment, 'interpretation':interpretation})

    # if a GET (or any other method) we'll create a blank form
    else:
        form = UrlForm()
        return render(request, 'index.html', {'form': form})