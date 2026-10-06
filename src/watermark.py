from datetime import datetime
from load import get_connection


PIPELINE_NAME = "enterprise_banking_etl"

DEFAULT_WATERMARK = "1900-01-01 00:00:00"


def create_watermark_table(connection):
    """
    Create the watermark control table for local execution.
    """

    connection.execute("""
        CREATE TABLE IF NOT EXISTS etl_watermark (
            pipeline_name TEXT PRIMARY KEY,
            last_watermark TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    connection.commit()


def get_watermark():
    """
    Return the last successfully processed watermark.
    """

    connection = get_connection()

    try:
        create_watermark_table(connection)

        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT last_watermark
            FROM etl_watermark
            WHERE pipeline_name = ?
            """,
            (PIPELINE_NAME,)
        )

        result = cursor.fetchone()

        if result:
            return datetime.strptime(
                result[0],
                "%Y-%m-%d %H:%M:%S"
            )

        return datetime.strptime(
            DEFAULT_WATERMARK,
            "%Y-%m-%d %H:%M:%S"
        )

    finally:
        connection.close()


def filter_incremental_records(records, watermark):
    """
    Select records changed after the previous successful run.
    """

    incremental_records = [
        record
        for record in records
        if record["last_updated"] > watermark
    ]

    print(
        f"Incremental records selected: "
        f"{len(incremental_records)}"
    )

    return incremental_records


def update_watermark(records):
    """
    Persist the maximum last_updated value after a
    successful pipeline run.
    """

    if not records:
        return

    new_watermark = max(
        record["last_updated"]
        for record in records
    )

    connection = get_connection()

    try:
        create_watermark_table(connection)

        connection.execute(
            """
            INSERT INTO etl_watermark (
                pipeline_name,
                last_watermark,
                updated_at
            )
            VALUES (?, ?, ?)

            ON CONFLICT(pipeline_name)
            DO UPDATE SET
                last_watermark = excluded.last_watermark,
                updated_at = excluded.updated_at
            """,
            (
                PIPELINE_NAME,
                new_watermark.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
                datetime.utcnow().strftime(
                    "%Y-%m-%d %H:%M:%S"
                )
            )
        )

        connection.commit()

        print(
            "Watermark updated to:",
            new_watermark
        )

    finally:
        connection.close()
