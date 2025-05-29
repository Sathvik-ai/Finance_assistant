from fastapi import FastAPI
import yfinance as yf

app = FastAPI()

@app.get("/price")
def get_stock_price(ticker: str):
    stock = yf.Ticker(ticker)
    data = stock.history(period="1d")
    if data.empty:
        return {"error": "Invalid ticker or no data"}
    
    latest_price = data['Close'].iloc[-1]
    return {"ticker": ticker, "latest_close": float(latest_price)}
