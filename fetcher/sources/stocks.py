# fetcher/sources/stocks.py

import yfinance as yf
from config import STOCK_TICKERS

def fetch_stocks():
    results = []

    for item in STOCK_TICKERS:
        ticker = item["ticker"]
        label  = item["label"]
        try:
            t    = yf.Ticker(ticker)
            info = t.fast_info

            price  = round(info.last_price, 2)
            prev   = round(info.previous_close, 2)
            change = round(price - prev, 2)
            pct    = round((change / prev) * 100, 1)

            results.append({
                "ticker": label,
                "price":  str(price),
                "change": change,
                "pct":    str(abs(pct)),
            })

        except Exception as e:
            print(f"  stocks: failed for {ticker}: {e}")
            results.append({
                "ticker": label,
                "price":  "---",
                "change": 0,
                "pct":    "0.0",
            })

    return results