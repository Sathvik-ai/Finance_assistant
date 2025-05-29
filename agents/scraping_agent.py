from fastapi import FastAPI
import requests
from bs4 import BeautifulSoup

app = FastAPI()

@app.get("/news")
def get_company_news(query: str = "TSMC"):
    url = f"https://news.google.com/search?q={query}+stock"
    headers = {"User-Agent": "Mozilla/5.0"}

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return {"error": "Failed to fetch news"}

    soup = BeautifulSoup(response.text, "html.parser")
    headlines = soup.select("article h3")
    news = [headline.text for headline in headlines[:5]]  # Get top 5

    return {"company": query, "headlines": news}
