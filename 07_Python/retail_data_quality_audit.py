"""
Retail Data Quality and Information Governance Audit

Purpose:
- Load and validate the Superstore retail dataset
- Identify missing values and master-data inconsistencies
- Create transparent data-quality flags
- Produce a privacy-safe portfolio dataset

The raw and private cleaned datasets are excluded from GitHub.
"""

from pathlib import Path

import pandas as pd


# ---------------------------------------------------------
# PROJECT FILE PATHS
# ---------------------------------------------------------

# The script is inside 07_Python, so parent.parent identifies
# the main Retail-Analytics-Portfolio folder.
PROJECT_FOLDER = Path(__file__).resolve().parent.parent

RAW_FILE = (
    PROJECT_FOLDER
    / "01_Raw_Data"
    / "superstore_raw.csv"
)

CLEANED_FILE = (
    PROJECT_FOLDER
    / "02_Cleaned_Data"
    / "superstore_cleaned.csv"
)

PUBLIC_FILE = (
    PROJECT_FOLDER
    / "02_Cleaned_Data"
    / "superstore_public_portfolio.csv"
)

DOCUMENTATION_FOLDER = (
    PROJECT_FOLDER
    / "05_Documentation"
)


# ---------------------------------------------------------
# LOAD THE RAW DATASET
# ---------------------------------------------------------

if not RAW_FILE.exists():
    raise FileNotFoundError(
        f"Raw dataset was not found at: {RAW_FILE}"
    )

df_raw = pd.read_csv(RAW_FILE)
df_clean = df_raw.copy()

print("Raw dataset loaded successfully.")
print(f"Rows: {len(df_raw):,}")
print(f"Columns: {len(df_raw.columns)}")

# ---------------------------------------------------------
# INITIAL DATA-QUALITY VALIDATION
# ---------------------------------------------------------

missing_values_before = int(df_clean.isna().sum().sum())
complete_duplicates = int(df_clean.duplicated().sum())
duplicate_row_ids = int(df_clean["Row ID"].duplicated().sum())

print("\nInitial data-quality checks:")
print(f"Missing values: {missing_values_before}")
print(f"Completely duplicated rows: {complete_duplicates}")
print(f"Duplicated Row IDs: {duplicate_row_ids}")


# ---------------------------------------------------------
# POSTAL-CODE CLEANING
# ---------------------------------------------------------

# The dataset contains 11 missing postal codes.
# All affected records relate to Burlington, Vermont.
missing_postal_mask = (
    df_clean["Postal Code"].isna()
    & df_clean["City"].eq("Burlington")
    & df_clean["State"].eq("Vermont")
)

# Retain an audit flag showing which records were changed.
df_clean["Postal Code Imputed"] = missing_postal_mask

# Apply the documented Burlington, Vermont postal code.
df_clean.loc[
    missing_postal_mask,
    "Postal Code"
] = 5401

# Postal codes are identifiers rather than quantities.
# Store them as five-character text values.
df_clean["Postal Code"] = (
    df_clean["Postal Code"]
    .astype("Int64")
    .astype("string")
    .str.zfill(5)
)

print("\nPostal-code cleaning:")
print(
    "Postal codes imputed:",
    int(df_clean["Postal Code Imputed"].sum())
)
print(
    "Missing postal codes remaining:",
    int(df_clean["Postal Code"].isna().sum())
)


# ---------------------------------------------------------
# DATE STANDARDISATION
# ---------------------------------------------------------

df_clean["Order Date"] = pd.to_datetime(
    df_clean["Order Date"],
    format="%d/%m/%Y",
    errors="coerce"
)

df_clean["Ship Date"] = pd.to_datetime(
    df_clean["Ship Date"],
    format="%d/%m/%Y",
    errors="coerce"
)

invalid_order_dates = int(
    df_clean["Order Date"].isna().sum()
)

invalid_ship_dates = int(
    df_clean["Ship Date"].isna().sum()
)

shipments_before_orders = int(
    (
        df_clean["Ship Date"]
        < df_clean["Order Date"]
    ).sum()
)

print("\nDate validation:")
print(f"Invalid Order Dates: {invalid_order_dates}")
print(f"Invalid Ship Dates: {invalid_ship_dates}")
print(
    "Shipments before Order Date:",
    shipments_before_orders
)

# ---------------------------------------------------------
# PRODUCT MASTER-DATA VALIDATION
# ---------------------------------------------------------

# Find Product IDs associated with more than one product name.
product_id_name_counts = (
    df_clean.groupby("Product ID")["Product Name"]
    .nunique()
)

reused_product_ids = product_id_name_counts[
    product_id_name_counts > 1
].index

