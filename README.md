

---

# 💱 Currency Rate Monitor — FastAPI + Selenium + PostgreSQL

### 🧠 Goal

This project is a mini system for monitoring and comparing currency exchange rates from two sources:

1. **Open API** — [https://open.er-api.com](https://open.er-api.com)
2. **National Bank of Kazakhstan (NBK)** — [https://nationalbank.kz](https://nationalbank.kz)

If a rate difference between the two sources exceeds **0.01%**, it is recorded in the database.

---

## ⚙️ System Architecture

The system consists of **three components**:

### **1️⃣ FastAPI Application**

Serves as the backend system that receives, stores, and provides currency data.

**Endpoints:**

| Endpoint       | Method | Description                                                   |
| -------------- | ------ | ------------------------------------------------------------- |
| `/rates`       | `POST` | Receive and store currency rates from the API worker          |
| `/rates`       | `GET`  | Retrieve the latest stored rates                              |
| `/differences` | `POST` | Receive and store rate discrepancies found by Selenium worker |
| `/differences` | `GET`  | Retrieve logged rate differences                              |

**Files:**

* `main.py` — initializes FastAPI, registers routes
* `database.py` — configures PostgreSQL using SQLAlchemy
* `models.py` — defines tables (`Rate`, `Difference`)
* `routes/rates.py` — logic for `/rates` endpoints
* `routes/differences.py` — logic for `/differences` endpoints
* `config.py` — loads environment variables for database connection

Example snippet:

```python
from fastapi import FastAPI
from app.database import Base, engine
from app.routes import rates, differences

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Currency Monitor")

app.include_router(rates.router)
app.include_router(differences.router)
```

---

### **2️⃣ API Worker (Script Worker)**

Fetches real-time exchange rates from open APIs and sends them to FastAPI.

**Source examples:**

* `https://open.er-api.com/v6/latest/KZT`
* `https://open.er-api.com/v6/latest/USD`

**Workflow:**

1. Fetch latest rates (e.g., USD→KZT, AED→KZT).
2. Format data into JSON.
3. Send via `POST /rates` to FastAPI.
4. Run periodically (e.g., every 5 minutes via scheduler or cron).

---

### **3️⃣ Selenium Worker**

Uses Selenium to fetch official rates from the **NBK website** and compare them with API data.

**Workflow:**

1. Opens [https://nationalbank.kz](https://nationalbank.kz) with Selenium.
2. Extracts official rate for USD (e.g., `538.56`).
3. Sends `GET /rates` request to FastAPI to retrieve stored API rates.
4. Compares both values:

   * If difference > `0.01%`, sends the result via `POST /differences`.
5. Logs all operations in the console.

**Example log output:**

```
✅ Parsed rates from NBK: {'USD': 538.56}
✅ API rates fetched: [{'USD→KZT': 533.2}]
✅ Difference sent for USD→KZT: 0.81%
```

---

## 🧩 Technologies Used

* **Python 3.10+**
* **FastAPI** — web framework for REST API
* **PostgreSQL** — relational database
* **SQLAlchemy** — ORM for database models
* **Selenium** — web automation for NBK site
* **Requests** — API data fetching
* **dotenv** — environment configuration

---

## 📁 Project Structure

```
fastapi_currency_monitor/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── config.py
│   └── routes/
│       ├── rates.py
│       └── differences.py
│
├── worker_api.py         # Fetches and sends API rates
├── worker_selenium.py    # Parses NBK site, compares, logs differences
├── requirements.txt
└── .env
```

---

## ⚡ How to Run

1. **Set up database**

   ```bash
   createdb currency_db
   ```

2. **Configure environment (.env)**

   ```bash
   DATABASE_URL=postgresql://user:password@localhost:5432/currency_db
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run FastAPI app**

   ```bash
   uvicorn app.main:app --reload
   ```

5. **Start workers**

   ```bash
   python worker_api.py
   python worker_selenium.py
   ```

---

## ✅ Example Results

```
[2025-10-29T13:31:10.182564+00:00] Starting rate monitor...
✅ Parsed rates from NBK: {'USD': 538.56}
✅ Difference sent for USD→KZT: 0.8118%
✅ Difference sent for USD→KZT: 0.9028%
```

---

## 🧠 Summary

This project demonstrates:

* REST API design using FastAPI
* Background data ingestion and validation
* Selenium-based real-time web scraping
* Database persistence and change detection

It automates the **comparison of financial data from multiple sources** and provides a simple foundation for extending into more robust monitoring or alerting systems.

