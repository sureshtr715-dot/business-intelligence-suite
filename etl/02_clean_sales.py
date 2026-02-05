"""
File: 02_clean_sales.py
Purpose: Clean raw sales funnel Excel and produce processed CSV
"""

import pandas as pd
from utils import normalize_text, safe_to_date, remove_duplicates
import os

RAW_FILE = "data/raw/sales_funnel.xlsx"
OUT_FILE = "data/processed/sales_clean.csv"

VALID_STAGES = {
    "lead": "Lead",
    "qualified": "Qualified",
    "proposal": "Proposal",
    "closed won": "Closed Won",
    "closed lost": "Closed Lost"
}


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
    df["stage_date"] = safe_to_date(df["stage_date"])

    # --------------------------
    # Normalize text
    # --------------------------
    df["customer_name"] = df["customer_name"].apply(normalize_text)
    df["region"] = df["region"].apply(normalize_text)
    df["source"] = df["source"].apply(normalize_text)
    df["sales_rep"] = df["sales_rep"].apply(normalize_text)

    # --------------------------
    # Stage standardization
    # --------------------------
    df["stage"] = df["stage"].astype(str).str.strip().str.lower()
    df["stage"] = df["stage"].map(VALID_STAGES)

    # --------------------------
    # Remove invalid records
    # --------------------------
    df = df[df["stage"].notna()]
    df = df[df["stage_date"].notna()]

    # --------------------------
    # Numeric conversion
    # --------------------------
    df["expected_value"] = pd.to_numeric(df["expected_value"], errors="coerce")
    df["actual_value"] = pd.to_numeric(df["actual_value"], errors="coerce")

    # --------------------------
    # Remove duplicates
    # --------------------------
    df = remove_duplicates(df, ["lead_id"])

    # --------------------------
    # Save output
    # --------------------------
    os.makedirs("data/processed", exist_ok=True)
    df.to_csv(OUT_FILE, index=False)

    print(f"✅ Cleaned Sales Funnel saved -> {OUT_FILE}")
    print(df.head())


if __name__ == "__main__":
    main()
