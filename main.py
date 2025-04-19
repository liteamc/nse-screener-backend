from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "NSE Screener is working!"}

fastapi
uvicorn
yfinance
import requests
import zipfile
import io
import pandas as pd
from datetime import datetime, timedelta


def download_nse_bhavcopy():
    # Get yesterday’s date
    date = datetime.now() - timedelta(days=1)
    day = date.strftime('%d')
    month = date.strftime('%b').upper()
    year = date.strftime('%Y')

    url = f"https://www1.nseindia.com/content/historical/EQUITIES/{year}/{month}/cm{day}{month}{year}bhav.csv.zip"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        raise Exception("Failed to download NSE Bhavcopy")

    with zipfile.ZipFile(io.BytesIO(response.content)) as z:
        file_name = z.namelist()[0]
        with z.open(file_name) as f:
            df = pd.read_csv(f)

    return df


def filter_equity_stocks(df):
    df = df[df['SERIES'] == 'EQ']  # Only Equity stocks
    df['SYMBOL'] = df['SYMBOL'].str.strip()
    return df[['SYMBOL', 'OPEN', 'HIGH', 'LOW', 'CLOSE', 'TOTTRDQTY', 'TOTTRDVAL']]


def detect_patterns(df):
    # Example mocked market cap for demo purposes
    # In production, use real market cap info (could be preloaded JSON or another API)
    mock_market_caps = {
        'INFY': 600000000000,
        'RELIANCE': 1700000000000,
        'TCS': 1400000000000,
        'HDFCBANK': 1100000000000,
    }

    results = []

    for _, row in df.iterrows():
        symbol = row['SYMBOL']
        open_price = row['OPEN']
        high = row['HIGH']
        low = row['LOW']
        close = row['CLOSE']

        market_cap = mock_market_caps.get(symbol, 0)
        if market_cap < 100000000000:  # ₹10,000 Cr
            continue

        range_ = high - low
        if range_ == 0:
            continue

        # Bullish Pin Bar (simplified)
        is_bullish_pin = (
            close > open_price and
            (high - close) < (0.33 * range_) and
            (open_price - low) > (0.66 * range_)
        )

        # Fully Shaved Bar
        is_fully_shaved = abs(open_price - low) < 0.1 and abs(close - high) < 0.1

        if is_bullish_pin:
            results.append({
                "ticker": symbol,
                "name": symbol,
                "marketCap": f"₹{market_cap // 10000000} Cr",
                "pattern": "Bullish Pin Bar"
            })
        elif is_fully_shaved:
            results.append({
                "ticker": symbol,
                "name": symbol,
                "marketCap": f"₹{market_cap // 10000000} Cr",
                "pattern": "Fully Shaved Bar"
            })

    return results
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from nse_utils import download_nse_bhavcopy, filter_equity_stocks, detect_patterns

app = FastAPI()

# Allow your frontend to access this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with ["https://www.liteamc.com"] for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/screener")
def run_screener():
    try:
        df = download_nse_bhavcopy()
        df = filter_equity_stocks(df)
        patterns = detect_patterns(df)
        return patterns
    except Exception as e:
        return {"error": str(e)}
fastapi
uvicorn
pandas
requests
python-multipart
services:
  - type: web
    name: nse-screener-api
    env: python
    buildCommand: ""
    startCommand: uvicorn main:app --host 0.0.0.0 --port 10000
    plan: free
    region: oregon
    runtime: python


