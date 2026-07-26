"""Intelligent schema mapper for identifying and resolving dataset column aliases."""

from typing import Dict, List


class SchemaMapper:
    """Automatically maps IBM AML and other AML dataset column variations to canonical names.

    Primary dataset: IBM AML Simulation dataset (Kaggle)
      transactions.csv: TX_ID, SENDER_ACCOUNT_ID, RECEIVER_ACCOUNT_ID,
                        TX_TYPE, TX_AMOUNT, TIMESTAMP, IS_FRAUD, ALERT_ID
      accounts.csv:     ACCOUNT_ID, CUSTOMER_ID, INIT_BALANCE, COUNTRY,
                        ACCOUNT_TYPE, IS_FRAUD, TX_BEHAVIOR_ID
    """

    ALIASES: Dict[str, List[str]] = {
        "transaction_id": [
            "tx_id", "transaction_id", "id", "txn_id", "messageid", "message_id",
        ],
        "sender_account": [
            "sender_account_id", "sender_account", "sender_id", "sender",
            "from_account", "from_acc", "from_account_id",
        ],
        "receiver_account": [
            "receiver_account_id", "receiver_account", "receiver_id", "receiver",
            "to_account", "to_acc", "to_account_id",
        ],
        "transaction_type": [
            "tx_type", "transaction_type", "type", "payment_format", "payment format",
        ],
        "amount": [
            "tx_amount", "amount", "transaction_amount", "amt", "value",
            "amount_received", "amount_paid",
        ],
        "timestamp": [
            "timestamp", "transaction_time", "time", "tx_time", "date", "date_time",
        ],
        "is_fraud": [
            "is_fraud", "is_laundering", "fraud", "laundering", "label",
            "is laundering", "is_suspicious",
        ],
        "customer_id": [
            "customer_id", "cust_id", "customer", "client_id", "client",
        ],
        "country": [
            "country", "tx_country", "sender_country", "receiver_country",
            "jurisdiction", "from_bank", "to_bank",
        ],
        "currency": [
            "currency", "ccy", "tx_currency", "receiving_currency", "payment_currency",
        ],
        "account_id": [
            "account_id", "acc_id", "account",
        ],
        "alert_id": [
            "alert_id",
        ],
    }

    @classmethod
    def get_mappings(cls, columns: List[str]) -> Dict[str, str]:
        """Resolves raw/normalized columns to canonical names using the alias registry.

        Args:
            columns: List of columns in the raw DataFrame.

        Returns:
            Dict[str, str]: Mappings of source column names to canonical names.
        """
        mappings: Dict[str, str] = {}
        mapped_canonicals = set()
        for col in columns:
            col_normalized = col.lower().strip().replace(" ", "_")
            for canonical, aliases in cls.ALIASES.items():
                aliases_normalized = [a.lower().replace(" ", "_") for a in aliases]
                if col_normalized in aliases_normalized:
                    if canonical not in mapped_canonicals:
                        mappings[col] = canonical
                        mapped_canonicals.add(canonical)
                        break
        return mappings
