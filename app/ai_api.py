from typing import Any, Optional, Dict
import os
import logging

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


class GenerateJobDescriptionRequest(BaseModel):
    title: Optional[str] = None
    skills: Optional[list[str]] = None
    prompt: Optional[str] = None
    model: Optional[str] = Field(default="gemini-1.5-flash")
    context: Optional[Dict[str, Any]] = None


class GenerateJobDescriptionResponse(BaseModel):
    text: str


def _build_prompt_from_context(payload: GenerateJobDescriptionRequest) -> str:
    # Construct a reasonable prompt if none supplied
    ctx = payload.context or {}
    title = payload.title or ctx.get("title") or "Team Member"
    location = ctx.get("location", "Australia")
    employment_type = ctx.get("employment_type", "Part-time")
    salary = ctx.get("salary", "Competitive")
    intl = ctx.get("international_student_friendly")
    visasp = ctx.get("visa_sponsorship")
    intl_txt = "Yes" if intl else "No"
    visasp_txt = "Yes" if visasp else "No"

    return (
        "You are an expert HR copywriter. Write a concise, friendly, student-inclusive job description.\n\n"
        "Constraints:\n"
        "- 160–260 words.\n"
        "- Use Australian spelling.\n"
        "- Plain text paragraphs and short bullet lists only; no markdown headers.\n"
        "- Emphasise international student friendliness and legal work constraints if applicable.\n\n"
        f"Job context:\n- Title: {title}\n- Location: {location}\n- Employment type: {employment_type}\n- Pay text: {salary}\n"
        f"- International student friendly: {intl_txt}\n- Visa sponsorship available: {visasp_txt}\n\n"
        "Output sections (no labels needed):\n"
        "1) 2–3 sentence overview of the role and team.\n"
        "2) 4–6 bullet points of day‑to‑day responsibilities.\n"
        "3) 3–5 bullet points of what you’re looking for (soft skills welcomed)."
    )


@router.post("/generate/job-description", response_model=GenerateJobDescriptionResponse)
async def generate_job_description(payload: GenerateJobDescriptionRequest) -> GenerateJobDescriptionResponse:
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        logger.warning("GOOGLE_GENAI_API_KEY not set; returning fallback text")
        # Fallback plain text so frontend can still display something
        title = payload.title or (payload.context or {}).get("title") or "Team Member"
        fallback = (
            f"About this role\n\nWe are looking for a {title} to join our team.\n\n"
            "Responsibilities\n- Deliver excellent service\n- Collaborate with team members\n- Communicate clearly and proactively\n- Be reliable and punctual\n\n"
            "What we’re looking for\n- Positive attitude\n- Team player\n- Willingness to learn\n"
        )
        return GenerateJobDescriptionResponse(text=fallback)

    try:
        import google.generativeai as genai  # type: ignore
    except Exception as e:
        logger.error(f"google-generativeai import failed: {e}")
        raise HTTPException(status_code=500, detail="AI service not available on server")

    try:
        genai.configure(api_key=api_key)
        model_name = payload.model or "gemini-1.5-flash"
        model = genai.GenerativeModel(model_name)
        prompt = payload.prompt or _build_prompt_from_context(payload)

        resp = model.generate_content(prompt)
        text = getattr(resp, "text", None) or "".join(getattr(resp, "candidates", []) or [])
        if not text:
            logger.warning("Gemini returned empty text; using fallback")
            text = (
                "About this role\n\nWe are hiring for this position. You'll work with a supportive team to deliver great outcomes.\n\n"
                "Responsibilities\n- Provide excellent service\n- Collaborate with teammates\n- Communicate clearly\n\n"
                "What we’re looking for\n- Positive attitude\n- Reliability\n- Willingness to learn\n"
            )
        return GenerateJobDescriptionResponse(text=text)
    except Exception as e:
        logger.error(f"Gemini generation error: {e}")
        raise HTTPException(status_code=502, detail="AI generation failed")
