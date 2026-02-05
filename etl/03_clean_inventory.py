"""
File: 03_clean_inventory.py
Purpose: Clean raw inventory Excel and produce processed CSV
"""

import pandas as pd
from utils import normalize_text, safe_to_date, remove_duplicates
import os

RAW_FILE = "data/raw/inventory.xlsx"
OUT_FILE = "data/processed/inventory_clean.csv"


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
    df = df[df["date"].notna()]

    # --------------------------
    # Normalize text fields
    # --------------------------
    df["product_name"] = df["product_name"].apply(normalize_text)
    df["product_category"] = df["product_category"].apply(normalize_text)
    df["warehouse"] = df["warehouse"].apply(normalize_text)

    # --------------------------
    # Movement type validation
    # --------------------------
    df["move_type"] = df["move_type"].astype(str).str.strip().str.upper()
    df = df[df["move_type"].isin(["IN", "OUT"])]

    # --------------------------
    # Quantity validation
    # --------------------------
    df["quantity"] = pd.to_numeric(df["quantity"], errors="coerce")
    df = df[df["quantity"].notna()]
    df = df[df["quantity"] > 0]

    # --------------------------
    # Price validation
    # --------------------------
    df["unit_price"] = pd.to_numeric(df["unit_price"], errors="coerce")

    # --------------------------
    # Remove duplicates
    # --------------------------
    df = remove_duplicates(df, ["move_id"])

    # --------------------------
    # Save output
    # --------------------------
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT_FILE, index=False)

    print(f"✅ Cleaned Inventory saved -> {OUT_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()
