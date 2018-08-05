from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import newspaper
import json
from pprint import pprint
from newspaper import Article
from newspaper import news_pool
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize
from django.shortcuts import render
import plotly.plotly as py
import plotly.graph_objs as go
from plotly.offline import plot
from .forms import ArticleForm, CompanyForm
from alpha_vantage.timeseries import TimeSeries

# Create your views here.

# list of available sources
sources = ['nyt','bust','ft','bloomberg','theguardian','wsj','economist','washingtonpost']

# load output from json file and create a list of articles from all available sources

with open('/home/ruxi/NewsScraper/scraped_articles.json') as f:
    data = json.load(f)
all_articles = []
for source in sources:
    all_articles += data['newspapers'][source]['articles']

# alpha vantage API key
apiKey = '03WCM1DO8Y5FKB3E'

# get all articles that contain the company a user searches for either in the title or in the text of the article
def get_relevant_articles(all_articles, query):
    relevant_articles = []
    for i in range (0,len(all_articles)):
        if all_articles[i]['title'] is not None and (query in all_articles[i]['title'] or query in all_articles[i]['text']):
           relevant_articles += [all_articles[i]]
    return relevant_articles

# download and parse a single article and return an article object
def get_article(url):
    article = Article(url)
    article.download()
    article.parse()
    return article

# calculate the sentiment score of a single article
def get_sentiment(text):
    sum = 0
    if text!="":
        analyzer = SentimentIntensityAnalyzer()
        text_sentences = sent_tokenize(text)
        for sentence in text_sentences:
            sum += analyzer.polarity_scores(sentence)['compound']
        return sum/len(text_sentences)
    else:
        return sum/1

# interpret the sentiment score of a single article
def interpret(score):
    if (score >= 0.05):
        return "positive"
    elif (score > -0.05 and score < 0.05):
        return "neutral"
    elif (score <= -0.05):
        return "negative"
    else:
        return "score out of bounds"

# using the alpha_vantage python wrapper (https://github.com/RomelTorres/alpha_vantage)
# get daily share prices for a company, return them in json format - example here : https://www.alphavantage.co/query?function=TIME_SERIES_MONTHLY&symbol=MSFT&apikey=demo
def get_company_stocks(company_code):
    ts = TimeSeries(key = apiKey, output_format = 'json')
    data, metadata = ts.get_daily(symbol = company_code, outputsize='full')
    return data

# return lists of the publish dates of relevant articles and their scores
def get_dates_scores(relevant_articles):
    company_scores = {}
    for article in relevant_articles:
        company_scores[article['published']] = article['sentiment']
    return company_scores

#index view
def index(request):
    template = loader.get_template('index.html')
    return HttpResponse(template.render({},request))

# article view
def article(request):
    # If POST request, process the form

    if request.method == 'POST':
        form = ArticleForm(request.POST)

        #print (url)
        # Validate data and redirect to success
        if form.is_valid():
            #print (form)
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

# plotting function - plot dates and sentiment scores for relevant articles
def plot_sentiment_graph (dictionary):
    dates = list(dictionary.keys())
    dates.sort()

    x_axis = []
    y_axis = []
    for date in dates:
        x_axis +=[date]
        y_axis +=[dictionary[date]]

    trace0 = go.Scatter(
        x=x_axis,
        y=y_axis,
        mode='lines',
        name='lines'
    )
    data = [trace0]
    layout = dict(
        title='Sentiment Over Time',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

# similar function, plot share prices and dates - will probably merge them in one function since code is redundant
def plot_share_graph (dictionary):
    dates = list(dictionary.keys())
    dates.sort()

    x_axis = []
    y_axis = []
    for date in dates:
        x_axis +=[date]
        y_axis +=[dictionary[date]['1. open']]

    trace0 = go.Scatter(
        x=x_axis,
        y=y_axis,
        mode='lines',
        name='lines'
    )
    data = [trace0]
    layout = dict(
        title='Share Price Over Time',
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1,
                         label='1m',
                         step='month',
                         stepmode='backward'),
                    dict(count=6,
                         label='6m',
                         step='month',
                         stepmode='backward'),
                    dict(step='all')
                ])
            ),
            rangeslider=dict(
                visible=True
            ),
            type='date'
        )
    )

    fig = go.Figure(data=data, layout=layout)
    plot_div = plot(fig, output_type='div', include_plotlyjs=False)
    return plot_div

# company view
def company(request):
    # If POST request, process the form
    if request.method == 'POST':
        company = CompanyForm(request.POST)
        print (company)

        # Validate data and redirect to success
        if company.is_valid():
            input = request.POST.get('company')
            query = input
            relevant_articles = get_relevant_articles(all_articles,query)
            #print (relevant_articles)
            dates_scores = get_dates_scores(relevant_articles)
            #print (dates_scores)
            simple_plot = plot_sentiment_graph(dates_scores)
            share_prices = get_company_stocks('FB')
            #print (share_prices)
            share_plot = plot_share_graph(share_prices)

            return render(request, 'company_result.html', {'company': input, 'plot':simple_plot, 'share_plot':share_plot})

    # Other requests should render the page and blank form
    else:
        input = CompanyForm()

    return render(request, 'company.html', {'company': input})