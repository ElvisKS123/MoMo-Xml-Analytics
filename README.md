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
Team name: Group 20

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


## 📊 ERD for MOMO XML Analytics database documentation

ERD for the MoMo SMS database system is designed around three central entities: Users, Transactions, and System_Logs. The Users table serves as the foundation for capturing customer information. It includes a unique identifier (User_id), personal details such as first name and last name, a phone number, and a category field indicating whether the user is acting as a sender or a receiver. To establish a link between users and their financial activities, a foreign key referencing the transaction identifier is included in the Users table. The Transactions table records the details of mobile money operations. Each transaction is uniquely identified by a Transaction_id and includes attributes such as the amount involved, the type of transaction (e.g., deposit, withdrawal, transfer, or payment), and a timestamp to capture when the transaction occurred. This table forms the core of the system, ensuring that all financial activity is systematically recorded and easily traceable. The System_Logs table ensures that every interaction is monitored and accounted for. Each log entry has a unique identifier (System_log_id) and records the status of the process, whether it was a success, error, or warning. The table also contains a foreign key linking it to the Users table, enabling administrators to track which user’s activity generated the log. In this design, the relationships are modeled as one-to-one: a user is tied to a single transaction, and each user can have a corresponding log entry. While this approach simplifies the structure, it creates a tightly coupled model that clearly demonstrates direct links between users, their transactions, and the system’s monitoring activities.