# Find Product Names associated with more than one Product ID.
product_name_id_counts = (
    df_clean.groupby("Product Name")["Product ID"]
    .nunique()
)

product_names_with_multiple_ids = product_name_id_counts[
    product_name_id_counts > 1
].index

# Retain transparent audit flags rather than changing
# or deleting the conflicting original values.
df_clean["Product ID Reused"] = (
    df_clean["Product ID"].isin(reused_product_ids)
)

df_clean["Product Name Multiple IDs"] = (
    df_clean["Product Name"].isin(
        product_names_with_multiple_ids
    )
)

# Create a reliable composite key from both original fields.
df_clean["Product Key"] = (
    df_clean["Product ID"].astype("string")
    + " | "
    + df_clean["Product Name"].astype("string")
)

print("\nProduct master-data validation:")
print(
    "Product IDs reused for different products:",
    len(reused_product_ids)
)
print(
    "Rows affected by reused Product IDs:",
    int(df_clean["Product ID Reused"].sum())
)
print(
    "Product names linked to multiple IDs:",
    len(product_names_with_multiple_ids)
)
print(
    "Rows affected by product names with multiple IDs:",
    int(df_clean["Product Name Multiple IDs"].sum())
)
print(
    "Unique composite Product Keys:",
    df_clean["Product Key"].nunique()
)


# ---------------------------------------------------------
# ANALYSIS-READY FIELDS
# ---------------------------------------------------------

df_clean["Shipping Days"] = (
    df_clean["Ship Date"]
    - df_clean["Order Date"]
).dt.days

df_clean["Order Year"] = (
    df_clean["Order Date"].dt.year
)

df_clean["Order Month Number"] = (
    df_clean["Order Date"].dt.month
)

df_clean["Order Month"] = (
    df_clean["Order Date"].dt.month_name()
)

df_clean["Order Year-Month"] = (
    df_clean["Order Date"]
    .dt.to_period("M")
    .astype("string")
)

print("\nAnalysis-field validation:")
print(
    "Negative shipping durations:",
    int((df_clean["Shipping Days"] < 0).sum())
)
print(
    "Minimum shipping days:",
    int(df_clean["Shipping Days"].min())
)
print(
    "Maximum shipping days:",
    int(df_clean["Shipping Days"].max())
)


# ---------------------------------------------------------
# OVERALL DATA-QUALITY STATUS
# ---------------------------------------------------------

quality_flag_columns = [
    "Postal Code Imputed",
    "Product ID Reused",
    "Product Name Multiple IDs"
]

df_clean["Data Quality Issue Count"] = (
    df_clean[quality_flag_columns]
    .astype(int)
    .sum(axis=1)
)

df_clean["Data Quality Status"] = (
    df_clean["Data Quality Issue Count"]
    .gt(0)
    .map({
        True: "Review Required",
        False: "Passed"
    })
)


def create_quality_notes(row):
    """Create a readable explanation of identified issues."""

    issues = []

    if row["Postal Code Imputed"]:
        issues.append("Postal code imputed")

    if row["Product ID Reused"]:
        issues.append(
            "Product ID reused for different products"
        )

    if row["Product Name Multiple IDs"]:
        issues.append(
            "Product name linked to multiple IDs"
        )

    if not issues:
        return "No known data-quality issue"

    return "; ".join(issues)


df_clean["Data Quality Notes"] = df_clean.apply(
    create_quality_notes,
    axis=1
)

records_passed = int(
    (df_clean["Data Quality Status"] == "Passed").sum()
)

records_requiring_review = int(
    (
        df_clean["Data Quality Status"]
        == "Review Required"
    ).sum()
)

print("\nOverall data-quality results:")
print("Records passed:", records_passed)
print(
    "Records requiring review:",
    records_requiring_review
)
print(
    "Records with two identified issues:",
    int((df_clean["Data Quality Issue Count"] == 2).sum())
)

# ---------------------------------------------------------
# PRODUCT-CONFLICT EVIDENCE
# ---------------------------------------------------------

product_conflict_details = (
    df_clean[
        df_clean["Product ID"].isin(reused_product_ids)
    ]
    .groupby(
        [
            "Product ID",
            "Product Name",
            "Category",
            "Sub-Category"
        ],
        dropna=False
    )
    .agg(
        Record_Count=("Row ID", "count"),
        Total_Sales=("Sales", "sum"),
        First_Order_Date=("Order Date", "min"),
        Last_Order_Date=("Order Date", "max")
    )
    .reset_index()
    .sort_values(
        ["Product ID", "Record_Count"],
        ascending=[True, False]
    )
)

