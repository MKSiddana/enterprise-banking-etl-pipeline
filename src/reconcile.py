from load import get_connection


def reconcile_transactions(source_records):
    """
    Reconcile transformed source records against the target table.

    Checks:
    1. Source vs target record count
    2. Source vs target transaction amount
    3. Source vs target signed amount
    """

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
        # Target metrics
        # -------------------------------------------------

        cursor.execute("""
            SELECT
                COUNT(*),
                COALESCE(SUM(transaction_amount), 0),
                COALESCE(SUM(signed_amount), 0)
            FROM banking_transactions
        """)

        target_count, target_amount, target_signed_amount = (
            cursor.fetchone()
        )

        target_amount = round(target_amount, 2)
        target_signed_amount = round(
            target_signed_amount,
            2
        )

        # -------------------------------------------------
        # Reconciliation results
        # -------------------------------------------------

        count_match = source_count == target_count

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

        print("\n--- Reconciliation Results ---")
        print(
            f"Source count: {source_count} | "
            f"Target count: {target_count}"
        )
        print(
            f"Source amount: {source_amount} | "
            f"Target amount: {target_amount}"
        )
        print(
            f"Source signed amount: "
            f"{source_signed_amount} | "
            f"Target signed amount: "
            f"{target_signed_amount}"
        )

        if reconciliation_passed:
            print("Reconciliation PASSED.")
        else:
            print("Reconciliation FAILED.")

        return reconciliation_passed

    finally:
        connection.close()
