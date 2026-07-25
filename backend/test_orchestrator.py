import asyncio
from app.orchestrator.engine import InvestigationOrchestrator
from app.config import PipelineConfig
from app.services.pipeline import AMLPipeline
import logging

logging.basicConfig(level=logging.INFO)

async def run_test():
    print("Initializing Pipeline...")
    config = PipelineConfig(
        remove_duplicates=True, validate_amounts=True, save_rejected_rows=True,
        generate_metadata=True, generate_report=True, sort_records=True,
        use_cache=True, reports_dir="reports", rejected_dir="reports/rejected",
        cache_dir=".cache", feature_store_dir=".feature_store"
    )
    pipeline = AMLPipeline(config)
    dataset_path = "IBM AML Transaction Dataset (IBM AMLSim)/transactions.csv"
    if not __import__('os').path.exists(dataset_path):
        dataset_path = "../" + dataset_path
    
    print("Running Pipeline...")
    pipeline_res = pipeline.run(dataset_path)
    
    print("Initializing Orchestrator...")
    orchestrator = InvestigationOrchestrator()
    
    print("Running Investigation for C_8392...")
    result = await orchestrator.investigate("C_8392", pipeline_res)
    print("--- RESULT ---")
    print(f"Customer: {result.customer_id}")
    print(f"Recommendation: {result.recommendation}")
    print(f"Risk Score: {result.risk_score}")
    print(f"Rule Hits: {len(result.rule_hits)}")
    print(f"Timeline Events: {len(result.timeline)}")
    print("Executive Summary:")
    print(result.executive_summary)

if __name__ == "__main__":
    asyncio.run(run_test())
