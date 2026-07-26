"""Tool: GET /api/v1/eda/summary — dataset-level Exploratory Data Analysis."""

from typing import Any, Dict
from app.planner.tools.base_tool import BaseTool, ToolMetadata


class EDAAnalysisTool(BaseTool):
    """Runs Exploratory Data Analysis on the full IBM AML transaction dataset.

    Use for queries like:
    - "Analyse this dataset for suspicious activity"
    - "Give me an overview of the data"
    - "What does the dataset look like?"
    - "How many flagged transactions are there?"
    """

    @property
    def metadata(self) -> ToolMetadata:
        return ToolMetadata(
            name="eda_analysis",
            description=(
                "Performs Exploratory Data Analysis on the full IBM AML dataset. "
                "Returns: total transactions, fraud rate, transaction type distribution, "
                "amount statistics, risk score distribution, top risky customers, "
                "and anomaly detection baseline counts. "
                "Use for broad dataset-level queries, NOT for single customer lookups."
            ),
            endpoint="/api/v1/eda/summary",
            http_method="GET",
            input_schema={},
            output_schema={
                "dataset_summary": "dict",
                "transaction_type_distribution": "dict",
                "amount_statistics_usd": "dict",
                "risk_distribution": "dict",
                "top_10_risky_customers": "list",
                "anomaly_detection": "dict",
            }
        )

    async def execute(self, client: Any, customer_id: str = "", **kwargs: Any) -> Dict[str, Any]:
        """Calls GET /api/v1/eda/summary.

        Args:
            client: FinShieldAPIClient instance.
            customer_id: Not used for EDA (dataset-wide analysis).

        Returns:
            EDA summary dict with dataset stats, distributions, and top risky customers.
        """
        return await client.get_eda_summary()
