"""
File: 01_clean_transactions.py
Purpose: Clean raw transactions Excel and produce processed CSV
"""

import pandas as pd
from utils import normalize_text, normalize_lower, safe_to_date, remove_duplicates
import os

RAW_FILE = "data/raw/transactions.xlsx"
OUT_FILE = "data/processed/transactions_clean.csv"


def main():

    # --------------------------
    # File existence check
    # --------------------------
    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(f"Missing file: {RAW_FILE}")

    df = pd.read_excel(RAW_FILE)

    # --------------------------
    # Standardize column names
    # --------------------------
    df.columns = [c.strip().lower() for c in df.columns]

    # --------------------------
    # Date cleaning
    # --------------------------
    df["date"] = safe_to_date(df["date"])

    # --------------------------
    # Normalize text fields
    # --------------------------
    df["type"] = df["type"].apply(normalize_lower)
    df["category"] = df["category"].apply(normalize_text)
    df["account"] = df["account"].apply(normalize_text)
    df["payment_method"] = df["payment_method"].apply(normalize_text)
    df["vendor"] = df["vendor"].apply(normalize_text)
    df["is_recurring"] = df["is_recurring"].apply(normalize_text)

    # --------------------------
    # Category standardization
    # --------------------------
    category_map = {
        "Grocery": "Groceries",
        "Groceries": "Groceries",
        "Food": "Food",
        "Subscription": "Subscription",
        "Mobile": "Mobile"
    }
    df["category"] = df["category"].replace(category_map)

    # --------------------------
    # Remove duplicates
    # --------------------------
    df = remove_duplicates(df, ["transaction_id"])

    # --------------------------
    # Remove missing dates
    # --------------------------
    df = df[df["date"].notna()]

    # --------------------------
    # Convert recurring to boolean
    # --------------------------
    df["is_recurring"] = (
        df["is_recurring"]
        .map({"Yes": True, "No": False})
        .fillna(False)
    )

    # --------------------------
    # Amount must be numeric
    # --------------------------
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df[df["amount"].notna()]

    # --------------------------
    # Save output
    # --------------------------
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT_FILE, index=False)

    print(f"✅ Cleaned Transactions saved -> {OUT_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()
