"""
File: 04_load_to_mysql.py
Purpose: Load cleaned CSV files into MySQL warehouse tables
"""

import pandas as pd
import numpy as np
from sqlalchemy import text
from db_connection import get_engine
import os

TXN_FILE = "data/processed/transactions_clean.csv"
SALES_FILE = "data/processed/sales_clean.csv"
INV_FILE = "data/processed/inventory_clean.csv"


# --------------------------
# Utility
# --------------------------

def mysql_safe_row_dict(row_dict: dict):
    """Convert NaN/NaT to None for MySQL"""
    clean = {}
    for k, v in row_dict.items():
        if v is None:
            clean[k] = None
        elif isinstance(v, float) and np.isnan(v):
            clean[k] = None
        else:
            clean[k] = v
    return clean


# --------------------------
# Dimension Helpers
# --------------------------

def ensure_dim_date(engine, df_dates):
    df_dates = df_dates.dropna().drop_duplicates()
    df_dates = pd.to_datetime(df_dates, errors="coerce").dropna()
    df_dates = pd.DataFrame({"full_date": df_dates.dt.date})

    df_dates["year_num"] = pd.to_datetime(df_dates["full_date"]).dt.year
    df_dates["month_num"] = pd.to_datetime(df_dates["full_date"]).dt.month
    df_dates["day_num"] = pd.to_datetime(df_dates["full_date"]).dt.day
    df_dates["month_name"] = pd.to_datetime(df_dates["full_date"]).dt.strftime("%B")
    df_dates["yearmonth"] = pd.to_datetime(df_dates["full_date"]).dt.strftime("%Y-%m")

    with engine.begin() as conn:
        for _, row in df_dates.iterrows():
            conn.execute(text("""
                INSERT IGNORE INTO dim_date
                (full_date, year_num, month_num, day_num, month_name, yearmonth)
                VALUES (:full_date, :year_num, :month_num, :day_num, :month_name, :yearmonth)
            """), row.to_dict())

    mapping = pd.read_sql("SELECT date_id, full_date FROM dim_date", engine)
    mapping["full_date"] = pd.to_datetime(mapping["full_date"]).dt.date
    return dict(zip(mapping["full_date"], mapping["date_id"]))


def ensure_dim_simple(engine, table, key_col, values):
    values = pd.Series(values).dropna().drop_duplicates()

    with engine.begin() as conn:
        for v in values:
            conn.execute(text(f"""
                INSERT IGNORE INTO {table}({key_col})
                VALUES (:val)
            """), {"val": v})

    id_col = table.replace("dim_", "") + "_id"
    df_map = pd.read_sql(f"SELECT {id_col}, {key_col} FROM {table}", engine)
    return dict(zip(df_map[key_col], df_map[id_col]))


def ensure_dim_category(engine, df):
    cat_df = df[["category", "type"]].dropna().drop_duplicates()
    cat_df["type"] = cat_df["type"].str.lower().map(
        {"income": "Income", "expense": "Expense"}
    )

    with engine.begin() as conn:
        for _, row in cat_df.iterrows():
            conn.execute(text("""
                INSERT IGNORE INTO dim_category(category_name, category_type)
                VALUES (:category_name, :category_type)
            """), {"category_name": row["category"], "category_type": row["type"]})

    df_map = pd.read_sql("SELECT category_id, category_name FROM dim_category", engine)
    return dict(zip(df_map["category_name"], df_map["category_id"]))


def upsert_customers(engine, df):
    cust_df = df[["customer_name", "region"]].dropna().drop_duplicates()

    with engine.begin() as conn:
        for _, row in cust_df.iterrows():
            conn.execute(text("""
                INSERT INTO dim_customer(customer_name, region)
                SELECT :customer_name, :region
                FROM dual
                WHERE NOT EXISTS (
                    SELECT 1 FROM dim_customer
                    WHERE customer_name=:customer_name
                      AND IFNULL(region,'')=IFNULL(:region,'')
                )
            """), row.to_dict())

    df_map = pd.read_sql(
        "SELECT customer_id, customer_name, region FROM dim_customer", engine
    )
    df_map["region"] = df_map["region"].fillna("")
    return {(r["customer_name"], r["region"]): r["customer_id"]
            for _, r in df_map.iterrows()}


