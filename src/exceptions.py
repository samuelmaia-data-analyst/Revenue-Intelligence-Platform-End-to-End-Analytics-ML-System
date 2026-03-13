class PipelineError(Exception):
    """Base exception for pipeline failures."""


class DataQualityError(PipelineError):
    """Raised when dataset validation fails."""


class PipelineStageError(PipelineError):
    """Raised when a pipeline stage cannot complete successfully."""
