from typing import Annotated

from fastapi import APIRouter, Depends, File, UploadFile, status

from src.core.exceptions import error_responses
from src.modules.auth.api.guards import AdminUser, StudentUser

from ..application.dtos import (
    OptionDto,
    QuestionCreateDto,
    QuestionUpdateDto,
    TestCreateDto,
    TestsQueryDto,
    TestUpdateDto,
)
from ..application.test_service import TestService
from ..domain.exceptions import (
    EmptyDocxError,
    InvalidDocxError,
    InvalidQuestionError,
    QuestionNotFoundError,
    TestNameAlreadyExistsError,
    TestNotFoundError,
)
from .dependencies import get_test_service
from .schemas import (
    ImportResult,
    QuestionCreate,
    QuestionResponse,
    QuestionUpdate,
    StudentTestsList,
    TestCreate,
    TestResponse,
    TestsList,
    TestUpdate,
)

router = APIRouter()

admin_router = APIRouter(prefix="/admin/tests", tags=["Tests (Admin)"])
student_router = APIRouter(prefix="/student/tests", tags=["Tests (Student)"])

MAX_DOCX_SIZE = 10 * 1024 * 1024
_DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"


@admin_router.post(
    "",
    response_model=TestResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a test",
    description="Creates a test with a name and a session mode (30 or 40 "
    "questions drawn per session).",
    responses=error_responses(TestNameAlreadyExistsError),
)
async def create_test(
    payload: TestCreate,
    service: Annotated[TestService, Depends(get_test_service)],
    admin: AdminUser,
) -> TestResponse:
    test = await service.create(
        TestCreateDto(name=payload.name, mode=payload.mode, created_by=admin.sub)
    )
    return TestResponse.from_entity(test)


@admin_router.get(
    "",
    response_model=TestsList,
    summary="List tests",
    description="Returns a paginated list of tests with their question counts.",
)
async def list_tests(
    query: Annotated[TestsQueryDto, Depends()],
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> TestsList:
    page = await service.get_tests(query)
    return TestsList.from_domain(page)


@admin_router.get(
    "/{test_id}",
    response_model=TestResponse,
    summary="Get a test",
    description="Returns a single test with its question count.",
    responses=error_responses(TestNotFoundError),
)
async def get_test(
    test_id: int,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> TestResponse:
    test = await service.get_by_id(test_id)
    return TestResponse.from_entity(test)


@admin_router.patch(
    "/{test_id}",
    response_model=TestResponse,
    summary="Update a test",
    description="Updates a test's name and/or session mode.",
    responses=error_responses(TestNotFoundError, TestNameAlreadyExistsError),
)
async def update_test(
    test_id: int,
    payload: TestUpdate,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> TestResponse:
    test = await service.update(
        test_id, TestUpdateDto(**payload.model_dump(exclude_unset=True))
    )
    return TestResponse.from_entity(test)


@admin_router.delete(
    "/{test_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a test",
    description="Deletes a test and all of its questions.",
    responses=error_responses(TestNotFoundError),
)
async def delete_test(
    test_id: int,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> None:
    await service.delete(test_id)


@admin_router.post(
    "/{test_id}/questions/import",
    response_model=ImportResult,
    status_code=status.HTTP_201_CREATED,
    summary="Import questions from a .docx file",
    description="Parses a .docx file (paragraphs tagged `<q>` question, `<va>` "
    "correct answer, `<v>` wrong answer) and appends the questions to the test.",
    responses=error_responses(
        TestNotFoundError, EmptyDocxError, InvalidDocxError, InvalidQuestionError
    ),
)
async def import_questions(
    test_id: int,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
    file: Annotated[UploadFile, File()],
) -> ImportResult:
    content = await _read_docx(file)
    count = await service.import_questions(test_id, content)
    return ImportResult(imported_count=count)


@admin_router.post(
    "/{test_id}/questions",
    response_model=QuestionResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Add a question",
    description="Manually adds a single question with its options to the test.",
    responses=error_responses(TestNotFoundError, InvalidQuestionError),
)
async def add_question(
    test_id: int,
    payload: QuestionCreate,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> QuestionResponse:
    question = await service.add_question(
        test_id,
        QuestionCreateDto(
            text=payload.text,
            options=[OptionDto(o.text, o.is_correct) for o in payload.options],
        ),
    )
    return QuestionResponse.from_entity(question)


@admin_router.get(
    "/{test_id}/questions",
    response_model=list[QuestionResponse],
    summary="List a test's questions",
    description="Returns every question of a test with its options and the "
    "correct answer flagged. Admin-only.",
    responses=error_responses(TestNotFoundError),
)
async def list_questions(
    test_id: int,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> list[QuestionResponse]:
    questions = await service.list_questions(test_id)
    return [QuestionResponse.from_entity(q) for q in questions]


@admin_router.patch(
    "/{test_id}/questions/{question_id}",
    response_model=QuestionResponse,
    summary="Update a question",
    description="Replaces a question's text and options.",
    responses=error_responses(
        TestNotFoundError, QuestionNotFoundError, InvalidQuestionError
    ),
)
async def update_question(
    test_id: int,
    question_id: int,
    payload: QuestionUpdate,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> QuestionResponse:
    question = await service.update_question(
        test_id,
        question_id,
        QuestionUpdateDto(
            text=payload.text,
            options=[OptionDto(o.text, o.is_correct) for o in payload.options],
        ),
    )
    return QuestionResponse.from_entity(question)


@admin_router.delete(
    "/{test_id}/questions/{question_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a question",
    description="Removes a single question from the test.",
    responses=error_responses(TestNotFoundError, QuestionNotFoundError),
)
async def delete_question(
    test_id: int,
    question_id: int,
    service: Annotated[TestService, Depends(get_test_service)],
    _: AdminUser,
) -> None:
    await service.delete_question(test_id, question_id)


@student_router.get(
    "",
    response_model=StudentTestsList,
    summary="List available tests",
    description="Returns tests the student can take — only those with at least "
    "`mode` questions. Correct answers are never exposed here.",
)
async def list_available_tests(
    query: Annotated[TestsQueryDto, Depends()],
    service: Annotated[TestService, Depends(get_test_service)],
    _: StudentUser,
) -> StudentTestsList:
    query.eligible_only = True
    page = await service.get_tests(query)
    return StudentTestsList.from_domain(page)


async def _read_docx(file: UploadFile) -> bytes:
    if file.content_type not in (_DOCX_MIME, "application/octet-stream") and not (
        file.filename or ""
    ).endswith(".docx"):
        raise InvalidDocxError()
    content = await file.read(MAX_DOCX_SIZE + 1)
    if len(content) > MAX_DOCX_SIZE:
        raise InvalidDocxError("The uploaded file is too large.")
    if not content:
        raise EmptyDocxError()
    return content


router.include_router(admin_router)
router.include_router(student_router)
