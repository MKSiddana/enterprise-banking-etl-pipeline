import time
import uuid

from extract import extract_transactions
from validate import validate_transactions
from transform import transform_transactions
from load import load_transactions
from reconcile import reconcile_transactions
from audit import start_audit, complete_audit


PIPELINE_NAME = "enterprise_banking_etl"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def run_pipeline():
    """
    Execute the end-to-end banking ETL pipeline.
    """

    run_id = str(uuid.uuid4())

    source_count = 0
    valid_count = 0
    rejected_count = 0
    loaded_count = 0

    start_audit(
        pipeline_name=PIPELINE_NAME,
        run_id=run_id
    )

    try:
        # ---------------------------------------------
        # Extract
        # ---------------------------------------------

        source_records = extract_transactions()
        source_count = len(source_records)

        # ---------------------------------------------
        # Validate
        # ---------------------------------------------

        valid_records, rejected_records = (
            validate_transactions(source_records)
        )

        valid_count = len(valid_records)
        rejected_count = len(rejected_records)

        # ---------------------------------------------
        # Transform
        # ---------------------------------------------

        transformed_records = transform_transactions(
            valid_records
        )

        # ---------------------------------------------
        # Load with retry handling
        # ---------------------------------------------

        for attempt in range(1, MAX_RETRIES + 1):
            try:
                loaded_count = load_transactions(
                    transformed_records
                )
                break

            except Exception as error:
                print(
                    f"Load attempt {attempt} failed: {error}"
                )

                if attempt == MAX_RETRIES:
                    raise

                time.sleep(RETRY_DELAY_SECONDS)

        # ---------------------------------------------
        # Reconcile
        # ---------------------------------------------

        reconciliation_passed = reconcile_transactions(
            transformed_records
        )

        if not reconciliation_passed:
            raise ValueError(
                "Source-to-target reconciliation failed."
            )

        # ---------------------------------------------
        # Successful audit completion
        # ---------------------------------------------

        complete_audit(
            run_id=run_id,
            status="SUCCESS",
            source_count=source_count,
            valid_count=valid_count,
            rejected_count=rejected_count,
            loaded_count=loaded_count
        )

        print("\nBanking ETL pipeline completed successfully.")
        print(f"Run ID: {run_id}")

    except Exception as error:

        complete_audit(
            run_id=run_id,
            status="FAILED",
            source_count=source_count,
            valid_count=valid_count,
            rejected_count=rejected_count,
            loaded_count=loaded_count,
            error_message=str(error)
        )

        print("\nBanking ETL pipeline failed.")
        print(f"Run ID: {run_id}")
        print(f"Error: {error}")

        raise


if __name__ == "__main__":
    run_pipeline()
