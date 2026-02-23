import yfinance as yf
import datetime
import os
import requests

tickers = ["IWDA.AS", "EIMI.L", "CSNDX.L"]
bond_fallback = "IB01.L"

today = datetime.datetime.today()
one_month_ago = today - datetime.timedelta(days=30)
twelve_months_ago = today - datetime.timedelta(days=365)

def get_momentum(ticker):
    data = yf.download(ticker, start=twelve_months_ago, end=one_month_ago)
    if len(data) < 2:
        return None
    start_price = data["Adj Close"].iloc[0]
    end_price = data["Adj Close"].iloc[-1]
    return (end_price / start_price) - 1

results = {}
for t in tickers:
    mom = get_momentum(t)
    if mom is not None:
        results[t] = mom

decision = bond_fallback
if results:
    best = max(results, key=results.get)
    if results[best] > 0:
        decision = best

message = "Decyzja GEM – {}\n\n".format(today.strftime("%d.%m.%Y"))
for k, v in results.items():
    message += f"{k}: {round(v*100,2)}%\n"
message += f"\nRekomendacja: {decision}"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message}
requests.post(url, data=payload)