def upsert_products(engine, df):
    prod_df = df[["product_name", "product_category", "unit_price"]] \
        .dropna(subset=["product_name"]).drop_duplicates()
    prod_df["product_category"] = prod_df["product_category"].fillna("Unknown")

    with engine.begin() as conn:
        for _, row in prod_df.iterrows():
            conn.execute(text("""
                INSERT INTO dim_product(product_name, product_category, unit_price)
                SELECT :product_name, :product_category, :unit_price
                FROM dual
                WHERE NOT EXISTS (
                    SELECT 1 FROM dim_product WHERE product_name=:product_name
                )
            """), row.to_dict())

    df_map = pd.read_sql("SELECT product_id, product_name FROM dim_product", engine)
    return dict(zip(df_map["product_name"], df_map["product_id"]))


# --------------------------
# Fact Loaders
# --------------------------

def load_transactions(engine):

    if not os.path.exists(TXN_FILE):
        raise FileNotFoundError(TXN_FILE)

    df = pd.read_csv(TXN_FILE)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    date_map = ensure_dim_date(engine, df["date"])
    account_map = ensure_dim_simple(engine, "dim_account", "account_name", df["account"])
    vendor_map = ensure_dim_simple(engine, "dim_vendor", "vendor_name", df["vendor"])
    category_map = ensure_dim_category(engine, df)

    df["date_id"] = df["date"].dt.date.map(date_map)
    df["account_id"] = df["account"].map(account_map)
    df["vendor_id"] = df["vendor"].map(vendor_map)
    df["category_id"] = df["category"].map(category_map)

    df_fact = df[[
        "transaction_id", "date_id", "account_id", "category_id",
        "vendor_id", "description", "amount", "type",
        "payment_method", "is_recurring"
    ]].copy()

    df_fact.rename(columns={
        "transaction_id": "txn_id",
        "type": "txn_type"
    }, inplace=True)

    with engine.begin() as conn:
        for _, row in df_fact.iterrows():
            conn.execute(text("""
                INSERT IGNORE INTO fact_transactions(
                    txn_id,date_id,account_id,category_id,vendor_id,
                    description,amount,txn_type,payment_method,is_recurring
                )
                VALUES (
                    :txn_id,:date_id,:account_id,:category_id,:vendor_id,
                    :description,:amount,:txn_type,:payment_method,:is_recurring
                )
            """), mysql_safe_row_dict(row.to_dict()))

    print("✅ fact_transactions loaded")


def load_sales(engine):

    if not os.path.exists(SALES_FILE):
        raise FileNotFoundError(SALES_FILE)

    df = pd.read_csv(SALES_FILE)
    df["stage_date"] = pd.to_datetime(df["stage_date"], errors="coerce")

    ensure_dim_date(engine, df["stage_date"])
    cust_map = upsert_customers(engine, df)

    df["customer_key"] = list(zip(df["customer_name"], df["region"].fillna("")))
    df["customer_id"] = df["customer_key"].map(cust_map)

    df_fact = df[[
        "lead_id","customer_id","source","stage",
        "stage_date","expected_value","actual_value","sales_rep"
    ]]

    with engine.begin() as conn:
        for _, row in df_fact.iterrows():
            conn.execute(text("""
                INSERT IGNORE INTO fact_sales_funnel(
                    lead_id,customer_id,source,stage,
                    stage_date,expected_value,actual_value,sales_rep
                )
                VALUES (
                    :lead_id,:customer_id,:source,:stage,
                    :stage_date,:expected_value,:actual_value,:sales_rep
                )
            """), mysql_safe_row_dict(row.to_dict()))

    print("✅ fact_sales_funnel loaded")


def load_inventory(engine):

    if not os.path.exists(INV_FILE):
        raise FileNotFoundError(INV_FILE)

    df = pd.read_csv(INV_FILE)
    df["date"] = pd.to_datetime(df["date"], errors="coerce")

    date_map = ensure_dim_date(engine, df["date"])
    prod_map = upsert_products(engine, df)

    df["date_id"] = df["date"].dt.date.map(date_map)
    df["product_id"] = df["product_name"].map(prod_map)

    df_fact = df[[
        "move_id","product_id","date_id",
        "quantity","move_type","unit_price","warehouse"
    ]]

    with engine.begin() as conn:
        for _, row in df_fact.iterrows():
            conn.execute(text("""
                INSERT IGNORE INTO fact_inventory_moves(
                    move_id,product_id,date_id,
                    quantity,move_type,unit_price,warehouse
                )
                VALUES (
                    :move_id,:product_id,:date_id,
                    :quantity,:move_type,:unit_price,:warehouse
                )
            """), mysql_safe_row_dict(row.to_dict()))

    print("✅ fact_inventory_moves loaded")


# --------------------------
# Main
# --------------------------

def main():
    engine = get_engine()
    load_transactions(engine)
    load_sales(engine)
    load_inventory(engine)
    print("\n🎉 ALL DATA LOADED INTO MYSQL SUCCESSFULLY!")


if __name__ == "__main__":
    main()
