## MoMo Xml Analytics

## 📝 Project Description

This project is an enterprise-level fullstack application that processes MoMo SMS data in XML format, cleans and categorizes transactions, stores them in a relational database (SQLite), and provides a frontend dashboard to analyze and visualize the data.

The system will include:

ETL pipeline (extract, clean, normalize, categorize)

SQLite database for storage

JSON exports for the dashboard

Frontend interface (charts + tables)

Through this project, we will demonstrate our team’s capacity to process and structure raw data, build reliable database systems, and create meaningful visualizations for end users.

## 📋 Overview
Team name: Group 21

Member 1: Premier Ufitinema

Member 2: KAGABA SHIMWA Elvis

Member 3: Marie Colombe Nyituriki Igihozo

## 🏗️ System Architecture
**High-Level System Architecture Diagram:**
🔗  https://drive.google.com/file/d/1GXHjN_hVkewKzGfN6XbdUWU-j5IL22Kf/view?usp=sharing

## 📋 Project Management
**Scrum Board:**
(https://alustudent-team-vshx4yzr.atlassian.net/jira/core/projects/MMMTA/list?direction=ASC&sortBy=key&atlOrigin=eyJpIjoiOWQwMzgzMWJhZTU3NDdiY2FkMmEwYTFhOWQ1NWZjYjgiLCJwIjoiaiJ9)

## Project organization
├── README.md                     
├── .env.example                     
├── requirements.txt                  
├── index.html                      
├── web/
│   ├── styles.css                
│   ├── chart_handler.js             
│   └── assets/                     
├── data/
│   ├── raw/                          
│   │   └── momo.xml
│   ├── processed/                   
│   │   └── dashboard.json           
│   ├── db.sqlite3                  
│   └── logs/
│       ├── etl.log                 
│       └── dead_letter/            
├── etl/
│   ├── __init__.py
│   ├── config.py                    
│   ├── parse_xml.py                 
│   ├── clean_normalize.py           
│   ├── categorize.py                
│   ├── load_db.py                 
│   └── run.py                     
├── api/                              
│   ├── __init__.py
│   ├── app.py                        
│   ├── db.py                         
│   └── schemas.py                  
├── scripts/
│   ├── run_etl.sh                    
│   ├── export_json.sh                
│   └── serve_frontend.sh             
└── tests/
    ├── test_parse_xml.py             
    ├── test_clean_normalize.py
    └── test_categorize.py
