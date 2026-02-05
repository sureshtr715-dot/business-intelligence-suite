/* ============================================================
   File: views.sql
   Project: Business Intelligence Suite
   Description: Analytical reporting views
   ============================================================ */

USE bi_suite;

/* ============================
   FINANCE VIEWS
   ============================ */

CREATE OR REPLACE VIEW vw_monthly_cashflow AS
SELECT
    d.year_num,
    d.month_num,
    d.yearmonth,
    SUM(CASE WHEN t.txn_type='Income' THEN t.amount ELSE 0 END) AS total_income,
    SUM(CASE WHEN t.txn_type='Expense' THEN ABS(t.amount) ELSE 0 END) AS total_expense,
    SUM(CASE WHEN t.txn_type='Income' THEN t.amount ELSE 0 END) -
    SUM(CASE WHEN t.txn_type='Expense' THEN ABS(t.amount) ELSE 0 END) AS net_cashflow
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
GROUP BY d.year_num, d.month_num, d.yearmonth;

CREATE OR REPLACE VIEW vw_expense_by_category AS
SELECT
    d.yearmonth,
    c.category_name,
    SUM(ABS(t.amount)) AS total_expense
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
JOIN dim_category c ON t.category_id = c.category_id
WHERE t.txn_type='Expense'
GROUP BY d.yearmonth, c.category_name;

CREATE OR REPLACE VIEW vw_income_by_category AS
SELECT
    d.yearmonth,
    c.category_name,
    SUM(t.amount) AS total_income
FROM fact_transactions t
JOIN dim_date d ON t.date_id = d.date_id
JOIN dim_category c ON t.category_id = c.category_id
WHERE t.txn_type='Income'
GROUP BY d.yearmonth, c.category_name;

/* ============================
   SALES VIEWS
   ============================ */

CREATE OR REPLACE VIEW vw_sales_funnel_stage_counts AS
SELECT
    DATE_FORMAT(stage_date,'%Y-%m') AS yearmonth,
    stage,
    COUNT(*) AS lead_count,
    SUM(expected_value) AS total_expected_value,
    SUM(CASE WHEN stage='Closed Won' THEN actual_value ELSE 0 END) AS total_actual_value
FROM fact_sales_funnel
GROUP BY DATE_FORMAT(stage_date,'%Y-%m'), stage;

CREATE OR REPLACE VIEW vw_sales_conversion_summary AS
SELECT
    DATE_FORMAT(stage_date,'%Y-%m') AS yearmonth,
    COUNT(*) AS total_leads,
    SUM(CASE WHEN stage='Qualified' THEN 1 ELSE 0 END) AS qualified,
    SUM(CASE WHEN stage='Proposal' THEN 1 ELSE 0 END) AS proposal,
    SUM(CASE WHEN stage='Closed Won' THEN 1 ELSE 0 END) AS closed_won,
    SUM(CASE WHEN stage='Closed Lost' THEN 1 ELSE 0 END) AS closed_lost
FROM fact_sales_funnel
GROUP BY DATE_FORMAT(stage_date,'%Y-%m');

CREATE OR REPLACE VIEW vw_revenue_by_source AS
SELECT
    source,
    COUNT(*) AS total_leads,
    SUM(CASE WHEN stage='Closed Won' THEN actual_value ELSE 0 END) AS revenue
FROM fact_sales_funnel
GROUP BY source;

CREATE OR REPLACE VIEW vw_sales_rep_performance AS
SELECT
    sales_rep,
    COUNT(*) AS total_leads,
    SUM(CASE WHEN stage='Closed Won' THEN 1 ELSE 0 END) AS won_deals,
    SUM(CASE WHEN stage='Closed Won' THEN actual_value ELSE 0 END) AS revenue
FROM fact_sales_funnel
GROUP BY sales_rep;

/* ============================
   INVENTORY VIEWS
   ============================ */

CREATE OR REPLACE VIEW vw_current_stock AS
SELECT
    p.product_name,
    p.product_category,
    COALESCE(
      SUM(CASE WHEN m.move_type='IN' THEN m.quantity ELSE 0 END) -
      SUM(CASE WHEN m.move_type='OUT' THEN m.quantity ELSE 0 END),
    0) AS current_stock
FROM fact_inventory_moves m
JOIN dim_product p ON m.product_id = p.product_id
GROUP BY p.product_name, p.product_category;

CREATE OR REPLACE VIEW vw_inventory_movement_monthly AS
SELECT
    d.yearmonth,
    p.product_name,
    SUM(CASE WHEN m.move_type='IN' THEN m.quantity ELSE 0 END) AS qty_in,
    SUM(CASE WHEN m.move_type='OUT' THEN m.quantity ELSE 0 END) AS qty_out
FROM fact_inventory_moves m
JOIN dim_date d ON m.date_id = d.date_id
JOIN dim_product p ON m.product_id = p.product_id
GROUP BY d.yearmonth, p.product_name;

CREATE OR REPLACE VIEW vw_dead_stock AS
SELECT
    p.product_name,
    p.product_category,
    MAX(d.full_date) AS last_movement_date,
    SUM(CASE WHEN m.move_type='IN' THEN m.quantity ELSE 0 END) -
    SUM(CASE WHEN m.move_type='OUT' THEN m.quantity ELSE 0 END) AS stock_left
FROM fact_inventory_moves m
JOIN dim_date d ON m.date_id = d.date_id
JOIN dim_product p ON m.product_id = p.product_id
GROUP BY p.product_name, p.product_category
HAVING stock_left > 0
   AND last_movement_date < DATE_SUB(CURDATE(), INTERVAL 30 DAY);
