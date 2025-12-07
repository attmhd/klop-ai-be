import logging

from app.shared.json_parser import parse_json_response
from app.shared.llm_client import BaseLLMClient

from .prompts import (
    ANSWER_OPTIONS_PROMPT,
    EXPECTED_CHOICE_PROMPT,
    EXPECTED_ESSAY_PROMPT,
)
from .schemas import (
    AnswerOptionsResponse,
    ExpectedAnswerResponse,
    ExpectedChoiceRequest,
    ExpectedEssayRequest,
)

logger = logging.getLogger(__name__)


class AnswerService:
    def __init__(self):
        self.llm = BaseLLMClient()

    async def _call_llm(self, prompt, content):
        raw = await self.llm.call_llm(prompt, content, json_mode=True, temperature=0.5)
        return parse_json_response(raw)

    async def generate_essay_key(
        self, payload: ExpectedEssayRequest
    ) -> ExpectedAnswerResponse:
        user_content = (
            f"Title: {payload.title}\n"
            f"Description: {payload.description}\n"
            f"Question: {payload.question}"
        )
        raw_data = await self._call_llm(EXPECTED_ESSAY_PROMPT, user_content)

        # Ensure we have a mapping/dict with string keys
        if not isinstance(raw_data, dict):
            logger.warning("LLM returned non-dict data for essay key: %r", raw_data)
            raw_data = {"expectedAnswer": str(raw_data)}

        # Extract required field(s) for ExpectedAnswerResponse
        expected_answer = raw_data.get("expectedAnswer")
        if expected_answer is None:
            # Fallback: try common alternate keys or build from content
            expected_answer = raw_data.get("answer") or raw_data.get("response") or ""

        return ExpectedAnswerResponse(expectedAnswer=expected_answer)

    # --- ENDPOINT /expected/choices ---
    async def select_best_choice(
        self, payload: ExpectedChoiceRequest
    ) -> ExpectedAnswerResponse:
        # Format opsi agar mudah dibaca AI
        formatted_opts = "\n".join([f"- {opt}" for opt in payload.answerOptions])

        user_content = (
            f"Title: {payload.title}\n"
            f"Description: {payload.description}\n"
            f"Question: {payload.question}\n\n"
            f"AVAILABLE OPTIONS (Select One):\n{formatted_opts}"
        )

        raw_data = await self._call_llm(EXPECTED_CHOICE_PROMPT, user_content)

        # Ensure we have a mapping/dict with string keys
        if not isinstance(raw_data, dict):
            logger.warning(
                "LLM returned non-dict data for choice selection: %r", raw_data
            )
            raw_data = {"expectedAnswer": str(raw_data)}

        # Extract required field(s) for ExpectedAnswerResponse
        expected_answer = raw_data.get("expectedAnswer")
        if expected_answer is None:
            # Fallback: try common alternate keys or build from content
            expected_answer = raw_data.get("answer") or raw_data.get("response") or ""

        return ExpectedAnswerResponse(expectedAnswer=expected_answer)

    async def generate_options(
        self, payload: ExpectedEssayRequest
    ) -> AnswerOptionsResponse:
        user_content = (
            f"Title: {payload.title}\n"
            f"Description: {payload.description}\n"
            f"Question: {payload.question}"
        )

        raw_data = await self._call_llm(ANSWER_OPTIONS_PROMPT, user_content)

        # Ensure we have a mapping/dict with string keys
        if not isinstance(raw_data, dict):
            logger.warning(
                "LLM returned non-dict data for answer options: %r", raw_data
            )
            raw_data = {}

        # Extract answer options robustly
        answer_options = raw_data.get("answerOptions")
        if not isinstance(answer_options, list):
            # Try alternate keys or convert from string
            alt = raw_data.get("options") or raw_data.get("answers")
            if isinstance(alt, list):
                answer_options = alt
            elif isinstance(alt, str):
                # Split lines and clean bullet markers
                answer_options = [
                    line.strip().lstrip("-").strip()
                    for line in alt.splitlines()
                    if line.strip()
                ]
            else:
                answer_options = []

        # Extract expected/correct answer robustly
        expected_answer = raw_data.get("expectedAnswer")
        if expected_answer is None:
            expected_answer = raw_data.get("answer") or ""
        if not isinstance(expected_answer, str):
            expected_answer = str(expected_answer)

        return AnswerOptionsResponse(
            answerOptions=answer_options, expectedAnswer=expected_answer
        )
