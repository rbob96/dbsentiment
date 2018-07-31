from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from newspaper import Article
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from django.shortcuts import render
from .forms import ArticleForm, CompanyForm

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

def interpret(score):
    if (score >= 0.05):
        return "positive"
    elif (score > -0.05 and score < 0.05):
        return "neutral"
    elif (score <= -0.05):
        return "negative"
    else:
        return "score out of bounds"

# def get_url(request):
#     # if this is a POST request we need to process the form data
#     if request.method == 'POST':
#         # create a form instance and populate it with data from the request:
#         form = UrlForm(request.POST)
#         # check whether it's valid:
#         url = request.POST.get('textfield','None')
#         article = get_article(url)
#         sentiment = get_sentiment(article.text)
#         interpretation = interpret(sentiment)
#         return render(request, 'result.html', {'sentiment': sentiment, 'interpretation':interpretation})
#
#     # if a GET (or any other method) we'll create a blank form
#     else:
#         form = UrlForm()
#         return render(request, 'index.html', {'form': form})


def article(request):
    # If POST request, process the form
    if request.method == 'POST':
        form = ArticleForm(request.POST)

        #print (url)
        # Validate data and redirect to success
        if form.is_valid():
            print (form)
            url = request.POST.get('url')
            article = get_article(url)
            sentiment = get_sentiment(article.text)
            interpretation = interpret(sentiment)
            # get_article(url)

            return render(request, 'result.html', {'sentiment': sentiment, 'interpretation':interpretation,'article':article, 'article_url':url})

    # Other requests should render the page and blank form
    else:
        url = ArticleForm()

    return render(request, 'index.html', {'url': url})


# Render and handle the index page
def company(request):
    # If POST request, process the form
    if request.method == 'POST':
        company = CompanyForm(request.POST)
        print (company)

        # Validate data and redirect to success
        if company.is_valid():
            input = request.POST.get('company')

            return render(request, 'result.html', {'company': input})

    # Other requests should render the page and blank form
    else:
        input = CompanyForm()

    return render(request, 'index.html', {'company': input})