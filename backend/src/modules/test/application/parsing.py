from typing import Protocol

from .dtos import ParsedQuestionDto


class IQuestionParser(Protocol):
    """Port for turning an uploaded document's bytes into questions.

    Implemented in the infrastructure layer (e.g. a .docx parser); the service
    depends only on this abstraction.
    """

    def parse(self, content: bytes) -> list[ParsedQuestionDto]: ...
