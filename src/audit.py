from datetime import datetime
from load import get_connection


def create_audit_table(connection):
    """
    Create the ETL audit table for local execution.
    """

    connection.execute("""
        CREATE TABLE IF NOT EXISTS etl_audit (
            audit_id INTEGER PRIMARY KEY AUTOINCREMENT,
            pipeline_name TEXT NOT NULL,
            run_id TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT,
            source_record_count INTEGER DEFAULT 0,
            valid_record_count INTEGER DEFAULT 0,
            rejected_record_count INTEGER DEFAULT 0,
            loaded_record_count INTEGER DEFAULT 0,
            pipeline_status TEXT NOT NULL,
            error_message TEXT
        )
    """)

    connection.commit()


def start_audit(pipeline_name, run_id):
    """
    Record the start of an ETL pipeline run.
    """

    connection = get_connection()

    try:
        create_audit_table(connection)

        connection.execute(
            """
            INSERT INTO etl_audit (
                pipeline_name,
                run_id,
                start_time,
                pipeline_status
            )
            VALUES (?, ?, ?, ?)
            """,
            (
                pipeline_name,
                run_id,
                str(datetime.utcnow()),
                "STARTED"
            )
        )

        connection.commit()

    finally:
        connection.close()


def complete_audit(
    run_id,
    status,
    source_count=0,
    valid_count=0,
    rejected_count=0,
    loaded_count=0,
    error_message=None
):
    """
    Update the audit record when a pipeline run completes.
    """

    connection = get_connection()

    try:
        connection.execute(
            """
            UPDATE etl_audit
            SET
                end_time = ?,
                source_record_count = ?,
                valid_record_count = ?,
                rejected_record_count = ?,
                loaded_record_count = ?,
                pipeline_status = ?,
                error_message = ?
            WHERE run_id = ?
            """,
            (
                str(datetime.utcnow()),
                source_count,
                valid_count,
                rejected_count,
                loaded_count,
                status,
                error_message,
                run_id
            )
        )

        connection.commit()

    finally:
        connection.close()
