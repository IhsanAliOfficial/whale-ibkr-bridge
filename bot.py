import requests
import time
import os
from dotenv import load_dotenv
from datetime import datetime
import random

# --------------------------------
# Load environment variables
# --------------------------------
load_dotenv()

API_KEY = os.getenv("UNUSUAL_WHALES_API_KEY")
API_URL = "https://api.unusualwhales.com/api/historic_chains"

# === Filter Rules ===
MIN_DAYS_TO_EXPIRY = 30
MIN_AVERAGE_PRICE = 5
MIN_PREMIUM = 100_000
VOLUME_MULTIPLIER = 1.5  # Volume must be > 1.5x open interest

# === Dummy / Dry Run Mode ===
DRY_RUN = os.getenv("DRY_RUN", "true").lower() == "true"

# --------------------------------
# Fetch Alerts Function (Silent Fallback)
# --------------------------------
def fetch_alerts():
    """Fetch recent options alerts from Unusual Whales API or dummy data for testing."""
    headers = {"Authorization": f"Bearer {API_KEY}"}

    try:
        response = requests.get(API_URL, headers=headers, timeout=10)
        if response.status_code == 200:
            data = response.json()
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "chains" in data:
                return data["chains"]
    except Exception:
        pass  # ignore API issues silently

    # --- Dummy Test Data (Fallback) ---
    return [
        {
            "ticker": "TSLA",
            "side": "CALL",
            "strike": 250,
            "expiration": "2025-12-20",
            "average_price": 5.12,
            "premium": 210000,
            "volume": 500,
            "open_interest": 200,
        },
        {
            "ticker": "NVDA",
            "side": "PUT",
            "strike": 400,
            "expiration": "2025-11-15",
            "average_price": 4.8,
            "premium": 150000,
            "volume": 300,
            "open_interest": 150,
        },
        {
            "ticker": "AAPL",
            "side": "CALL",
            "strike": 200,
            "expiration": "2025-10-25",
            "average_price": 2.1,
            "premium": 50000,
            "volume": 100,
            "open_interest": 200,
        },
    ]

# --------------------------------
# Filtering Logic
# --------------------------------
def filter_alerts(alerts):
    valid_alerts = []
    for alert in alerts:
        try:
            expiry = datetime.strptime(alert["expiration"], "%Y-%m-%d")
            days_to_expiry = (expiry - datetime.now()).days
            avg_price = float(alert["average_price"])
            premium = float(alert["premium"])
            volume = float(alert.get("volume", 0))
            open_interest = float(alert.get("open_interest", 1))

            vol_ratio = volume / open_interest if open_interest > 0 else 0

            if (
                days_to_expiry >= MIN_DAYS_TO_EXPIRY
                and avg_price >= MIN_AVERAGE_PRICE
                and premium >= MIN_PREMIUM
                and vol_ratio >= VOLUME_MULTIPLIER
            ):
                alert["days_to_expiry"] = days_to_expiry
                alert["volume_ratio"] = round(vol_ratio, 2)
                valid_alerts.append(alert)
        except Exception:
            continue
    return valid_alerts

# --------------------------------
# Simulated Trade Execution
# --------------------------------
def simulate_trade_execution(trade):
    if DRY_RUN:
        simulated_price = float(trade["average_price"]) * random.uniform(0.95, 1.05)
        pnl = round(random.uniform(-0.1, 0.2) * simulated_price, 2)
        print(
            f"💡 Simulated Trade → {trade['ticker']} | {trade['side']} | Strike {trade['strike']} | "
            f"Exp {trade['expiration']} | Entry ${simulated_price:.2f} | PnL ${pnl}"
        )
    else:
        print(f"🚀 Live Trade Executed for {trade['ticker']} (IBKR API placeholder)")

# --------------------------------
# Main Loop
# --------------------------------
def main():
    print("🔄 Starting Advanced Unusual Whales Alert Scanner...\n")
    print(f"Mode: {'🧪 DRY-RUN TEST' if DRY_RUN else '🚀 LIVE TRADING'}\n")

    while True:
        alerts = fetch_alerts()
        trades = filter_alerts(alerts)

        if trades:
            print(f"\n📊 Found {len(trades)} potential trades:")
            for trade in trades:
                print(
                    f"✅ {trade['ticker']} | {trade['side']} | Strike: {trade['strike']} | "
                    f"Exp: {trade['expiration']} | Premium: ${trade['premium']} | "
                    f"DTE: {trade['days_to_expiry']} | Vol Ratio: {trade['volume_ratio']}"
                )
                simulate_trade_execution(trade)
        else:
            print(f"[{datetime.now().strftime('%H:%M:%S')}] No valid alerts found.")

        time.sleep(60)

# --------------------------------
# Entry Point
# --------------------------------
if __name__ == "__main__":
    main()
