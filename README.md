# MTN Mobile Money Transaction Analytics

## 📋 Overview
Team name:Team Syntax

## 👥 Team 21 
Member 1: Premier Ufitinema

Member 2: KAGABA SHIMWA Elvis

Member 3: Marie Colombe Nyituriki Igihozo

## 🏗️ System Architecture
**High-Level System Architecture Diagram:**
🔗  https://drive.google.com/file/d/1GXHjN_hVkewKzGfN6XbdUWU-j5IL22Kf/view?usp=sharing


## 📋 Project Management
**Scrum Board:**
(https://alustudent-team-vshx4yzr.atlassian.net/jira/core/projects/MMMTA/list?direction=ASC&sortBy=key&atlOrigin=eyJpIjoiOWQwMzgzMWJhZTU3NDdiY2FkMmEwYTFhOWQ1NWZjYjgiLCJwIjoiaiJ9)
#

## 📁 Project Structure
.
├── README.md                         # This file - setup, run, overview
├── .env.example                      # Environment configuration template
├── requirements.txt                  # Python dependencies
├── index.html                        # Main dashboard entry point
├── web/
│   ├── styles.css                    # Dashboard styling
│   ├── chart_handler.js              # Chart rendering and data fetching
│   └── assets/                       # Images and icons
├── data/
│   ├── raw/                          # Input XML files (git-ignored)
│   │   └── momo.xml
│   ├── processed/                    # Cleaned outputs for frontend
│   │   └── dashboard.json
│   ├── db.sqlite3                    # SQLite database
│   └── logs/
│       ├── etl.log                   # ETL process logs
│       └── dead_letter/              # Unparsed XML snippets
├── etl/
│   ├── config.py                     # Configuration and thresholds
│   ├── parse_xml.py                  # XML parsing logic
│   ├── clean_normalize.py            # Data cleaning and normalization
│   ├── categorize.py                 # Transaction categorization
│   ├── load_db.py                    # Database operations
│   └── run.py                        # Main ETL orchestrator
├── api/                              # Optional FastAPI backend
│   ├── app.py                        # API endpoints
│   ├── db.py                         # Database connections
│   └── schemas.py                    # Data models
├── scripts/
│   ├── run_etl.sh                    # ETL execution script
│   ├── export_json.sh                # Data export script
│   └── serve_frontend.sh             # Frontend server script
└── tests/
    ├── test_parse_xml.py             # XML parsing tests
    ├── test_clean_normalize.py       # Data cleaning tests
    └── test_categorize.py            # Categorization tests
