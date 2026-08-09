import os
from pydantic import BaseModel, Field
from typing import List
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://opencode.ai/zen/v1",
    api_key=os.getenv("OPENCODE_API_KEY"),
)


class DomainConstraint(BaseModel):
    domain: str = Field(description="The discipline (e.g., 'FRONTEND', 'BACKEND', 'PRODUCT')")
    business_impact: str = Field(description="The layman translation of the blocker")
    deep_dive: str = Field(description="The hardcore, code-level architectural constraint")
    risk_level: str = Field(description="LOW, MEDIUM, or HIGH")

class ArchitecturalAudit(BaseModel):
    global_risk_score: str = Field(description="Overall risk of the proposal: LOW, MEDIUM, or HIGH")
    global_rationale: str = Field(description="Executive summary of the cross-domain friction")
    missing_chairs: List[str] = Field(description="Which disciplines are dangerously absent from this chat?")
    constraints: List[DomainConstraint]
    jargon_caught: List[str] = Field(description="Vague buzzwords that need normalizing in the Project Dictionary")


def run_architectural_audit(chat_ledger: str, target_model: str = "meta-llama/llama-3.1-70b-instruct") -> ArchitecturalAudit:
    """
    Ingests raw chat history and returns a strictly typed JSON audit.
    Swap `target_model` at any time to avoid vendor lock-in.
    """
    
    system_prompt = """
    You are Project Naur, an ontological linter and Principal Architect. 
    Analyze the following project chat ledger. 
    Calculate the cross-domain blast radius, catch vague jargon, and identify if any vital engineering roles (Missing Chairs) are absent from the decision-making process.
    Be brutally objective and highly technical in your deep dives.
    """

    response = client.beta.chat.completions.parse(
        model=target_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the raw chat ledger:\n\n{chat_ledger}"}
        ],
        response_format=ArchitecturalAudit,
    )

    return response.choices[0].message.parsed