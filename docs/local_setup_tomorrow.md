# Local Setup Guide

Use this tomorrow when deploying the project locally.

## 1. Open terminal in the project folder

```bash
cd retail-supply-chain-control-tower
```

## 2. Create virtual environment

Windows PowerShell:

```bash
python -m venv .venv
.venv\Scripts\activate
```

Mac/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

## 4. Download raw datasets

Place Olist CSV files here:

```text
data/raw/olist/
```

Place M5 CSV files here:

```text
data/raw/m5/
```

## 5. Create MySQL database

Open MySQL Workbench and run:

```sql
CREATE DATABASE retail_supply_chain;
```

Then run the SQL scripts in this order:

```text
sql/01_create_olist_tables.sql
sql/02_clean_olist_data.sql
sql/03_build_supply_chain_kpis.sql
sql/04_seller_delivery_scorecard.sql
sql/05_late_delivery_features.sql
```

## 6. Import Olist CSV files into MySQL

Recommended first method: use MySQL Workbench Table Data Import Wizard.

Target tables:

```text
stg_orders
stg_order_items
stg_customers
stg_sellers
stg_products
stg_payments
stg_reviews
stg_category_translation
```

## 7. Open Jupyter Notebook

```bash
jupyter notebook
```

Then start with:

```text
notebooks/01_olist_supply_chain_eda.ipynb
```

## 8. First success checkpoint

By the end of local setup, you should be able to produce:

- a monthly KPI table;
- a seller scorecard table;
- one delivery performance chart;
- one GitHub README update with early findings.
