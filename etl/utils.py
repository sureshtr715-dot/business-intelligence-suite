"""
File: utils.py
Purpose: Common utility functions for ETL pipelines
"""

import pandas as pd


def normalize_text(x):
    """
    Strip spaces and convert text to Title Case.
    Returns None if value is NaN.
    """
    if pd.isna(x):
        return None
    return str(x).strip().title()


def normalize_lower(x):
    """
    Strip spaces and convert text to lowercase.
    Returns None if value is NaN.
    """
    if pd.isna(x):
        return None
    return str(x).strip().lower()


def safe_to_date(series):
    """
    Convert mixed-format date series into datetime.
    Invalid values become NaT.
    """
    return pd.to_datetime(series, errors="coerce", dayfirst=True)


def year_month_str(dt_series):
    """
    Convert datetime series to YYYY-MM string.
    """
    return dt_series.dt.strftime("%Y-%m")


def remove_duplicates(df, key_cols):
    """
    Remove duplicate rows using key columns.
    Keeps first occurrence.
    """
    return df.drop_duplicates(subset=key_cols, keep="first")
