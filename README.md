# MTN Mobile Money Transaction Analytics
A Full-Stack Financial Data Processing System

## 📋 Overview
This project ingests MoMo SMS data (XML), parses and categorizes transactions, loads them into a SQLite database, and serves an interactive dashboard (Chart.js) via a FastAPI backend that also exposes JSON APIs.

## 👥 Team
Team 21 
Member 1: Premier Ufitinema
Member 2: KAGABA SHIMWA Elvis
Member 3: Colombe Nyituriki Igihozo

## 🏗️ System Architecture
**High-Level System Architecture Diagram:**
🔗 https://drive.google.com/file/d/1vcEXmbKvywyNi8HfH-Zil79VfWpfHRtc/view?usp=sharing


## 📋 Project Management
**Scrum Board:**
link here


## 🚀 Features
- ETL pipeline from XML SMS exports to SQLite
- Automatic transaction typing (CASH_IN, CASH_OUT, OTHER) and category tagging
- FastAPI backend with JSON endpoints and static file serving
- Interactive dashboard (Chart.js) with filters and pagination
- Persistent logging and dead-letter queue for unparsable messages

## 💻 Tech Stack
- Backend: Python 3, FastAPI, Uvicorn, SQLite, SQLAlchemy (for compatibility), Pandas, xmltodict
- Frontend: HTML, CSS, JavaScript, Chart.js
- Testing: pytest, pytest-cov

## 📁 Project Structure
```
.
├── README.md                         # Setup, run, overview
├── .env.example                      # DATABASE_URL or path to SQLite
├── requirements.txt                  # lxml/ElementTree, dateutil, (FastAPI optional)
├── index.html                        # Dashboard entry (static)
├── start_server.py                   # Convenience launcher for FastAPI
├── web/
│   ├── styles.css                    # Dashboard styling
│   ├── chart_handler.js              # Fetch + render charts/tables
│   ├── app.js                        # Frontend application logic
│   └── assets/                       # Images/icons (optional)
├── data/
│   ├── raw/                          # Provided XML input (git-ignored)
│   │   └── momo.xml
│   ├── processed/                    # Cleaned/derived outputs for frontend
│   │   ├── dashboard.json            # Aggregates the dashboard reads
│   │   └── transactions.db           # SQLite DB file
│   └── logs/
│       ├── etl.log                   # Structured ETL logs
│       └── dead_letter/              # Unparsed/ignored XML snippets
├── etl/
│   ├── __init__.py
│   ├── config.py                     # File paths, thresholds, categories
│   ├── parse_xml.py                  # XML parsing (ElementTree/lxml)
│   ├── clean_normalize.py            # Amounts, dates, phone normalization
│   ├── categorize.py                 # Simple rules for transaction types
│   ├── load_db.py                    # Create tables + upsert to SQLite
│   ├── run.py                        # CLI: parse -> clean -> categorize -> load -> export JSON
│   └── sms_processor.py              # Legacy monolithic processor (kept for compatibility)
├── api/                              # Optional (bonus)
│   ├── __init__.py
│   ├── app.py                        # FastAPI with /transactions, /analytics
│   ├── db.py                         # SQLite connection helpers
│   └── schemas.py                    # Pydantic response models
├── scripts/
│   ├── run_etl.sh/.ps1               # python -m etl.run --xml data/raw/momo.xml
│   ├── export_json.sh/.ps1           # Rebuild data/processed/dashboard.json
│   ├── serve_frontend.sh/.ps1        # python -m uvicorn api.app:app or http.server
│   ├── run.py                        # Run ETL then API (or API only)
│   ├── run_tests.py
│   ├── generate_sample_data.py
│   └── init_project.py
└── tests/
    ├── test_parse_xml.py             # Small unit tests
    ├── test_clean_normalize.py
    ├── test_categorize.py
    ├── test_api.py
    └── test_etl.py
```

## ⚙️ Setup
PowerShell (Windows):

```powershell
# 1) (Recommended) Create and activate a virtual environment
python -m venv .venv
. .venv\Scripts\Activate.ps1

# 2) Install dependencies
pip install -r requirements.txt

# 3) Optional: set environment variables
$env:DATABASE_URL = "data/processed/transactions.db"  # or sqlite:///absolute/path.db
$env:XML_INPUT_PATH = "data/raw/momo.xml"
```

Bash (macOS/Linux):

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DATABASE_URL="data/processed/transactions.db"
export XML_INPUT_PATH="data/raw/momo.xml"
```

## 🏃 Run
Option A: One-shot runner (ETL then API)

```powershell
python -m scripts.run            # Runs ETL then starts API on port 8000
python -m scripts.run --skip-etl # Start API only
python -m scripts.run --port 8080
```

Option B: Manual

```powershell
# 1) Run ETL (reads $env:XML_INPUT_PATH, writes to $env:DATABASE_URL)
python - <<'PY'
from etl.sms_processor import MomoSmsProcessor
import os
xml = os.environ.get('XML_INPUT_PATH', 'data/raw/momo.xml')
db  = os.environ.get('DATABASE_URL', 'data/processed/transactions.db').replace('sqlite:///','')
MomoSmsProcessor(xml, db).process()
PY

# 2) Start API
python -m uvicorn api.app:app --reload --host 127.0.0.1 --port 8000

# 3) Open http://127.0.0.1:8000
```

Option C: Convenience launcher

```powershell
python start_server.py
```

Notes
- FastAPI auto docs: http://127.0.0.1:8000/docs and /redoc
- Static assets are served at /web and processed data at /data

## 🌐 API Summary (from api/app.py)
- GET / → serves index.html
- GET /api/ → {"message":"MoMo Data Analysis API"}
- GET /api/transactions
  - Query: limit, offset, type, category, date_from, date_to, search
  - Returns list of transactions
- GET /api/transactions/{id}
- GET /api/stats → key/value stats from stats table
- GET /api/dashboard → { transactions, stats, generated_at }
- GET /api/categories → category aggregates
- GET /api/types → type aggregates
- GET /api/trends/monthly?months=12 → monthly aggregates
- GET /api/dashboard.json → returns data/processed/dashboard.json

## 🧩 ETL Details (etl/sms_processor.py)
- Input: XML SMS export at $XML_INPUT_PATH (default data/raw/momo.xml)
- Detection: Identifies likely MoMo messages by keywords
- Extraction: Parses timestamps, amounts (RWF patterns), phone/reference when present
- Typing: Maps to CASH_IN / CASH_OUT / OTHER based on keywords
- Categorization: Heuristics over description (bills, shopping, food, transport, etc.)
- Output:
  - SQLite at $DATABASE_URL (default data/processed/transactions.db)
  - Precomputed dashboard JSON at data/processed/dashboard.json
  - Logs at data/logs/etl.log; unparsable messages to data/logs/dead_letter/

Environment variables
- DATABASE_URL: SQLite path (sqlite:/// optional prefix). Example: data/processed/transactions.db
- XML_INPUT_PATH: Path to input XML. Example: data/raw/momo.xml

## 🧪 Tests
```powershell
# Via pytest
pytest

# Or helper script
python -m scripts.run_tests
```

## 📚 Dependencies (requirements.txt)
- fastapi, uvicorn, pydantic
- lxml, xmltodict, python-dateutil
- pandas, numpy, matplotlib
- sqlalchemy
- pytest, pytest-cov

## ❗ Notes and Tips
- If transactions.db doesn’t exist, the API will create the folder and connect; run the ETL first for data.
- The frontend fetches dashboard data from /data/processed/dashboard.json; ensure the ETL has generated it.
- On Windows PowerShell, use $env:VAR to set environment variables for the current session.

