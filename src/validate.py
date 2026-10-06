from collections import Counter


VALID_TRANSACTION_TYPES = {"DEBIT", "CREDIT"}
VALID_STATUSES = {"COMPLETED", "PENDING", "FAILED"}
VALID_CHANNELS = {"CARD", "ACH", "ATM", "WIRE"}


def validate_transactions(records):
    """
    Validate banking transactions using business and data-quality rules.

    Returns:
        tuple: (valid_records, rejected_records)
    """

    valid_records = []
    rejected_records = []

    transaction_ids = [
        record["transaction_id"]
        for record in records
        if record.get("transaction_id")
    ]

    duplicate_ids = {
        transaction_id
        for transaction_id, count in Counter(transaction_ids).items()
        if count > 1
    }

    for record in records:
        errors = []

        # Required fields
        required_fields = [
            "transaction_id",
            "account_id",
            "customer_id",
            "transaction_type",
            "currency",
            "transaction_timestamp",
            "transaction_status",
            "channel",
            "last_updated",
        ]

        for field in required_fields:
            if not record.get(field):
                errors.append(f"Missing required field: {field}")

        # Duplicate transaction check
        if record.get("transaction_id") in duplicate_ids:
            errors.append("Duplicate transaction ID")

        # Amount validation
        if record.get("transaction_amount", 0) <= 0:
            errors.append("Transaction amount must be greater than zero")

        # Transaction type validation
        if record.get("transaction_type") not in VALID_TRANSACTION_TYPES:
            errors.append("Invalid transaction type")

        # Status validation
        if record.get("transaction_status") not in VALID_STATUSES:
            errors.append("Invalid transaction status")

        # Channel validation
        if record.get("channel") not in VALID_CHANNELS:
            errors.append("Invalid transaction channel")

        # Currency validation
        if record.get("currency") != "USD":
            errors.append("Unsupported currency")

        if errors:
            rejected_record = record.copy()
            rejected_record["validation_errors"] = errors
            rejected_records.append(rejected_record)
        else:
            valid_records.append(record)

    print(f"Valid records: {len(valid_records)}")
    print(f"Rejected records: {len(rejected_records)}")

    return valid_records, rejected_records
