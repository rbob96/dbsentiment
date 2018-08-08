from __future__ import unicode_literals
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
import newspaper
from plotly import tools
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
sources = ['nyt','bbc','ft','bloomberg','theguardian','wsj','economist','washingtonpost','investors']

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

def plot_subplot(sentiment, share_prices):
    dates_s = list(sentiment.keys())
    dates_s.sort()

    x_axis_s = []
    y_axis_s = []
    for date in dates_s:
        x_axis_s += [date]
        y_axis_s += [sentiment[date]]

    trace0 = go.Scatter(
        x=x_axis_s,
        y=y_axis_s,
        mode='lines',
        name='sentiment'
    )

    dates = list(share_prices.keys())
    dates.sort()

    x_axis_p = []
    y_axis_p = []
    for date in dates:
        x_axis_p += [date]
        y_axis_p += [share_prices[date]['1. open']]

    trace1 = go.Scatter(
        x=x_axis_p,
        y=y_axis_p,
        mode='lines',
        name='share price'
    )


    fig = tools.make_subplots(rows=2, cols=1, subplot_titles=('Sentiment Score','Share Price')
                              )

    fig.append_trace(trace0, 1, 1)
    fig.append_trace(trace1, 2, 1)

    fig['layout'].update(height=1200, width=1100, title='Company Sentiment vs Company Share Price', autosize=True, xaxis=dict(
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
        ),yaxis=dict(title='Sentiment'),xaxis2=dict(
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
            type='date',
        title = "Date"
        ) , yaxis2=dict(title='Share Price'))
    return plot(fig, output_type='div', include_plotlyjs=False)

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
            #simple_plot = plot_sentiment_graph(dates_scores)
            if input == 'Facebook' or input=='facebook':
                share_prices = get_company_stocks('FB')
            elif input == 'Apple'or input=='apple':
                share_prices = get_company_stocks('AAPL')
            elif input == 'J.P. Morgan' or input=='j.p. morgan':
                share_prices = get_company_stocks('JPM')
            elif input== 'Tesla' or input=='tesla':
                share_prices= get_company_stocks('TSLA')
            elif input == 'Samsung' or input=='samsung':
                share_prices = get_company_stocks('SMSN.L')
            elif input == 'Deutsche Bank' or input =='deutsche bank':
                share_prices = get_company_stocks('DB')
            elif input=='Google' or input=='google':
                share_prices=get_company_stocks('GOOGL')
            #print (share_prices)
            plot = plot_subplot(dates_scores,share_prices)

            return render(request, 'company_result.html', {'company': input, 'plot':plot})

    # Other requests should render the page and blank form
    else:
        input = CompanyForm()

    return render(request, 'company.html', {'company': input})