import time
import uuid

from extract import extract_transactions
from validate import validate_transactions
from transform import transform_transactions
from load import load_transactions
from reconcile import reconcile_transactions
from audit import start_audit, complete_audit
from watermark import (
    get_watermark,
    filter_incremental_records,
    update_watermark
)


PIPELINE_NAME = "enterprise_banking_etl"
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 2


def run_pipeline():
    """
    Execute the end-to-end incremental banking ETL pipeline.
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
        # -------------------------------------------------
        # Extract
        # -------------------------------------------------

        source_records = extract_transactions()
        source_count = len(source_records)

        print(f"Source records extracted: {source_count}")

        # -------------------------------------------------
        # Read previous watermark
        # -------------------------------------------------

        last_watermark = get_watermark()

        print(
            "Previous successful watermark:",
            last_watermark
        )

        # -------------------------------------------------
        # Incremental filtering
        # -------------------------------------------------

        incremental_records = filter_incremental_records(
            source_records,
            last_watermark
        )

        # If nothing changed, finish successfully
        if not incremental_records:
            print("No new or changed records to process.")

            complete_audit(
                run_id=run_id,
                status="SUCCESS",
                source_count=source_count,
                valid_count=0,
                rejected_count=0,
                loaded_count=0
            )

            return

        # -------------------------------------------------
        # Validate
        # -------------------------------------------------

        valid_records, rejected_records = (
            validate_transactions(
                incremental_records
            )
        )

        valid_count = len(valid_records)
        rejected_count = len(rejected_records)

        # -------------------------------------------------
        # Transform
        # -------------------------------------------------

        transformed_records = (
            transform_transactions(
                valid_records
            )
        )

        # -------------------------------------------------
        # Load with retry handling
        # -------------------------------------------------

        for attempt in range(
            1,
            MAX_RETRIES + 1
        ):
            try:
                print(
                    f"Load attempt "
                    f"{attempt}/{MAX_RETRIES}"
                )

                loaded_count = (
                    load_transactions(
                        transformed_records
                    )
                )

                break

            except Exception as error:
                print(
                    f"Load attempt {attempt} "
                    f"failed: {error}"
                )

                if attempt == MAX_RETRIES:
                    raise

                time.sleep(
                    RETRY_DELAY_SECONDS
                )

        # -------------------------------------------------
        # Source-to-target reconciliation
        # -------------------------------------------------

        reconciliation_passed = (
            reconcile_transactions(
                transformed_records
            )
        )

        if not reconciliation_passed:
            raise ValueError(
                "Source-to-target "
                "reconciliation failed."
            )
# -------------------------------------------------
# Update watermark only after successful
# load and reconciliation
# -------------------------------------------------

update_watermark(
    incremental_records
)

# -------------------------------------------------
# Mark pipeline successful only after
# the watermark update completes
# -------------------------------------------------

complete_audit(
    run_id=run_id,
    status="SUCCESS",
    source_count=source_count,
    valid_count=valid_count,
    rejected_count=rejected_count,
    loaded_count=loaded_count
)

        print(
            "\nBanking ETL pipeline "
            "completed successfully."
        )

        print(
            f"Run ID: {run_id}"
        )

        print(
            f"Source records: "
            f"{source_count}"
        )

        print(
            f"Incremental records: "
            f"{len(incremental_records)}"
        )

        print(
            f"Valid records: "
            f"{valid_count}"
        )

        print(
            f"Rejected records: "
            f"{rejected_count}"
        )

        print(
            f"Loaded records: "
            f"{loaded_count}"
        )

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

        print(
            "\nBanking ETL pipeline failed."
        )

        print(
            f"Run ID: {run_id}"
        )

        print(
            f"Error: {error}"
        )

        raise


if __name__ == "__main__":
    run_pipeline()
