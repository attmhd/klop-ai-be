import logging

from app.shared.llm_client import BaseLLMClient
from app.shared.toon_parser import parse_toon_string

from .prompts import (
    COMPREHENSIVE_PROMPT,
    ENHANCE_QUESTION_PROMPT,
    GENERATE_QUESTION_PROMPT,
)

# Import Schema & Prompts
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

    # --- Helper Private ---
    async def _call_llm(self, system_prompt: str, user_content: str) -> dict:
        try:
            raw_response = await self.llm.call_llm(
                system_prompt=system_prompt,
                user_prompt=user_content,
                json_mode=False,
                temperature=0.4,
            )
            return parse_toon_string(raw_response)
        except Exception as e:
            logger.error(f"LLM Call Error: {str(e)}")
            raise e

    # GENERATE (Simple)
    async def create_question(
        self, payload: CreateQuestionRequest
    ) -> SimpleQuestionResponse:
        user_content = f"Title: {payload.title}\nDescription: {payload.description}"
        data = await self._call_llm(GENERATE_QUESTION_PROMPT, user_content)
        return SimpleQuestionResponse(**data)

    # ENHANCE (Rewrite)
    async def enhance_question(
        self, payload: QuestionRequest
    ) -> SimpleQuestionResponse:
        user_content = (
            f"Title: {payload.title}\n"
            f"Description: {payload.description}\n"
            f"Draft Question: {payload.question}"
        )
        data = await self._call_llm(ENHANCE_QUESTION_PROMPT, user_content)
        return SimpleQuestionResponse(**data)

    # COMPREHENSIVE (Full Package)
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

        if not payload.isAnswerOptions:
            data["answerOptions"] = None
            data["isAnswerOptions"] = None

        return ComprehensiveResponse(**data)
