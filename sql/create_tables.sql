-- =========================================================
-- Enterprise Banking ETL
-- Target and Audit Tables
-- =========================================================


-- ---------------------------------------------------------
-- Target transaction table
-- ---------------------------------------------------------

CREATE TABLE banking_transactions (
    transaction_id        VARCHAR(50) PRIMARY KEY,
    account_id            VARCHAR(50) NOT NULL,
    customer_id           VARCHAR(50) NOT NULL,
    transaction_type      VARCHAR(20) NOT NULL,
    transaction_amount    DECIMAL(18, 2) NOT NULL,
    signed_amount         DECIMAL(18, 2) NOT NULL,
    currency              VARCHAR(10) NOT NULL,
    transaction_timestamp DATETIME2 NOT NULL,
    transaction_date      DATE NOT NULL,
    transaction_status    VARCHAR(20) NOT NULL,
    channel               VARCHAR(20) NOT NULL,
    last_updated          DATETIME2 NOT NULL,
    etl_processed_at      DATETIME2 NOT NULL
);


-- ---------------------------------------------------------
-- ETL audit table
-- ---------------------------------------------------------

CREATE TABLE etl_audit (
    audit_id              BIGINT IDENTITY(1,1) PRIMARY KEY,
    pipeline_name         VARCHAR(100) NOT NULL,
    run_id                VARCHAR(100) NOT NULL,
    start_time            DATETIME2 NOT NULL,
    end_time              DATETIME2 NULL,
    source_record_count   INT DEFAULT 0,
    valid_record_count    INT DEFAULT 0,
    rejected_record_count INT DEFAULT 0,
    loaded_record_count   INT DEFAULT 0,
    pipeline_status       VARCHAR(20) NOT NULL,
    error_message         VARCHAR(1000) NULL
);


-- ---------------------------------------------------------
-- Incremental load control table
-- ---------------------------------------------------------

CREATE TABLE etl_watermark (
    pipeline_name         VARCHAR(100) PRIMARY KEY,
    last_watermark        DATETIME2 NOT NULL,
    updated_at            DATETIME2 NOT NULL
);
