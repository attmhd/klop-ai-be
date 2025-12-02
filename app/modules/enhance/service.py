import logging

from app.shared.llm_client import BaseLLMClient
from app.shared.toon_parser import parse_toon_string

# Import Prompt dan Schema khusus modul Enhance
from .prompts import ENHANCE_SYSTEM_PROMPT
from .schemas import EnhanceData, EnhanceRequest

logger = logging.getLogger(__name__)


class EnhanceService:
    def __init__(self):
        # Inisialisasi Client Gemini
        self.llm = BaseLLMClient()

    async def enhance_question(self, payload: EnhanceRequest) -> EnhanceData:
        try:
            # 1. Prepare User Prompt
            # Menyusun input string sesuai format yang diminta System Prompt
            user_content = (
                f"Role: {payload.role}\n"
                f"Location: {payload.location}\n"
                f"Level: {payload.level}\n"
                f"Criteria: {payload.criteria}\n"
                f"Original Question: {payload.question_to_enhance}"
            )

            # 2. Call LLM
            logger.info(f"Enhancing question for role: {payload.role}")

            raw_toon_response = await self.llm.call_llm(
                system_prompt=ENHANCE_SYSTEM_PROMPT,
                user_prompt=user_content,
                json_mode=False,
                temperature=0.4,
            )

            # 3. Parse & Validate
            parsed_dict = parse_toon_string(raw_toon_response)

            # Kita gabungkan data dari input user (original_text)
            # dengan hasil dari AI (enhanced_text & improvement_notes)
            return EnhanceData(original_text=payload.question_to_enhance, **parsed_dict)

        except Exception as e:
            logger.error(f"Enhance Service Error: {str(e)}")
            raise e
