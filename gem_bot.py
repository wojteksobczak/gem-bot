import yfinance as yf
import datetime
import os
import requests

tickers = [
    "CSNDX.L",   # Nasdaq 100
    "EIMI.L",    # MSCI EM IMI
    "IWDA.AS"    # MSCI World
]

bond_fallback = [
    "CSBGU0.L",  # Obligacje 7-10Y
    "IB01.L"     # Obligacje 0-1Y
]
today = datetime.datetime.today()
one_month_ago = today - datetime.timedelta(days=30)
twelve_months_ago = today - datetime.timedelta(days=365)

def get_momentum(ticker):
    try:
        data = yf.download(
            ticker,
            start=twelve_months_ago,
            end=one_month_ago,
            auto_adjust=True,
            progress=False
        )

        if data.empty or len(data) < 2:
            print(f"Brak danych dla {ticker}")
            return None

        start_price = float(data["Close"].iloc[0])
        end_price = float(data["Close"].iloc[-1])

        return (end_price / start_price) - 1

    except Exception as e:
        print(f"Błąd dla {ticker}: {e}")
        return None


results = {}

for t in tickers:
    mom = get_momentum(t)
    if mom is not None:
        results[t] = mom

if not results:
    print("Brak poprawnych danych.")
    exit()

best = max(results, key=results.get)

if results[best] > 0:
    decision = best
else:
    decision = bond_fallback

message = f"Decyzja GEM – {today.strftime('%d.%m.%Y')}\n\n"

for k, v in results.items():
    message += f"{k}: {round(v*100,2)}%\n"

message += f"\nRekomendacja: {decision}"

TELEGRAM_TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]

url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
payload = {"chat_id": CHAT_ID, "text": message}

requests.post(url, data=payload)
