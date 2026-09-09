# Retail Data Quality and Information Governance Audit

## Project Overview

This project demonstrates how Python can be used to assess, clean and document the quality of a retail transaction dataset while applying practical information-governance principles.

The analysis covers 9,800 retail transaction records and focuses on:

- Data-quality validation
- Missing-value investigation
- Master-data consistency
- Transparent data correction
- Privacy and data minimisation
- Audit documentation
- Preparation of an analysis-ready dataset

The project preserves the original source data and records every important cleaning decision through audit flags and supporting documentation.

---

## Business Problem

Poor-quality customer, product and transaction data can lead to:

- Inaccurate business reporting
- Incorrect customer or product analysis
- Unreliable dashboard results
- Duplicate or conflicting master records
- Privacy and information-governance risks

The objective was to create a controlled process that identifies these risks without silently deleting or overwriting valid source records.

---

## Dataset

The original dataset contains:

- 9,800 transaction-line records
- 18 original columns
- 4,922 orders
- 793 customers
- Sales records from 2015 to 2018

The dataset includes order, customer, location, product, shipping and sales information.

The original raw dataset and private cleaned dataset are excluded from this public repository.

---

## Data-Quality Checks Completed

The following checks were performed:

- Row and column validation
- Missing-value analysis
- Complete duplicate detection
- Duplicate Row ID detection
- Date-format validation
- Shipping-date validation
- Sales-value validation
- Blank-text and extra-space checks
- Customer ID and Customer Name consistency
- Order ID and Customer ID consistency
- Product ID and Product Name consistency
- Privacy and direct-identifier review

---

## Key Findings

| Finding | Result |
|---|---:|
| Total records reviewed | 9,800 |
| Missing values identified | 11 |
| Completely duplicated rows | 0 |
| Duplicate Row IDs | 0 |
| Invalid Order Dates | 0 |
| Invalid Ship Dates | 0 |
| Shipments before Order Date | 0 |
| Negative Sales values | 0 |
| Product IDs reused for different products | 32 |
| Rows affected by reused Product IDs | 331 |
| Product names linked to multiple Product IDs | 16 |
| Unique composite Product Keys created | 1,893 |
| Records passing all checks | 9,151 |
| Records requiring review | 649 |

---

## Missing Postal-Code Treatment

Eleven postal-code values were missing.

All affected records related to Burlington, Vermont. The missing values were filled using the documented Burlington postal code `05401`.

The correction was not applied silently. A Boolean field named:

`Postal Code Imputed`

was created so every modified record remains identifiable.

Postal codes were converted to text values to preserve leading zeros.

---

## Product Master-Data Issue

The audit identified 32 Product IDs that were associated with more than one Product Name.

The affected values represented genuinely different products rather than simple spelling differences. Therefore, the original values were not overwritten or deleted.

The following controls were introduced:

- `Product ID Reused`
- `Product Name Multiple IDs`
- `Product Key`

The `Product Key` combines the original Product ID and Product Name, producing 1,893 unique product combinations for reliable analysis.

---

## Data-Quality Status

Each transaction received an overall quality result.

The following fields were created:

- `Data Quality Issue Count`
- `Data Quality Status`
- `Data Quality Notes`

Records without a known issue were classified as:

`Passed`

Records containing one or more identified issues were classified as:

`Review Required`

This approach retains potentially valuable records while clearly communicating their limitations.

---

## Information-Governance Controls

The project applies several practical governance principles.

### Data minimisation

The public dataset excludes:

- Customer Name
- Original Customer ID
- Original Order ID
- Exact City
- Postal Code
- Internal Row ID

### Pseudonymisation

Original customer and order identifiers were replaced with:

- `Anonymous Customer Key`
- `Anonymous Order Key`

### Auditability

Important cleaning decisions are recorded through flags, quality-status fields and separate audit reports.

### Access control

The raw dataset, private cleaned dataset and record-level working notebook are excluded from GitHub through `.gitignore`.

### Purpose limitation

The public dataset retains only the information required to demonstrate retail analysis and data-quality controls.

---

## Analysis-Ready Fields Added

The following calculated fields were added:

- Shipping Days
- Order Year
- Order Month Number
- Order Month
- Order Year-Month
- Product Key
- Data Quality Issue Count
- Data Quality Status
- Data Quality Notes

These fields support future SQL analysis and Power BI reporting.

---

## Repository Structure

```text
Retail-Analytics-Portfolio/
│
├── 01_Raw_Data/
│   └── Private raw dataset — excluded from GitHub
│
├── 02_Cleaned_Data/
│   ├── superstore_cleaned.csv — private and excluded
│   └── superstore_public_portfolio.csv
│
├── 03_SQL/
│
├── 04_PowerBI/
│
├── 05_Documentation/
│   ├── data_dictionary.csv
│   ├── data_quality_audit_summary.csv
│   ├── product_mapping_conflicts.csv
│   └── postal_code_imputations.csv — private and excluded
│
├── 06_Images/
│
├── 07_Python/
│   ├── retail_data_cleaning.ipynb — private and excluded
│   └── retail_data_quality_audit.py
│
├── .gitignore
└── README.md
```

---

## Public Repository Files

### `retail_data_quality_audit.py`

A reproducible Python script containing the main validation, cleaning, audit and privacy-safe export process.

### `superstore_public_portfolio.csv`

A privacy-safe version of the cleaned dataset with direct customer identifiers and precise location fields removed.

### `data_quality_audit_summary.csv`

A summary of the principal audit findings and cleaning results.

### `product_mapping_conflicts.csv`

Detailed evidence of Product IDs associated with multiple Product Names.

### `data_dictionary.csv`

Documentation describing the purpose, data type, governance classification and recommended handling of each cleaned-data field.

---

## Tools Used

- Python
- pandas
- pathlib
- Visual Studio Code
- Jupyter Notebook
- CSV
- GitHub

---

## Running the Python Audit

The public script expects the original dataset to be available locally at:

```text
01_Raw_Data/superstore_raw.csv
```

Run the script from the main project folder using:

```powershell
python 07_Python/retail_data_quality_audit.py
```

The script produces:

- A private cleaned dataset
- A privacy-safe public dataset
- A data-quality audit summary
- A product-conflict report

The original source dataset is not included in the public repository.

---

## Limitations

- The dataset does not contain complete street-address information.
- The postal-code correction is recorded as an imputation rather than treated as verified address-level information.
- Conflicting product identifiers cannot be conclusively corrected without an authoritative product master-data source.
- Records requiring review are retained because their transactional values may still be useful.
- The dataset is used as a portfolio simulation and does not represent a live organisational information-governance system.

---

## Recommendations

1. Introduce validation rules when Product IDs are created.
2. Maintain one authoritative product master-data table.
3. Prevent Product IDs from being assigned to multiple products.
4. Require mandatory postal-code validation during data entry.
5. Maintain an audit trail for corrected or imputed values.
6. Restrict access to direct customer identifiers.
7. Use anonymised or aggregated data for public reporting.
8. Review records marked as `Review Required` before operational use.

---

## Skills Demonstrated

- Python data cleaning
- Data-quality auditing
- Data validation
- Master-data analysis
- Privacy-aware data preparation
- Pseudonymisation
- Data minimisation
- Audit-trail creation
- Data documentation
- Analytical problem-solving