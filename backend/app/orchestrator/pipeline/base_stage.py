from abc import ABC, abstractmethod
from app.orchestrator.models.context import InvestigationContext
from app.models.pipeline_result import PipelineResult

class BaseStage(ABC):
    
    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the stage."""
        pass
        
    @abstractmethod
    async def execute(self, context: InvestigationContext, pipeline_res: PipelineResult) -> None:
        """Executes the pipeline stage, modifying the context in place."""
        pass
