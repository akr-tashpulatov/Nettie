from dataclasses import dataclass


@dataclass(frozen=True)
class ExplanationPrompt:
    """The two-part instruction handed to an LLM to explain a question.

    Framework-free on purpose: the domain decides *what* the model is asked,
    while the infrastructure adapter maps this to a concrete provider's message
    format.
    """

    system: str
    user: str


@dataclass(frozen=True)
class ExplainableQuestion:
    """A question with its answer, ready to be explained to a student."""

    question_id: int
    text: str
    options: list[str]
    correct_answer: str

    def build_prompt(self) -> ExplanationPrompt:
        numbered = "\n".join(
            f"{index}. {option}" for index, option in enumerate(self.options, start=1)
        )
        system = (
            "You are a patient tutor helping a student learn. Explain the concept "
            "behind a multiple-choice question so the student understands why the "
            "correct answer is right and, briefly, why the tempting alternatives "
            "are wrong. Teach the underlying idea rather than just naming the "
            "answer. Keep it concise (a short paragraph), clear, and encouraging. "
            "Do not use Markdown headings."
        )
        user = (
            f"Question:\n{self.text}\n\n"
            f"Options:\n{numbered}\n\n"
            f"The correct answer is: {self.correct_answer}\n\n"
            "Explain the concept so I understand why this answer is correct."
        )
        return ExplanationPrompt(system=system, user=user)
