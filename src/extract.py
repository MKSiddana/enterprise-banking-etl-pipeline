import csv
from datetime import datetime
from pathlib import Path


SOURCE_FILE = Path("data/sample_transactions.csv")


def extract_transactions(source_file=SOURCE_FILE):
    """
    Extract banking transaction records from the source CSV file.

    Returns:
        list[dict]: Parsed transaction records.
    """

    records = []

    with open(source_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row in reader:
            row["transaction_amount"] = float(
                row["transaction_amount"]
            )

            row["transaction_timestamp"] = datetime.strptime(
                row["transaction_timestamp"],
                "%Y-%m-%d %H:%M:%S"
            )

            row["last_updated"] = datetime.strptime(
                row["last_updated"],
                "%Y-%m-%d %H:%M:%S"
            )

            records.append(row)

    print(f"Extracted {len(records)} transaction records.")

    return records


if __name__ == "__main__":
    transactions = extract_transactions()

    for transaction in transactions[:5]:
        print(transaction)
