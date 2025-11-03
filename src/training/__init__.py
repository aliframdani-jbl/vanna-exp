try:
    from .training_manager import TrainingManager
    __all__ = ['TrainingManager']
except ImportError:
    __all__ = []