"""Model registry for registering, fetching, and managing ML models.

Acts as a central gateway for all machine learning models in the platform, 
providing metadata tracking and supporting future model plug-ins.
"""

from typing import Any, Dict, List, Optional
from app.utils.logger import get_logger

logger = get_logger(__name__)

class ModelRegistry:
    """Registry managing instantiated ML model references, lifecycles, and metadata."""
    
    _registry: Dict[str, Any] = {}
    _metadata: Dict[str, Dict[str, Any]] = {}

    @classmethod
    def register_model(cls, model_name: str, model_instance: Any, metadata: Optional[Dict[str, Any]] = None) -> None:
        """Registers a model instance under a key.

        Args:
            model_name: Unique name identifier.
            model_instance: Model service instance.
            metadata: Optional dictionary tracking parameters or versions.
        """
        cls._registry[model_name] = model_instance
        cls._metadata[model_name] = metadata or {}
        logger.info(f"ModelRegistry: Registered model '{model_name}'")

    @classmethod
    def get_model(cls, model_name: str) -> Any:
        """Fetches a registered model instance by name.

        Args:
            model_name: Registered model key.

        Returns:
            Any: The registered model instance.
        """
        if not cls.model_exists(model_name):
            raise KeyError(f"Model '{model_name}' not registered in ModelRegistry.")
        return cls._registry[model_name]

    @classmethod
    def load_model(cls, model_name: str, path: str) -> Any:
        """Loads model parameters from storage for a registered model.

        Args:
            model_name: Registered model key.
            path: Absolute or relative filepath.

        Returns:
            Any: Loaded model instance.
        """
        model = cls.get_model(model_name)
        if hasattr(model, "load_model"):
            model.load_model(path)
            logger.info(f"ModelRegistry: Successfully loaded parameters for '{model_name}' from {path}")
        return model

    @classmethod
    def list_models(cls) -> List[str]:
        """Lists all registered model names.

        Returns:
            List[str]: List of registered keys.
        """
        return list(cls._registry.keys())

    @classmethod
    def model_exists(cls, model_name: str) -> bool:
        """Checks if a model is currently registered.

        Args:
            model_name: Model name key.

        Returns:
            bool: True if registered, False otherwise.
        """
        return model_name in cls._registry

    @classmethod
    def delete_model(cls, model_name: str) -> None:
        """Removes a model from the registry.

        Args:
            model_name: Model name key to delete.
        """
        if cls.model_exists(model_name):
            del cls._registry[model_name]
            if model_name in cls._metadata:
                del cls._metadata[model_name]
            logger.info(f"ModelRegistry: Deleted model '{model_name}'")
        else:
            logger.warning(f"ModelRegistry: Attempted to delete non-existent model '{model_name}'")

    @classmethod
    def get_metadata(cls, model_name: str) -> Dict[str, Any]:
        """Gets metadata for a registered model.

        Args:
            model_name: Model name key.

        Returns:
            Dict[str, Any]: Metadata dictionary.
        """
        if not cls.model_exists(model_name):
            raise KeyError(f"Model '{model_name}' not registered in ModelRegistry.")
        return cls._metadata.get(model_name, {})
