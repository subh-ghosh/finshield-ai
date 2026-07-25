"""Intelligent schema mapper for identifying and resolving dataset column aliases."""

from typing import Dict, List

class SchemaMapper:
    """Automatically maps variations of AML transaction columns to canonical names.

    Supports extensible aliases and case-insensitive matching.
    """
    
    # Map of canonical column names to their recognized raw dataset aliases
    ALIASES: Dict[str, List[str]] = {
        "customer_id": ["customer_id", "cust_id", "customer", "client_id", "client"],
        "transaction_id": ["transaction_id", "tx_id", "id", "transaction_id_val", "tx_id_val"],
        "sender_account": ["sender_account", "sender_account_id", "sender_id", "sender", "from_account", "from_acc"],
        "receiver_account": ["receiver_account", "receiver_account_id", "receiver_id", "receiver", "to_account", "to_acc"],
        "timestamp": ["timestamp", "transaction_time", "time", "tx_time", "date"],
        "amount": ["amount", "tx_amount", "transaction_amount", "amt", "value"],
        "currency": ["currency", "ccy", "tx_currency"],
        "country": ["country", "tx_country", "sender_country", "receiver_country"],
        "transaction_type": ["transaction_type", "tx_type", "type", "transaction_type_val"],
        "account_id": ["account_id", "acc_id", "account"]
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
            col_lower = col.lower()
            for canonical, aliases in cls.ALIASES.items():
                if col_lower in [alias.lower() for alias in aliases]:
                    if canonical not in mapped_canonicals:
                        mappings[col] = canonical
                        mapped_canonicals.add(canonical)
                        break
        return mappings
