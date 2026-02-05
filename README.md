## 📊 Business Intelligence Suite (Finance, Sales & Inventory Analytics)

[![Status](https://img.shields.io/badge/status-completed%20%7C%20Python%20%7C%20SQL%20%7C%20MySQL%20%7C%20Power%20BI-brightgreen.svg)]()

An end-to-end Business Intelligence system built using Python, MySQL, and Power BI.  
This project demonstrates real-world ETL pipelines, data warehouse design, SQL analytics, and interactive dashboards.

---

## 📌 Project Overview

The Business Intelligence Suite helps organizations:

- Monitor cash flow and profitability  
- Track sales funnel performance and conversion rates  
- Optimize inventory and identify dead stock  

Data flows from raw Excel files → Python ETL → MySQL Data Warehouse → SQL Views → Power BI Dashboards.

---

## 🏗 Architecture

Raw Excel Files  
↓  
Python ETL (Pandas)  
↓  
MySQL Data Warehouse  
↓  
SQL Views  
↓  
Power BI Dashboards  

---

## 🛠 Tech Stack

- Python (Pandas, SQLAlchemy)  
- MySQL  
- Power BI  
- Git & GitHub  

---

## 📊 Dashboards

### Finance Dashboard
![Finance Dashboard](screenshorts\01_finance_dashboard.png)

### Sales Funnel Dashboard
![Sales Funnel Dashboard](screenshots/02_sales_dashboard.png)

### Inventory Optimization Dashboard
![Inventory Dashboard](screenshots/03_inventory_dashboard.png)

### Data Model
![Data Model](screenshots/04_data_model.png)

---

## 🔁 ETL Pipeline

1. Read raw Excel files  
2. Clean and standardize data using Pandas  
3. Load dimension and fact tables into MySQL  
4. Create analytical SQL views  
5. Connect Power BI to MySQL  

---

## 🧱 Data Warehouse Design

### Dimensions
- dim_date  
- dim_category  
- dim_account  
- dim_vendor  
- dim_customer  
- dim_product  

### Facts
- fact_transactions  
- fact_sales_funnel  
- fact_inventory_moves  

Star schema design.

---

## 📈 SQL Views

- vw_monthly_cashflow  
- vw_expense_by_category  
- vw_income_by_category  
- vw_sales_conversion_summary  
- vw_revenue_by_source  
- vw_sales_rep_performance  
- vw_current_stock  
- vw_inventory_movement_monthly  
- vw_dead_stock  

All SQL logic is available inside:sql/views.sql

---

## ▶ How to Run

### 1) Create Database and Tables
```bash
 Run inside MySQL Workbench:
-sql/schema.sql
-sql/views.sql
```

### 2) Create Virtual Environment
```bash
-python -m venv venv
-venv\Scripts\activate
-pip install pandas sqlalchemy pymysql
```

### 3) Run ETL
```dash
-python etl/01_clean_transactions.py
-python etl/02_clean_sales.py
-python etl/03_clean_inventory.py
-python etl/04_load_to_mysql.py
```

### 4) Open Power BI

Open: powerbi/bi_suite.pbix


---

## 📊 Business Insights

### Finance
- Monthly net cash flow  
- Profit margin %  
- Top expense categories  

### Sales
- Win rate  
- Funnel stage conversion  
- Revenue by source and sales rep  

### Inventory
- Current stock by product  
- Dead stock detection  
- Stock in vs stock out  

---

## 👤 Author

Suresh Kumar  







