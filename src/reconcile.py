from load import get_connection


def reconcile_transactions(source_records):
    """
    Reconcile the current incremental source batch
    against the corresponding records in the target.

    Checks:
    1. Incremental source vs target record count
    2. Transaction amount totals
    3. Signed/net amount totals
    """

    if not source_records:
        print("No records available for reconciliation.")
        return True

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # -------------------------------------------------
        # Source metrics
        # -------------------------------------------------

        source_count = len(source_records)

        source_amount = round(
            sum(
                record["transaction_amount"]
                for record in source_records
            ),
            2
        )

        source_signed_amount = round(
            sum(
                record["signed_amount"]
                for record in source_records
            ),
            2
        )

        # -------------------------------------------------
        # Get IDs belonging to this incremental batch
        # -------------------------------------------------

        transaction_ids = [
            record["transaction_id"]
            for record in source_records
        ]

        placeholders = ",".join(
            "?"
            for _ in transaction_ids
        )

        # -------------------------------------------------
        # Target metrics for the SAME batch only
        # -------------------------------------------------

        query = f"""
            SELECT
                COUNT(*),
                COALESCE(SUM(transaction_amount), 0),
                COALESCE(SUM(signed_amount), 0)
            FROM banking_transactions
            WHERE transaction_id IN ({placeholders})
        """

        cursor.execute(
            query,
            transaction_ids
        )

        (
            target_count,
            target_amount,
            target_signed_amount
        ) = cursor.fetchone()

        target_amount = round(
            target_amount,
            2
        )

        target_signed_amount = round(
            target_signed_amount,
            2
        )

        # -------------------------------------------------
        # Reconciliation comparisons
        # -------------------------------------------------

        count_match = (
            source_count == target_count
        )

        amount_match = (
            source_amount == target_amount
        )

        signed_amount_match = (
            source_signed_amount
            == target_signed_amount
        )

        reconciliation_passed = all([
            count_match,
            amount_match,
            signed_amount_match
        ])

        # -------------------------------------------------
        # Display reconciliation results
        # -------------------------------------------------

        print(
            "\n--- Incremental Reconciliation ---"
        )

        print(
            f"Source count: {source_count} | "
            f"Target count: {target_count}"
        )

        print(
            f"Source amount: {source_amount} | "
            f"Target amount: {target_amount}"
        )

        print(
            "Source signed amount: "
            f"{source_signed_amount} | "
            "Target signed amount: "
            f"{target_signed_amount}"
        )

        if reconciliation_passed:
            print("Reconciliation PASSED.")
        else:
            print("Reconciliation FAILED.")

        return reconciliation_passed

    finally:
        connection.close()
