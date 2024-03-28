import requests  # For news retrieval
from textblob import TextBlob

def get_news(query):
    """
    Retrieves news articles for a given query using a news API.

    Args:
        query (str): The search term for news articles.

    Returns:
        list: A list of dictionaries containing news article information
              (may vary depending on the API used).
    """

    # Replace 'YOUR_NEWS_API_KEY' with your actual API key
    news_api_key = "1ff67f37fded4d319447445f1cd7280a"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={news_api_key}"

    response = requests.get(url)
    data = response.json()

    if data["status"] == "ok":
        return data["articles"]
    else:
        print(f"Error: Failed to retrieve news using News API ({data['message']})")
        return []  # Empty list if news retrieval fails

def get_sentiment(statement):
    """
    Analyzes the sentiment of a statement using TextBlob.

    Args:
        statement (str): The statement to analyze.

    Returns:
        str: The sentiment label (positive, negative, or neutral).
    """

    blob = TextBlob(statement)
    sentiment = blob.sentiment.polarity

    if sentiment > 0:
        return "positive"
    elif sentiment < 0:
        return "negative"
    else:
        return "neutral"

if __name__ == "__main__":
    # Replace 'YOUR_NEWS_API_KEY' with a valid News API key
    # You can get a free API key at https://newsapi.org/
    news_api_key = "1ff67f37fded4d319447445f1cd7280a"

    if not news_api_key:
        print("Error: Please provide a valid News API key in the 'get_news' function.")
        exit()

    # Get news about TSLA
    ticker = input("Enter the ticker symbol: ") # Input the ticker symbol
    news = get_news(query=ticker)

    # Check if news retrieval was successful
    if not news:
        exit()  # Exit if news retrieval fails

    # Apply sentiment analysis to each news description
    for article in news:
        description = article.get("description")  # Extract description (may vary depending on API)
        if description:
            sentiment = get_sentiment(description)
            print(f"Headline: {article.get('title')}")  # Extract title (may vary depending on API)
            print(f"Description: {description}")
            print(f"Sentiment: {sentiment}")
            print("-" * 20)  # Separator between articles
