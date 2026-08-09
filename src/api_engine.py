import os
import json
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

def run_architectural_audit(chat_ledger: str, target_model: str = "deepseek-v4-flash-free") -> ArchitecturalAudit:
    """
    Ingests raw chat history and returns a strictly typed JSON audit.
    Uses a prompt-injected JSON schema fallback for third-party compatibility.
    """
    
    # 1. Dynamically extract the schema from our Pydantic model
    schema_definition = ArchitecturalAudit.model_json_schema()
    
    # 2. Inject the schema directly into the system prompt
    system_prompt = f"""
    You are Project Naur, an ontological linter and Principal Architect. 
    Analyze the following project chat ledger. 
    Calculate the cross-domain blast radius, catch vague jargon, and identify if any vital engineering roles (Missing Chairs) are absent from the decision-making process.
    Be brutally objective and highly technical in your deep dives.
    
    You MUST respond in pure JSON format. Your output must strictly adhere to the following JSON schema:
    {json.dumps(schema_definition)}
    """

    # 3. Use the standard `.create()` instead of `.parse()`
    response = client.chat.completions.create(
        model=target_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the raw chat ledger:\n\n{chat_ledger}"}
        ],
        response_format={"type": "json_object"}, # Standard JSON mode
        temperature=0.1, # Keep it highly deterministic
    )

    # 4. Extract the raw JSON string and validate it through Pydantic
    raw_json_string = response.choices[0].message.content
    
    return ArchitecturalAudit.model_validate_json(raw_json_string)