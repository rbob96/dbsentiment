from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from newspaper import Article
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from django.shortcuts import render
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot
from .forms import ArticleForm, CompanyForm

# Create your views here.

DB = ["https://www.bloomberg.com/news/articles/2018-07-27/deutsche-bank-is-said-to-cut-staff-in-chicago-amid-u-s-retreat",
      "https://www.bloomberg.com/news/articles/2018-07-25/ex-deutsche-bank-traders-charged-in-expanding-spoofing-probe",
      "https://www.bloomberg.com/news/articles/2018-07-25/deutsche-bank-s-sewing-talks-about-growth-again-amid-cutbacks",
      "https://www.bloomberg.com/view/articles/2018-07-25/deutsche-bank-is-playing-for-time",
      "https://www.bloomberg.com/view/articles/2018-07-25/for-deutsche-bank-escapee-freedom-brings-its-own-woes",
      "https://www.bloomberg.com/news/articles/2018-07-25/deutsche-bank-vows-to-defend-fixed-income-trading-after-cutbacks"]

JP = []

MS = []

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

def get_company_scores(list):
    company_scores = []
    article_dates = []
    for url in list:
        article = get_article(url)
        sentiment = get_sentiment(article.text)
        company_scores += [sentiment]
        article_dates += [article.publish_date]
    return company_scores, article_dates


def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({},request))

def article(request):
    # If POST request, process the form
    score, dates = get_company_scores(DB)

    print (score)
    print (dates)

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

    return render(request, 'article.html', {'url': url})

def plot_graph (x_axis, y_axis):
    trace0 = go.Scatter(
        x=x_axis,
        y=y_axis,
        mode='lines',
        name='lines'
    )
    data = [trace0]
    layout = go.Layout(
        # autosize=False,
        # width=900,
        # height=500,

        xaxis=dict(
            autorange=True
        ),
        yaxis=dict(
            autorange=True
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

# Render and handle the index page
def company(request):
    # If POST request, process the form
    if request.method == 'POST':
        company = CompanyForm(request.POST)
        print (company)

        # Validate data and redirect to success
        if company.is_valid():
            input = request.POST.get('company')
            if input == "Deutsche Bank":
                scores, dates = get_company_scores(DB)
                simple_plot = plot_graph(dates, scores)
            return render(request, 'company_result.html', {'company': input, 'scores':scores, 'dates':dates, 'plot':simple_plot})

    # Other requests should render the page and blank form
    else:
        input = CompanyForm()

    return render(request, 'company.html', {'company': input})