/* ============================================================
   File: schema.sql
   Project: Business Intelligence Suite
   Description: Star schema warehouse tables
   ============================================================ */

CREATE DATABASE IF NOT EXISTS bi_suite;
USE bi_suite;

/* ============================
   DIMENSION TABLES
   ============================ */

-- Date Dimension

CREATE TABLE IF NOT EXISTS dim_date (
  date_id INT AUTO_INCREMENT PRIMARY KEY,
  full_date DATE NOT NULL,
  year_num SMALLINT NOT NULL,
  month_num TINYINT NOT NULL,
  day_num TINYINT NOT NULL,
  month_name VARCHAR(20) NOT NULL,
  yearmonth CHAR(7) NOT NULL,
  UNIQUE KEY uq_full_date (full_date)
);

-- Category Dimension

CREATE TABLE IF NOT EXISTS dim_category (
  category_id INT AUTO_INCREMENT PRIMARY KEY,
  category_name VARCHAR(100) NOT NULL,
  category_type ENUM('Income','Expense') NOT NULL,
  UNIQUE KEY uq_category_name (category_name)
);

-- Account Dimension

CREATE TABLE IF NOT EXISTS dim_vendor (
  vendor_id INT AUTO_INCREMENT PRIMARY KEY,
  vendor_name VARCHAR(150) NOT NULL,
  UNIQUE KEY uq_vendor_name (vendor_name)
);

-- Vendor Dimension

CREATE TABLE IF NOT EXISTS dim_account (
  account_id INT AUTO_INCREMENT PRIMARY KEY,
  account_name VARCHAR(100) NOT NULL,
  account_type VARCHAR(50),
  UNIQUE KEY uq_account_name (account_name)
);

-- Customer Dimension

CREATE TABLE IF NOT EXISTS dim_customer (
  customer_id INT AUTO_INCREMENT PRIMARY KEY,
  customer_name VARCHAR(150) NOT NULL,
  region VARCHAR(100),
  customer_type VARCHAR(50)
);

-- Product Dimension

CREATE TABLE IF NOT EXISTS dim_product (
  product_id INT AUTO_INCREMENT PRIMARY KEY,
  product_name VARCHAR(150) NOT NULL,
  product_category VARCHAR(100),
  unit_price DECIMAL(12,2)
);

/* ============================
   FACT TABLES
   ============================ */


-- Transactions Fact

CREATE TABLE IF NOT EXISTS fact_transactions (
  txn_id VARCHAR(30) PRIMARY KEY,
  date_id INT NOT NULL,
  account_id INT,
  category_id INT,
  vendor_id INT,
  description VARCHAR(255),
  amount DECIMAL(12,2) NOT NULL,
  txn_type ENUM('Income','Expense') NOT NULL,
  payment_method VARCHAR(50),
  is_recurring BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_txn_date FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
  CONSTRAINT fk_txn_account FOREIGN KEY (account_id) REFERENCES dim_account(account_id),
  CONSTRAINT fk_txn_category FOREIGN KEY (category_id) REFERENCES dim_category(category_id),
  CONSTRAINT fk_txn_vendor FOREIGN KEY (vendor_id) REFERENCES dim_vendor(vendor_id)
);

-- Sales Funnel Fact

CREATE TABLE IF NOT EXISTS fact_sales_funnel (
  lead_id VARCHAR(30) PRIMARY KEY,
  customer_id INT,
  source VARCHAR(100),
  stage ENUM('Lead','Qualified','Proposal','Closed Won','Closed Lost') NOT NULL,
  stage_date DATE NOT NULL,
  expected_value DECIMAL(12,2),
  actual_value DECIMAL(12,2),
  sales_rep VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_sales_customer FOREIGN KEY (customer_id)
    REFERENCES dim_customer(customer_id)
);

-- Inventory Movement Fact

CREATE TABLE IF NOT EXISTS fact_inventory_moves (
  move_id VARCHAR(30) PRIMARY KEY,
  product_id INT NOT NULL,
  date_id INT NOT NULL,
  quantity INT NOT NULL,
  move_type ENUM('IN','OUT') NOT NULL,
  unit_price DECIMAL(12,2),
  warehouse VARCHAR(100),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

  CONSTRAINT fk_inv_product FOREIGN KEY (product_id)
    REFERENCES dim_product(product_id),
  CONSTRAINT fk_inv_date FOREIGN KEY (date_id)
    REFERENCES dim_date(date_id)
);

/* ============================
   INDEXES
   ============================ */

CREATE INDEX idx_txn_date ON fact_transactions(date_id);
CREATE INDEX idx_txn_category ON fact_transactions(category_id);

CREATE INDEX idx_sales_stage_date ON fact_sales_funnel(stage_date);
CREATE INDEX idx_sales_stage ON fact_sales_funnel(stage);

CREATE INDEX idx_inv_date ON fact_inventory_moves(date_id);
CREATE INDEX idx_inv_product ON fact_inventory_moves(product_id);
