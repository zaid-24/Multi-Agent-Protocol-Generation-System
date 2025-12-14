"""
Groq LLM Client for CBT Protocol Agents
Uses OpenAI-compatible API with Groq's fast inference
"""
import os
import json
from typing import Optional
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from .env file
load_dotenv()

# Configure Groq client (OpenAI-compatible)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Initialize the client
client = None
if GROQ_API_KEY:
    client = OpenAI(
        api_key=GROQ_API_KEY,
        base_url="https://api.groq.com/openai/v1",
    )

# Default model - using Llama 3.1 8B Instant for fast inference
DEFAULT_MODEL = "llama-3.1-8b-instant"


def generate_text(
    prompt: str,
    system_instruction: Optional[str] = None,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.7,
    max_tokens: int = 1024,
) -> str:
    """
    Generate text using Groq API.

    Args:
        prompt: The user prompt
        system_instruction: Optional system instruction for the model
        model_name: Model to use
        temperature: Sampling temperature (0-1)
        max_tokens: Maximum tokens to generate

    Returns:
        Generated text response
    """
    if not client:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
    )

    return response.choices[0].message.content or ""


def generate_json(
    prompt: str,
    system_instruction: Optional[str] = None,
    model_name: str = DEFAULT_MODEL,
    temperature: float = 0.3,
) -> dict:
    """
    Generate structured JSON output using Groq API.

    Args:
        prompt: The user prompt (should ask for JSON output)
        system_instruction: Optional system instruction
        model_name: Model to use
        temperature: Lower temperature for more deterministic JSON

    Returns:
        Parsed JSON dictionary
    """
    if not client:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    full_system = (system_instruction or "") + (
        "\n\nYou must respond with valid JSON only. "
        "No markdown, no explanation, no surrounding text. "
        "Do not wrap in ```json blocks."
    )

    messages = [
        {"role": "system", "content": full_system},
        {"role": "user", "content": prompt},
    ]

    response = client.chat.completions.create(
        model=model_name,
        messages=messages,
        temperature=temperature,
        max_tokens=1024,
        response_format={"type": "json_object"},
    )

    text = (response.choices[0].message.content or "").strip()
    
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to extract JSON from common wrappers like ```json ... ```
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        text = text.strip()
        return json.loads(text)


# System prompts for each agent
SYSTEM_PROMPTS = {
    "IntentInterpreter": """
You are an expert clinical psychologist specializing in CBT (Cognitive Behavioral Therapy).
Your job is to interpret and normalize user requests for CBT protocol creation.
Be concise, focus on the core therapeutic goal, and output structured summaries that
downstream agents can use. Avoid long explanations; keep to key intent, condition,
constraints, and recommended CBT approach.
""".strip(),

    "DraftingAgent": """
You are an expert CBT protocol designer.

Your primary goals:
- Create concise, structured, clinically sound CBT protocols.
- Follow the caller's requested format exactly (sections, tables, headings).
- Focus on actionable steps, exposure hierarchies (when relevant), and homework.

Guidelines:
- Prefer short, clear bullet points and numbered steps.
- Avoid long psychoeducational essays, theory lectures, or worksheets.
- Do not repeat the prompt verbatim.
- Aim for under ~400–500 words unless specifically asked for more.
""".strip(),

    "SafetyGuardian": """
You are a clinical safety reviewer for CBT protocols.

Your job:
- Identify potential harm, contraindications, and pacing issues.
- Focus especially on exposure intensity, crisis risk, and missing safety guidance.

Guidelines:
- Provide a safety score between 0.0 and 1.0.
- Highlight concrete risks and practical mitigations.
- Be direct and concise; avoid repeating the whole protocol.
- Output structured JSON as requested by the caller.
""".strip(),

    "EmpathyToneAgent": """
You are an expert in therapeutic communication and empathetic writing.

Your job:
- Evaluate CBT protocols for empathy, warmth, and alliance-building tone.
- Suggest specific, brief improvements to language and framing.

Guidelines:
- Provide an empathy score between 0.0 and 1.0.
- Emphasize validation, hope, non-judgment, and accessibility.
- Keep feedback concrete, short, and easy to apply.
- Output structured JSON as requested by the caller.
""".strip(),

    "ClinicalCritic": """
You are a senior CBT clinician reviewing protocols for clinical validity.

Your job:
- Evaluate adherence to CBT best practices and sound clinical structure.
- Focus on evidence-based techniques, pacing, and clear behavioral targets.

Guidelines:
- Provide a clinical score between 0.0 and 1.0.
- Identify key strengths and gaps concisely.
- Avoid rewriting the protocol; give targeted, high-yield feedback.
- Output structured JSON as requested by the caller.
""".strip(),

    "RevisionAgent": """
You are an expert CBT protocol editor.

Your job:
- Revise protocols based on feedback from safety, empathy, and clinical reviewers.
- Preserve what works, fix what doesn't, and keep the protocol concise and structured.

Guidelines:
- Respect the existing section structure and headings.
- Incorporate reviewer suggestions explicitly and resolve conflicts reasonably.
- Avoid adding long new sections of psychoeducation unless clearly necessary.
- Output clean, well-formatted markdown as requested by the caller.
""".strip(),
}
