import logging

from app.shared.json_parser import parse_json_response
from app.shared.llm_client import BaseLLMClient

from .prompts import (
    COMPREHENSIVE_PROMPT,
    ENHANCE_QUESTION_PROMPT,
    GENERATE_QUESTION_PROMPT,
)
from .schemas import (
    ComprehensiveRequest,
    ComprehensiveResponse,
    CreateQuestionRequest,
    QuestionRequest,
    SimpleQuestionResponse,
)

logger = logging.getLogger(__name__)


class QuestionService:
    def __init__(self):
        self.llm = BaseLLMClient()

    async def _call_llm(self, system_prompt: str, user_content: str) -> dict | list:
        try:
            raw_response = await self.llm.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_content,
                json_mode=True,
                temperature=0.6,
            )
            return parse_json_response(raw_response)
        except Exception as e:
            logger.error(f"LLM Call Error: {str(e)}")
            raise e

    async def create_question(
        self, payload: CreateQuestionRequest
    ) -> SimpleQuestionResponse:
        user_content = f"Title: {payload.title}\nDescription: {payload.description}"
        data = await self._call_llm(GENERATE_QUESTION_PROMPT, user_content)

        # Normalize LLM response to a dict
        if isinstance(data, list):
            data = data[0] if data else {}
        if not isinstance(data, dict):
            data = {}

        # Ensure required field "question" is present
        question = data.get("question") or ""

        return SimpleQuestionResponse(question=question)

    async def enhance_question(
        self, payload: QuestionRequest
    ) -> SimpleQuestionResponse:
        user_content = (
            f"Title: {payload.title}\n"
            f"Description: {payload.description}\n"
            f"Draft Question: {payload.question}"
        )
        data = await self._call_llm(ENHANCE_QUESTION_PROMPT, user_content)

        # Normalize LLM response to a dict with string keys
        if isinstance(data, list):
            data = data[0] if data else {}
        if not isinstance(data, dict):
            data = {}

        # Ensure required field "question" is present
        question = data.get("question") or ""

        return SimpleQuestionResponse(question=question)

    async def create_comprehensive(
        self, payload: ComprehensiveRequest
    ) -> ComprehensiveResponse:
        req_type = "MULTIPLE CHOICE" if payload.isAnswerOptions else "ESSAY"

        user_content = (
            f"Title: {payload.title}\n"
            f"Description: {payload.description}\n"
            f"REQUESTED TYPE: {req_type}"
        )

        data = await self._call_llm(COMPREHENSIVE_PROMPT, user_content)

        # Normalize LLM response to a dict with string keys
        if isinstance(data, list):
            data = data[0] if data else {}
        if not isinstance(data, dict):
            data = {}

        # Ensure required fields are present
        question = data.get("question") or ""
        expected_answer = data.get("expectedAnswer") or ""

        # Handle answer options based on requested type
        if payload.isAnswerOptions:
            # Normalize possible keys to "answerOptions"
            answer_options = data.get("answerOptions") or data.get("options") or []
            data["answerOptions"] = answer_options
            data["isAnswerOptions"] = True
        else:
            data["answerOptions"] = None
            data["isAnswerOptions"] = False

        # Set normalized required fields back into data
        data["question"] = question
        data["expectedAnswer"] = expected_answer

        return ComprehensiveResponse(**data)