product_conflict_details["Total_Sales"] = (
    product_conflict_details["Total_Sales"].round(2)
)


# ---------------------------------------------------------
# CREATE PRIVACY-SAFE PORTFOLIO DATASET
# ---------------------------------------------------------

unique_customers = sorted(
    df_clean["Customer ID"].unique()
)

unique_orders = sorted(
    df_clean["Order ID"].unique()
)

customer_key_map = {
    customer_id: f"CUST-{number:04d}"
    for number, customer_id in enumerate(
        unique_customers,
        start=1
    )
}

order_key_map = {
    order_id: f"ORD-{number:05d}"
    for number, order_id in enumerate(
        unique_orders,
        start=1
    )
}

df_public = df_clean.copy()

df_public["Anonymous Customer Key"] = (
    df_public["Customer ID"].map(customer_key_map)
)

df_public["Anonymous Order Key"] = (
    df_public["Order ID"].map(order_key_map)
)

columns_removed_from_public_file = [
    "Row ID",
    "Order ID",
    "Customer ID",
    "Customer Name",
    "City",
    "Postal Code",
    "Postal Code Imputed"
]

df_public = df_public.drop(
    columns=columns_removed_from_public_file
)

public_column_order = [
    "Anonymous Order Key",
    "Anonymous Customer Key"
] + [
    column
    for column in df_public.columns
    if column not in [
        "Anonymous Order Key",
        "Anonymous Customer Key"
    ]
]

df_public = df_public[public_column_order]


# ---------------------------------------------------------
# CREATE AUDIT SUMMARY
# ---------------------------------------------------------

data_quality_summary = pd.DataFrame({
    "Metric": [
        "Total raw records",
        "Original columns",
        "Cleaned columns",
        "Missing values before cleaning",
        "Missing values after cleaning",
        "Completely duplicated rows",
        "Postal codes imputed",
        "Product IDs reused for different products",
        "Rows affected by reused Product IDs",
        "Product names linked to multiple IDs",
        "Unique composite Product Keys",
        "Records passed",
        "Records requiring review"
    ],
    "Result": [
        len(df_raw),
        len(df_raw.columns),
        len(df_clean.columns),
        missing_values_before,
        int(df_clean.isna().sum().sum()),
        complete_duplicates,
        int(df_clean["Postal Code Imputed"].sum()),
        len(reused_product_ids),
        int(df_clean["Product ID Reused"].sum()),
        len(product_names_with_multiple_ids),
        df_clean["Product Key"].nunique(),
        records_passed,
        records_requiring_review
    ]
})


# ---------------------------------------------------------
# EXPORT FILES
# ---------------------------------------------------------

CLEANED_FILE.parent.mkdir(
    parents=True,
    exist_ok=True
)

DOCUMENTATION_FOLDER.mkdir(
    parents=True,
    exist_ok=True
)

# Private cleaned dataset — excluded through .gitignore
df_clean.to_csv(
    CLEANED_FILE,
    index=False,
    date_format="%Y-%m-%d"
)

# Privacy-safe dataset suitable for GitHub
df_public.to_csv(
    PUBLIC_FILE,
    index=False,
    date_format="%Y-%m-%d"
)

summary_file = (
    DOCUMENTATION_FOLDER
    / "data_quality_audit_summary.csv"
)

conflict_file = (
    DOCUMENTATION_FOLDER
    / "product_mapping_conflicts.csv"
)

data_quality_summary.to_csv(
    summary_file,
    index=False
)

product_conflict_details.to_csv(
    conflict_file,
    index=False,
    date_format="%Y-%m-%d"
)


# ---------------------------------------------------------
# FINAL EXPORT VALIDATION
# ---------------------------------------------------------

print("\nExport validation:")
print(
    "Private cleaned file created:",
    CLEANED_FILE.exists()
)
print(
    "Public portfolio file created:",
    PUBLIC_FILE.exists()
)
print(
    "Audit summary created:",
    summary_file.exists()
)
print(
    "Product conflict report created:",
    conflict_file.exists()
)

print(
    "Rows in public dataset:",
    len(df_public)
)
print(
    "Columns in public dataset:",
    len(df_public.columns)
)
print(
    "Customer Name present in public dataset:",
    "Customer Name" in df_public.columns
)
print(
    "Customer ID present in public dataset:",
    "Customer ID" in df_public.columns
)
print(
    "Missing anonymous customer keys:",
    int(
        df_public[
            "Anonymous Customer Key"
        ].isna().sum()
    )
)
print(
    "Missing anonymous order keys:",
    int(
        df_public[
            "Anonymous Order Key"
        ].isna().sum()
    )
)

print("\nAudit completed successfully.")