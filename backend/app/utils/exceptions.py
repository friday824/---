class PipelineError(Exception):
    """Base exception for pipeline failures."""

    def __init__(self, stage: str, message: str):
        self.stage = stage
        self.message = message
        super().__init__(f"[{stage}] {message}")


class ScriptGenerationError(PipelineError):
    def __init__(self, message: str):
        super().__init__("script_gen", message)


class ImageGenerationError(PipelineError):
    def __init__(self, message: str):
        super().__init__("image_gen", message)


class TTSError(PipelineError):
    def __init__(self, message: str):
        super().__init__("tts", message)


class CompositorError(PipelineError):
    def __init__(self, message: str):
        super().__init__("compositing", message)
