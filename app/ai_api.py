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


class SkillRecommendationsRequest(BaseModel):
    query: str = Field(..., description="Partial skill name or keyword to get recommendations for")
    context: Optional[str] = Field(None, description="Additional context like field of study or job role")


class SkillRecommendationsResponse(BaseModel):
    skills: list[str] = Field(..., description="List of recommended skills")


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
        logger.error("GOOGLE_GENAI_API_KEY not set")
        raise HTTPException(status_code=500, detail="AI service not configured")

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
            logger.error("Gemini returned empty text")
            raise HTTPException(status_code=502, detail="AI generated empty content")
        return GenerateJobDescriptionResponse(text=text)
    except Exception as e:
        logger.error(f"Gemini generation error: {e}")
        raise HTTPException(status_code=502, detail="AI generation failed")


@router.post("/skill-recommendations", response_model=SkillRecommendationsResponse)
async def get_skill_recommendations(payload: SkillRecommendationsRequest) -> SkillRecommendationsResponse:
    """Get skill recommendations based on partial input using Gemini AI"""
    api_key = os.getenv("GOOGLE_GENAI_API_KEY")
    if not api_key:
        logger.error("GOOGLE_GENAI_API_KEY not set")
        raise HTTPException(status_code=500, detail="AI service not configured")

    try:
        import google.generativeai as genai  # type: ignore
    except Exception as e:
        logger.error(f"google-generativeai import failed: {e}")
        raise HTTPException(status_code=500, detail="AI service not available on server")

    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-1.5-flash")
        
        # Build context-aware prompt
        context_text = f" in {payload.context}" if payload.context else ""
        prompt = (
            f"You are a career advisor helping international students in Australia. "
            f"Given the partial skill input '{payload.query}'{context_text}, suggest 8-12 relevant, specific skills that would be valuable for job applications. "
            f"Focus on:\n"
            f"- Technical skills relevant to the field\n"
            f"- Soft skills valued by Australian employers\n"
            f"- Skills that complement the input\n"
            f"- Industry-standard terminology\n\n"
            f"Return only a simple list of skills, one per line, without numbering or bullet points. "
            f"Make them specific and actionable (e.g., 'Python Programming' not just 'Programming')."
        )

        response = model.generate_content(prompt)
        text = getattr(response, "text", None) or ""
        
        if not text:
            logger.error("Gemini returned empty text for skill recommendations")
            raise HTTPException(status_code=502, detail="AI generated empty content")
        
        # Parse the response into a list of skills
        skills = []
        for line in text.strip().split('\n'):
            skill = line.strip()
            if skill and not skill.startswith(('1.', '2.', '3.', '4.', '5.', '6.', '7.', '8.', '9.', '-', '*')):
                skills.append(skill)
        
        # Limit to 12 skills and filter out duplicates
        unique_skills = list(dict.fromkeys(skills))[:12]
        
        if not unique_skills:
            logger.error("No valid skills parsed from AI response")
            raise HTTPException(status_code=502, detail="AI generated invalid skill format")
        
        return SkillRecommendationsResponse(skills=unique_skills)
        
    except Exception as e:
        logger.error(f"Gemini skill recommendations error: {e}")
        raise HTTPException(status_code=502, detail="AI skill recommendations failed")
