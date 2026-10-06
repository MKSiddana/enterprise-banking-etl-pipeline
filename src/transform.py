from datetime import datetime


def transform_transactions(records):
    """
    Standardize and enrich validated banking transactions.

    Returns:
        list[dict]: Transformed transaction records.
    """

    transformed_records = []

    for record in records:
        transformed = record.copy()

        # Standardize text fields
        transformed["transaction_type"] = (
            transformed["transaction_type"].strip().upper()
        )

        transformed["transaction_status"] = (
            transformed["transaction_status"].strip().upper()
        )

        transformed["channel"] = (
            transformed["channel"].strip().upper()
        )

        transformed["currency"] = (
            transformed["currency"].strip().upper()
        )

        # Standardize monetary precision
        transformed["transaction_amount"] = round(
            transformed["transaction_amount"],
            2
        )

        # Derive transaction date
        transformed["transaction_date"] = (
            transformed["transaction_timestamp"].date()
        )

        # Create signed amount for downstream analytics
        if transformed["transaction_type"] == "CREDIT":
            transformed["signed_amount"] = transformed[
                "transaction_amount"
            ]
        else:
            transformed["signed_amount"] = -transformed[
                "transaction_amount"
            ]

        # Add ETL processing timestamp
        transformed["etl_processed_at"] = datetime.utcnow()

        transformed_records.append(transformed)

    print(
        f"Transformed {len(transformed_records)} transaction records."
    )

    return transformed_records
