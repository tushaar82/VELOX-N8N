import json
import os
import time
import random
import pandas as pd
from curl_cffi import requests
from playwright.sync_api import sync_playwright


# ===============================
# Load input symbols.json
# ===============================
with open("symbols.json", "r", encoding="utf-8") as f:
    symbols_data = json.load(f)

os.makedirs("optionchains", exist_ok=True)


# ===============================
# curl_cffi fetcher
# ===============================
def fetch_with_curl(symbol, expiry, market_type):
    url = f"https://www.nseindia.com/api/option-chain-v3?type={market_type}&symbol={symbol}&expiry={expiry}"
    base_url = "https://www.nseindia.com/option-chain"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36",
        "Referer": "https://www.nseindia.com/option-chain",
        "Accept": "application/json,text/html;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Connection": "keep-alive"
    }

    s = requests.Session()
    s.headers.update(headers)

    try:
        s.get(base_url, impersonate="chrome120", timeout=15)  # homepage for cookies
        time.sleep(random.uniform(1, 3))  # slight wait

        resp = s.get(url, impersonate="chrome120", timeout=15)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("records", {}).get("data"):
                return data
        return None
    except Exception as e:
        print(f"⚠️ curl_cffi error for {symbol}: {e}")
        return None


# ===============================
# Playwright fetcher
# ===============================
def fetch_with_playwright(symbol, expiry, market_type):
    url = f"https://www.nseindia.com/api/option-chain-v3?type={market_type}&symbol={symbol}&expiry={expiry}"
    data = None

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True,
                                    args=["--disable-blink-features=AutomationControlled",
                                          "--disable-dev-shm-usage", "--no-sandbox"])
        context = browser.new_context(user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/120.0.0.0 Safari/537.36"
        ))

        req = context.request
        req.get("https://www.nseindia.com/option-chain")  # homepage for cookies

        resp = req.get(url)
        if resp.ok:
            data = resp.json()

        browser.close()

    return data


# ===============================
# Main loop
# ===============================
for entry in symbols_data:
    symbol = entry.get("symbol")
    expiry = entry.get("expiry")
    market_type = entry.get("type")

    if not symbol or not expiry or not market_type:
        print(f"⚠️ Skipping invalid entry: {entry}")
        continue

    print(f"\n🔄 Fetching {symbol} ({market_type}, expiry {expiry})...")

    # Try curl_cffi first
    data = fetch_with_curl(symbol, expiry, market_type)

    # If curl fails, fallback to Playwright
    if not data:
        print(f"⚠️ curl_cffi failed for {symbol}, retrying with Playwright...")
        data = fetch_with_playwright(symbol, expiry, market_type)

    if data and data.get("records", {}).get("data"):
        outfile = os.path.join("optionchains", f"{symbol}.json")
        with open(outfile, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)

        print(f"✅ Saved {symbol} -> {outfile}")

        # Save CSV
        records = []
        for item in data.get("records", {}).get("data", []):
            ce, pe = item.get("CE", {}), item.get("PE", {})
            records.append({
                "strikePrice": item.get("strikePrice"),
                "expiryDate": item.get("expiryDate"),
                "CE_OI": ce.get("openInterest"),
                "CE_LTP": ce.get("lastPrice"),
                "CE_IV": ce.get("impliedVolatility"),
                "PE_OI": pe.get("openInterest"),
                "PE_LTP": pe.get("lastPrice"),
                "PE_IV": pe.get("impliedVolatility"),
            })

        if records:
            df = pd.DataFrame(records).sort_values("strikePrice")
            df.to_csv(os.path.join("optionchains", f"{symbol}.csv"), index=False)
            print(f"📊 Saved {symbol} -> CSV")
    else:
        print(f"❌ Failed to fetch {symbol} from both methods")

    # 🔹 Random natural delay (2–6s)
    delay = random.uniform(2, 6)
    print(f"⏳ Waiting {delay:.2f} seconds before next request...")
    time.sleep(delay)
