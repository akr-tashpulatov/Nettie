import io
import zipfile
from xml.etree import ElementTree as ET

from ..application.dtos import OptionDto, ParsedQuestionDto
from ..domain.exceptions import EmptyDocxError, InvalidDocxError, InvalidQuestionError

_WORD_NS = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"

_QUESTION_TAG = "<q>"
_CORRECT_TAG = "<va>"
_OPTION_TAG = "<v>"


class DocxQuestionParser:
    """Parses questions out of a .docx file.

    Expected format: each paragraph begins with a tag — `<q>` a question,
    `<va>` the correct answer, `<v>` a wrong answer. A `<q>` opens a new
    question; every `<va>`/`<v>` until the next `<q>` is one of its options.
    """

    def parse(self, content: bytes) -> list[ParsedQuestionDto]:
        questions: list[ParsedQuestionDto] = []
        text: str | None = None
        options: list[OptionDto] = []

        for paragraph in self._paragraphs(content):
            if paragraph.startswith(_QUESTION_TAG):
                if text is not None:
                    questions.append(self._build(text, options))
                text = paragraph[len(_QUESTION_TAG) :].strip()
                options = []
            elif paragraph.startswith(_CORRECT_TAG):
                options.append(
                    OptionDto(
                        text=paragraph[len(_CORRECT_TAG) :].strip(), is_correct=True
                    )
                )
            elif paragraph.startswith(_OPTION_TAG):
                options.append(
                    OptionDto(
                        text=paragraph[len(_OPTION_TAG) :].strip(), is_correct=False
                    )
                )

        if text is not None:
            questions.append(self._build(text, options))

        if not questions:
            raise EmptyDocxError()
        return questions

    @staticmethod
    def _build(text: str, options: list[OptionDto]) -> ParsedQuestionDto:
        if len(options) < 2 or sum(1 for o in options if o.is_correct) != 1:
            raise InvalidQuestionError(
                f"Question {text!r} must have at least two options and exactly "
                "one correct answer (a single <va>)."
            )
        return ParsedQuestionDto(text=text, options=options)

    @staticmethod
    def _paragraphs(content: bytes) -> list[str]:
        try:
            with zipfile.ZipFile(io.BytesIO(content)) as archive:
                xml = archive.read("word/document.xml")
        except (zipfile.BadZipFile, KeyError) as exc:
            raise InvalidDocxError() from exc

        root = ET.fromstring(xml)
        paragraphs = []
        for paragraph in root.iter(f"{_WORD_NS}p"):
            runs = [t.text for t in paragraph.iter(f"{_WORD_NS}t") if t.text]
            paragraphs.append("".join(runs).strip())
        return paragraphs
