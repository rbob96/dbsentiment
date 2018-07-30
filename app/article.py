import newspaper
from newspaper import Article
from nltk.sentiment.vader import SentimentIntensityAnalyzer
from nltk.tokenize import sent_tokenize

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