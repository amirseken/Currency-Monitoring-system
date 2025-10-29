# workers/api_worker.py
import requests
from datetime import datetime, UTC
import time

API_URLS = [
    "https://open.er-api.com/v6/latest/KZT",
    "https://open.er-api.com/v6/latest/USD"
]
FASTAPI_URL = "http://127.0.0.1:8000/rates"

while True:
    for url in API_URLS:
        try:
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            payload = {
                "base_code": data["base_code"],  # must match FastAPI
                "rates": data["rates"]
            }

            timestamp = datetime.now(UTC).isoformat()
            print(f"[{timestamp}] Successfully fetched {data['base_code']} rates.")

            res = requests.post(FASTAPI_URL, json=payload)
            if res.status_code == 200:
                print(f"Sent {data['base_code']} rates successfully.")
            else:
                print(f"Failed to send rates: {res.status_code} - {res.text}")

        except Exception as e:
            print(f"Error fetching from {url}: {e}")

    print("Sleeping for 5 minutes...")
    time.sleep(300)
