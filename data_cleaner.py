import pandas as pd
import numpy as np
import re


def clean_text(value):
    """
    Clean text values while preserving meaningful information.
    """

    if pd.isna(value):
        return ""

    value = str(value).strip()

    # Normalize multiple spaces
    value = re.sub(r"\s+", " ", value)

    return value


def clean_money_column(series):
    """
    Convert masked monetary values into numeric values.
    """

    cleaned = (
        series
        .astype(str)
        .str.replace(",", "", regex=False)
        .str.replace("₹", "", regex=False)
        .str.replace("Rs.", "", regex=False)
        .str.strip()
    )

    return pd.to_numeric(
        cleaned,
        errors="coerce"
    )


def clean_date_column(series):
    """
    Convert Monday date strings into pandas datetime.
    """

    return pd.to_datetime(
        series,
        errors="coerce",
        utc=True
    ).dt.tz_localize(None)


def clean_deals(df):
    """
    Clean Deals data from Monday.com.
    """

    df = df.copy()

    # Clean text columns
    text_columns = [
        "item_name",
        "Owner",
        "Owner code",
        "Client Code",
        "Deal Status",
        "Deal Stage",
        "Product deal",
        "Sector/service"
    ]

    for column in text_columns:

        if column in df.columns:
            df[column] = df[column].apply(clean_text)

    # Numeric columns
    if "Masked Deal value" in df.columns:

        df["Masked Deal value"] = clean_money_column(
            df["Masked Deal value"]
        )

    if "Closure Probability" in df.columns:

        df["Closure Probability"] = pd.to_numeric(
            df["Closure Probability"],
            errors="coerce"
        )

    # Date columns
    date_columns = [
        "Close Date (A)",
        "Tentative Close Date",
        "Created Date",
        "Due date"
    ]

    for column in date_columns:

        if column in df.columns:

            df[column] = clean_date_column(
                df[column]
            )

    return df


def clean_work_orders(df):
    """
    Clean Work Orders data from Monday.com.
    """

    df = df.copy()

    text_columns = [
        "item_name",
        "Customer Name Code",
        "Serial #",
        "Nature of Work",
        "Execution Status",
        "Document Type",
        "BD/KAM Personnel code",
        "Sector",
        "Type of Work",
        "Invoice Status",
        "WO Status (billed)",
        "Collection status",
        "Billing Status"
    ]

    for column in text_columns:

        if column in df.columns:

            df[column] = df[column].apply(
                clean_text
            )

    # Money columns
    money_columns = [
        "Amount in Rupees (Excl of GST) (Masked)",
        "Amount in Rupees (Incl of GST) (Masked)",
        "Billed Value in Rupees (Excl of GST.) (Masked)",
        "Billed Value in Rupees (Incl of GST.) (Masked)",
        "Collected Amount in Rupees (Incl of GST.) (Masked)",
        "Amount to be billed in Rs. (Exl. of GST) (Masked)",
        "Amount to be billed in Rs. (Incl. of GST) (Masked)",
        "Amount Receivable (Masked)"
    ]

    for column in money_columns:

        if column in df.columns:

            df[column] = clean_money_column(
                df[column]
            )

    # Quantity columns
    quantity_columns = [
        "Quantity by Ops",
        "Quantities as per PO",
        "Quantity billed (till date)",
        "Balance in quantity"
    ]

    for column in quantity_columns:

        if column in df.columns:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Date columns
    date_columns = [
        "Date",
        "Last executed month of recurring project",
        "Data Delivery Date",
        "Date of PO/LOI",
        "Probable Start Date",
        "Probable End Date",
        "Last invoice date",
        "Expected Billing Month",
        "Actual Billing Month",
        "Actual Collection Month",
        "Collection Date"
    ]

    for column in date_columns:

        if column in df.columns:

            df[column] = clean_date_column(
                df[column]
            )

    return df


def get_data_quality_report(df):

    report = {}

    report["total_rows"] = len(df)

    report["total_columns"] = len(df.columns)

    report["missing_values"] = (
        df.isna().sum().to_dict()
    )

    report["rows_with_missing_values"] = int(
        df.isna().any(axis=1).sum()
    )

    return report