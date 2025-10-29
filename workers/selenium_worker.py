import time
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timezone

FASTAPI_URL = "http://127.0.0.1:8000"
NBK_URL = (
    "https://nationalbank.kz/en/exchangerates/"
    "ezhednevnye-oficialnye-rynochnye-kursy-valyut/"
    "report?beginDate=22.10.2025&endDate=29.10.2025&search-exchanges=&rates%5B%5D=5"
)


def get_site_rates():
    """Fetch exchange rate (e.g., USD) directly from NBK table."""
    response = requests.get(NBK_URL, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", class_="table")

    rates = {}

    if not table:
        print("⚠️ Table not found in the page.")
        return rates

    # Extract table header
    headers = [th.get_text(strip=True) for th in table.select("thead th")]
    if len(headers) >= 3:
        currency_name = headers[2]  # e.g. "US DOLLAR"
    else:
        currency_name = "UNKNOWN"

    # Extract first data row
    first_row = table.select_one("tbody tr")
    if first_row:
        cols = [td.get_text(strip=True) for td in first_row.select("td")]
        if len(cols) >= 3:
            rate_text = cols[2].replace(",", ".")
            try:
                rate = float(rate_text)
                rates["USD"] = rate
            except ValueError:
                print(f"⚠️ Could not parse rate value: {rate_text}")

    print(f"Parsed rates from NBK: {rates}")
    return rates


def get_api_rates():
    """Fetch latest stored rates from FastAPI"""
    try:
        response = requests.get(f"{FASTAPI_URL}/rates")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"⚠️ Error fetching API rates: {e}")
        return []


def compare_and_send_differences(site_rates, api_rates):
    """Compare rates and send differences if > 0.01%, avoid duplicates"""
    processed_pairs = set()

    for api_rate in api_rates:
        base = api_rate["base_currency"]
        target = api_rate["target_currency"]
        rate_api = api_rate["rate"]

        if not rate_api or rate_api <= 0:
            continue

        # We only care about USD–KZT relationship
        if target != "USD" and base != "USD":
            continue

        # Normalize API rate direction
        if base == "USD" and target == "KZT":
            rate_api_kzt_per_usd = rate_api
        elif base == "KZT" and target == "USD":
            rate_api_kzt_per_usd = 1 / rate_api
        else:
            continue

        pair_key = ("USD", "KZT")
        if pair_key in processed_pairs:
            continue  # already sent this pair

        rate_site = site_rates.get("USD")
        if not rate_site:
            continue

        diff_percent = abs(rate_api_kzt_per_usd - rate_site) / rate_site * 100

        if diff_percent < 0.01:
            continue  # ignore very small diffs

        payload = {
            "base_currency": "USD",
            "target_currency": "KZT",
            "rate_api": round(rate_api_kzt_per_usd, 6),
            "rate_site": rate_site,
            "diff_percent": round(diff_percent, 4),
        }

        try:
            r = requests.post(f"{FASTAPI_URL}/differences", json=payload)
            if r.status_code == 200:
                print(f"Sent difference USD→KZT: {diff_percent:.4f}%")
            else:
                print(f"⚠️ Failed to send diff: {r.text}")
        except Exception as e:
            print(f"⚠️ Request failed: {e}")

        processed_pairs.add(pair_key)




def main():
    while True:
        print(f"\n[{datetime.now(timezone.utc).isoformat()}] Starting rate monitor...")
        site_rates = get_site_rates()
        api_rates = get_api_rates()
        
        if site_rates and api_rates:
            compare_and_send_differences(site_rates, api_rates)
        else:
            print("Skipping comparison — missing data.")

        print("Sleeping for 5 minutes...\n")
        time.sleep(300)


if __name__ == "__main__":
    main()
