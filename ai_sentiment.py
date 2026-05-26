from textblob import TextBlob


def analyze_sentiment(text):

    blob = TextBlob(text)

    polarity = blob.sentiment.polarity

    if polarity > 0:
        return "BULLISH"

    elif polarity < 0:
        return "BEARISH"

    return "NEUTRAL"