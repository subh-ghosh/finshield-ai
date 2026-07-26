"""Configuration constants for AML rule thresholds and contributing risk scores."""

# 1. High Velocity Rule Config (Z-Score > 2.5)
HIGH_VELOCITY_THRESHOLD: float = 2.5
HIGH_VELOCITY_SCORE: int = 15

# 2. Structuring Rule Config (Ratio)
STRUCTURING_THRESHOLD: float = 0.5
STRUCTURING_SCORE: int = 25

# 3. Smurfing Rule Config (Structuring * Velocity)
SMURFING_THRESHOLD: float = 0.25
SMURFING_SCORE: int = 20

# 4. Round Amount Rule Config
ROUND_AMOUNT_THRESHOLD: float = 0.8
ROUND_AMOUNT_SCORE: int = 10

# 5. Rapid Cash Out Rule Config
HIGH_CASHOUT_THRESHOLD: float = 0.8
HIGH_CASHOUT_SCORE: int = 15

# 6. Recipient Diversity Rule Config
RECIPIENT_DIVERSITY_THRESHOLD: float = 10.0
RECIPIENT_DIVERSITY_SCORE: int = 10

# 7. Dormant Account Rule Config
DORMANT_ACCOUNT_THRESHOLD: float = 30.0
DORMANT_ACCOUNT_SCORE: int = 10

# 8. Large Transaction Rule Config
LARGE_TRANSACTION_THRESHOLD: float = 10000.0
LARGE_TRANSACTION_SCORE: int = 15
