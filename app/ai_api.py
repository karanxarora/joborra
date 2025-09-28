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
    model: Optional[str] = Field(default="gemini-2.5-flash")
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
    role_category = ctx.get("role_category", "")
    company_name = ctx.get("company_name", "Our Company")
    salary = ctx.get("salary", "Competitive")
    intl = ctx.get("international_student_friendly")
    visasp = ctx.get("visa_sponsorship")
    intl_txt = "Yes" if intl else "No"
    visasp_txt = "Yes" if visasp else "No"
    
    # Get skills from payload
    skills = payload.skills or []
    skills_text = ", ".join(skills) if skills else "relevant skills"

    return (
        "You are an expert HR copywriter specializing in Australian job descriptions for international students. "
        "Create a professional, industry-standard job description using the following EXACT format:\n\n"
        
        "FORMAT REQUIREMENTS:\n"
        "- Use HTML formatting with proper tags\n"
        "- Use <strong> tags for bold headings (NOT <h3> tags)\n"
        "- Follow this exact structure with these exact headings\n"
        "- Use Australian spelling throughout\n"
        "- Target 300-400 words total\n"
        "- Add one blank line between each section\n"
        "- DO NOT wrap the output in markdown code blocks (no ```html or ```)\n"
        "- Return only the HTML content directly\n\n"
        
        "REQUIRED STRUCTURE (follow EXACTLY with proper spacing):\n"
        "<strong>About the Role</strong>\n"
        "<p>[2-3 sentences describing the role, company culture, and team environment. Use the actual company name: {company_name}]</p>\n"
        "<br><br>\n"
        
        "<strong>Key Responsibilities</strong>\n"
        "<ul>\n"
        "<li>[Responsibility 1 - specific and actionable]</li>\n"
        "<li>[Responsibility 2 - specific and actionable]</li>\n"
        "<li>[Responsibility 3 - specific and actionable]</li>\n"
        "<li>[Responsibility 4 - specific and actionable]</li>\n"
        "<li>[Responsibility 5 - specific and actionable]</li>\n"
        "</ul>\n"
        "<br><br>\n"
        
        "<strong>What We're Looking For</strong>\n"
        "<ul>\n"
        "<li>[Essential requirement 1]</li>\n"
        "<li>[Essential requirement 2]</li>\n"
        "<li>[Essential requirement 3]</li>\n"
        "<li>[Preferred skill or experience]</li>\n"
        "<li>[Soft skill or attitude]</li>\n"
        "</ul>\n"
        "<br><br>\n"
        
        "<strong>What We Offer</strong>\n"
        "<ul>\n"
        "<li>[Benefit 1 - e.g., flexible hours, training opportunities]</li>\n"
        "<li>[Benefit 2 - e.g., supportive team environment]</li>\n"
        "<li>[Benefit 3 - e.g., career development opportunities]</li>\n"
        "</ul>\n"
        
        f"JOB CONTEXT:\n"
        f"- Title: {title}\n"
        f"- Company: {company_name}\n"
        f"- Location: {location}\n"
        f"- Employment type: {employment_type}\n"
        f"- Role category: {role_category}\n"
        f"- Key skills: {skills_text}\n"
        f"- International student friendly: {intl_txt}\n"
        f"- Visa sponsorship available: {visasp_txt}\n\n"
        
        "IMPORTANT NOTES:\n"
        "- ALWAYS use the actual company name '{company_name}' in the description, never use '[Company Name]' or placeholders\n"
        "- Make it welcoming to international students\n"
        "- Emphasize learning opportunities and growth\n"
        "- Use inclusive, encouraging language\n"
        "- Focus on transferable skills and cultural diversity\n"
        "- If visa sponsorship is available, mention it naturally in the benefits\n"
        "- Keep the tone professional but approachable\n"
        "- Use <strong> tags for headings, not <h3> tags\n"
        "- CRITICAL: Add <br><br> after each section to create proper spacing\n"
        "- Follow the exact structure above with <br><br> tags between sections\n\n"
        
        "Generate the complete job description following this exact format:"
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
        model_name = payload.model or "gemini-2.5-flash"
        model = genai.GenerativeModel(model_name)
        prompt = payload.prompt or _build_prompt_from_context(payload)

        resp = model.generate_content(prompt)
        text = getattr(resp, "text", None) or "".join(getattr(resp, "candidates", []) or [])
        if not text:
            logger.error("Gemini returned empty text")
            raise HTTPException(status_code=502, detail="AI generated empty content")
        
        # Clean up any markdown code block syntax that might be added
        text = text.strip()
        if text.startswith("```html"):
            text = text[7:]  # Remove ```html
        if text.startswith("```"):
            text = text[3:]  # Remove ```
        if text.endswith("```"):
            text = text[:-3]  # Remove trailing ```
        text = text.strip()
        
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
        model = genai.GenerativeModel("gemini-2.5-flash")
        
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
