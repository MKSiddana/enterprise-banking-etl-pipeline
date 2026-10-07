# 🏦 Enterprise Banking ETL Pipeline

A production-oriented banking ETL framework built with **Python and SQL**, demonstrating incremental data processing, data quality validation, idempotent loading, source-to-target reconciliation, audit logging, watermark management, and retry/recovery patterns.

> All banking data in this repository is synthetic and created solely for portfolio demonstration.

---

## 🏗️ Architecture

```text
                  ┌─────────────────────┐
                  │ Banking Source Data │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │       Extract       │
                  └──────────┬──────────┘
                             ↓
                   Read Last Watermark
                             ↓
                  ┌─────────────────────┐
                  │ Incremental Filter  │
                  │ last_updated > WM   │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │      Validate       │
                  └──────┬────────┬─────┘
                         │        │
                       Valid   Rejected
                         │
                         ↓
                  ┌─────────────────────┐
                  │     Transform       │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │       Load          │
                  │ Idempotent Upsert   │
                  │ Retry / Recovery    │
                  └──────────┬──────────┘
                             ↓
                  ┌─────────────────────┐
                  │     Reconcile       │
                  │ Count + Amounts     │
                  └──────────┬──────────┘
                             ↓
                      SUCCESS / FAILED
                             ↓
                  ┌─────────────────────┐
                  │     ETL Audit       │
                  └─────────────────────┘
                             │
                       If Successful
                             ↓
                     Update Watermark
```

---

## 🛠️ Technology Stack

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=FFD43B)
![SQL](https://img.shields.io/badge/SQL-CC2927?style=for-the-badge&logo=microsoftsqlserver&logoColor=white)
![Azure SQL](https://img.shields.io/badge/Azure_SQL-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

---

## 📁 Repository Structure

```text
enterprise-banking-etl-pipeline/
│
├── data/
│   └── sample_transactions.csv
│
├── src/
│   ├── extract.py
│   ├── validate.py
│   ├── transform.py
│   ├── load.py
│   ├── reconcile.py
│   ├── audit.py
│   ├── watermark.py
│   └── pipeline.py
│
├── sql/
│   └── create_tables.sql
│
├── .gitignore
└── README.md
```

---

## ⚙️ ETL Pipeline

### 1️⃣ Extract

`src/extract.py`

Reads banking transaction data and converts source values into strongly typed Python objects.

The extraction layer handles:

- Transaction amounts
- Transaction timestamps
- Last-updated timestamps
- Source record counting

---

### 2️⃣ Incremental Processing

`src/watermark.py`

The pipeline uses `last_updated` as an incremental-processing control.

```text
Previous Successful Watermark
            ↓
       Source Records
            ↓
last_updated > watermark
            ↓
     Changed Records
```

The watermark is advanced only after successful processing and reconciliation, reducing the risk of skipping records after a failed pipeline execution.

---

### 3️⃣ Data Quality Validation

`src/validate.py`

Incoming records are validated for:

- Required fields
- Duplicate transaction IDs
- Positive transaction amounts
- Valid transaction types
- Valid transaction statuses
- Supported transaction channels
- Supported currency

Records are separated into:

```text
Incoming Records
      ↓
  Validation
   ↙       ↘
Valid     Rejected
```

This allows invalid records to be isolated instead of automatically terminating processing for every data-quality issue.

---

### 4️⃣ Transform

`src/transform.py`

Validated transactions are standardized and enriched with:

- Standardized transaction types
- Standardized status values
- Standardized channels
- Currency normalization
- Monetary precision
- Transaction date
- ETL processing timestamp
- Signed transaction amount

Example:

```text
CREDIT  $2,500 → +2500
DEBIT     $125 → -125
```

The signed amount provides a convenient representation for downstream financial aggregation.

---

### 5️⃣ Idempotent Load

`src/load.py`

The load layer writes transformed records into the target transaction table.

The implementation demonstrates **idempotent processing** using the transaction ID as the business key.

```text
New transaction
      ↓
    INSERT

Existing transaction
      ↓
    UPDATE
```

This prevents duplicate target records when a transaction is reprocessed.

SQLite is used to make the portfolio project locally runnable without requiring cloud infrastructure.

The included SQL scripts demonstrate a SQL Server/Azure SQL-style production schema.

---

### 6️⃣ Retry & Recovery

Transient load failures are retried automatically.

```text
Load Attempt 1
      ↓
   Failure
      ↓
Wait → Retry

Load Attempt 2
      ↓
   Success
```

The example pipeline supports up to **3 load attempts** before marking the run as failed.

---

### 7️⃣ Source-to-Target Reconciliation

`src/reconcile.py`

The reconciliation layer validates the incremental batch after loading.

It compares:

| Control | Source | Target |
|---|---|---|
| Record Count | Incremental records | Matching target records |
| Transaction Amount | Source total | Target total |
| Signed Amount | Source net total | Target net total |

The target comparison is limited to the transaction IDs belonging to the current incremental batch.

This prevents historical target records from incorrectly affecting incremental reconciliation.

---

### 8️⃣ ETL Audit Logging

`src/audit.py`

Every pipeline execution receives a unique `run_id`.

Audit information includes:

- Pipeline name
- Run ID
- Start time
- End time
- Source record count
- Valid record count
- Rejected record count
- Loaded record count
- Pipeline status
- Error message

Example lifecycle:

```text
STARTED
   ↓
ETL Processing
   ↓
┌──────────────┐
↓              ↓
SUCCESS       FAILED
```

This provides operational traceability for pipeline executions.

---

## 🗄️ SQL Control Tables

`sql/create_tables.sql`

The SQL layer defines three enterprise-style tables:

### `banking_transactions`

Stores curated banking transactions.

### `etl_audit`

Stores execution history, counts, status, timestamps, and errors.

### `etl_watermark`

Stores the last successfully processed timestamp for incremental ingestion.

---

## 🔄 End-to-End Flow

```text
Extract
   ↓
Read Watermark
   ↓
Incremental Filter
   ↓
Validate
   ↓
Transform
   ↓
Load
   ↓
Reconcile
   ↓
Audit
   ↓
Update Watermark
```

---

## ▶️ Run Locally

This project uses only the Python standard library and SQLite for the local demonstration.

From the repository root:

```bash
python src/pipeline.py
```

The pipeline creates the local database under:

```text
output/banking_etl.db
```

The `output/` directory should remain local and should not contain production or client data.

---

## 💡 Key Data Engineering Concepts

- Enterprise ETL architecture
- Incremental ingestion
- Watermark management
- Python data processing
- SQL data modeling
- Data quality validation
- Reject handling
- Idempotent loading
- Upsert patterns
- Source-to-target reconciliation
- Audit/control frameworks
- Retry and recovery
- Pipeline observability
- Error handling

---

## 🔐 Data Privacy

All transaction, account, and customer records included in this repository are **synthetic**.

This repository contains no proprietary employer data, client data, banking information, credentials, or production code.

---

## 🚀 Future Enhancements

Potential extensions include:

- Azure Data Factory orchestration
- Azure SQL Database integration
- ADLS Gen2 source/landing zones
- Config-driven pipeline execution
- Automated unit testing
- CI/CD with GitHub Actions
- Rejected-record persistence
- Email/Teams failure notifications
- Secrets management with Azure Key Vault
- Pipeline metrics and monitoring dashboards

---

## 👩‍💻 Author

**Madhuri Krishna Siddana**

Senior Data Engineer focused on scalable ETL/ELT pipelines, cloud data platforms, distributed processing, data quality, and reliable production data systems.
