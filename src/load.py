import sqlite3
from pathlib import Path


DATABASE_PATH = Path("output/banking_etl.db")


def get_connection():
    """
    Create a connection to the local demonstration database.
    """

    DATABASE_PATH.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    return sqlite3.connect(DATABASE_PATH)


def create_target_table(connection):
    """
    Create the target transaction table for local execution.
    """

    connection.execute("""
        CREATE TABLE IF NOT EXISTS banking_transactions (
            transaction_id TEXT PRIMARY KEY,
            account_id TEXT NOT NULL,
            customer_id TEXT NOT NULL,
            transaction_type TEXT NOT NULL,
            transaction_amount REAL NOT NULL,
            signed_amount REAL NOT NULL,
            currency TEXT NOT NULL,
            transaction_timestamp TEXT NOT NULL,
            transaction_date TEXT NOT NULL,
            transaction_status TEXT NOT NULL,
            channel TEXT NOT NULL,
            last_updated TEXT NOT NULL,
            etl_processed_at TEXT NOT NULL
        )
    """)

    connection.commit()


def load_transactions(records):
    """
    Load transformed transactions into the target table.

    Existing transaction IDs are updated so the load
    remains idempotent when records are reprocessed.
    """

    connection = get_connection()

    try:
        create_target_table(connection)

        for record in records:
            connection.execute(
                """
                INSERT INTO banking_transactions (
                    transaction_id,
                    account_id,
                    customer_id,
                    transaction_type,
                    transaction_amount,
                    signed_amount,
                    currency,
                    transaction_timestamp,
                    transaction_date,
                    transaction_status,
                    channel,
                    last_updated,
                    etl_processed_at
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)

                ON CONFLICT(transaction_id)
                DO UPDATE SET
                    account_id = excluded.account_id,
                    customer_id = excluded.customer_id,
                    transaction_type = excluded.transaction_type,
                    transaction_amount = excluded.transaction_amount,
                    signed_amount = excluded.signed_amount,
                    currency = excluded.currency,
                    transaction_timestamp =
                        excluded.transaction_timestamp,
                    transaction_date = excluded.transaction_date,
                    transaction_status =
                        excluded.transaction_status,
                    channel = excluded.channel,
                    last_updated = excluded.last_updated,
                    etl_processed_at =
                        excluded.etl_processed_at
                """,
                (
                    record["transaction_id"],
                    record["account_id"],
                    record["customer_id"],
                    record["transaction_type"],
                    record["transaction_amount"],
                    record["signed_amount"],
                    record["currency"],
                    str(record["transaction_timestamp"]),
                    str(record["transaction_date"]),
                    record["transaction_status"],
                    record["channel"],
                    str(record["last_updated"]),
                    str(record["etl_processed_at"]),
                )
            )

        connection.commit()

        print(
            f"Loaded {len(records)} records "
            "into banking_transactions."
        )

        return len(records)

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
