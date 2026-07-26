"""Graph type definitions and constants."""

from enum import Enum

class NodeType(str, Enum):
    """Enumeration of all supported graph node types."""
    CUSTOMER = "CUSTOMER"
    ACCOUNT = "ACCOUNT"
    TRANSACTION = "TRANSACTION"
    DEVICE = "DEVICE"
    PHONE = "PHONE"
    IP = "IP"
    COMPANY = "COMPANY"
    DIRECTOR = "DIRECTOR"
    MERCHANT = "MERCHANT"
    COUNTRY = "COUNTRY"

class RelationshipType(str, Enum):
    """Enumeration of all supported graph relationship types."""
    OWNS_ACCOUNT = "OWNS_ACCOUNT"
    USES_DEVICE = "USES_DEVICE"
    USES_PHONE = "USES_PHONE"
    USES_IP = "USES_IP"
    WORKS_FOR = "WORKS_FOR"
    TRANSACTS_WITH = "TRANSACTS_WITH"
    SHARES_DIRECTOR = "SHARES_DIRECTOR"
    PAYS = "PAYS"
    RECEIVES = "RECEIVES"
    LOCATED_IN = "LOCATED_IN"
