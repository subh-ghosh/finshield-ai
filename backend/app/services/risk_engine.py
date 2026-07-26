"""Risk Scoring stage — combines rule triggers and anomaly flags into a priority score."""

import pandas as pd


class RiskEngine:
    """Combines rule triggers and anomaly scores into a unified alert risk priority score."""

    # Weight mapping: rule_score and anomaly_score contributions
    RULE_WEIGHT = 0.4
    ANOMALY_WEIGHT = 0.6

    def run(self, dataframe: pd.DataFrame) -> pd.DataFrame:
        """Scores transaction risks by combining rule engine and anomaly detection signals.

        Risk Score = 0.4 * normalized_rule_score + 0.6 * anomaly_flag
        Categorizes into: LOW / MEDIUM / HIGH / CRITICAL

        Args:
            dataframe: Input DataFrame with optional rule_score and prediction columns.

        Returns:
            pd.DataFrame: DataFrame with added risk_priority_score and risk_category columns.
        """
        df = dataframe.copy()

        # Normalize rule score to [0, 1]
        if "rule_score" in df.columns:
            max_rule = df["rule_score"].max()
            df["_rule_norm"] = df["rule_score"] / max_rule if max_rule > 0 else 0.0
        else:
            df["_rule_norm"] = 0.0

        # Anomaly flag: Isolation Forest returns -1 (anomaly) or 1 (normal)
        if "prediction" in df.columns:
            df["_anomaly_flag"] = (df["prediction"] == -1).astype(float)
        else:
            df["_anomaly_flag"] = 0.0

        # Combined risk priority score [0, 1]
        df["risk_priority_score"] = (
            self.RULE_WEIGHT * df["_rule_norm"] +
            self.ANOMALY_WEIGHT * df["_anomaly_flag"]
        ).clip(0, 1)

        # Risk category
        df["risk_category"] = pd.cut(
            df["risk_priority_score"],
            bins=[-0.001, 0.35, 0.65, 0.85, 1.0],
            labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        ).astype(str)

        # Clean up temp columns
        df.drop(columns=["_rule_norm", "_anomaly_flag"], inplace=True, errors="ignore")

        return df
