import os
import json
from pydantic import BaseModel, Field
from typing import List, Literal
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    base_url="https://opencode.ai/zen/v1",
    api_key=os.getenv("OPENCODE_API_KEY"),
)

class JargonTerm(BaseModel):
    term: str = Field(description="The vague buzzword caught in the ledger")
    definition: str = Field(description="The strict, highly technical definition")

class DomainConstraint(BaseModel):
    domain: Literal["PROD", "FE", "BE", "DS", "UI", "DEVOPS", "DATA"] = Field(description="The discipline acronym")
    business_impact: str = Field(description="The layman translation of the blocker")
    deep_dive: str = Field(description="The hardcore, code-level architectural constraint")
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="Risk severity")

class ArchitecturalAudit(BaseModel):
    global_risk_score: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="Overall risk")
    global_rationale: str = Field(description="Executive summary")
    missing_chairs: List[str] = Field(description="Missing disciplines")
    constraints: List[DomainConstraint]
    jargon_caught: List[JargonTerm] = Field(description="Caught jargon")

def run_architectural_audit(chat_ledger: str, target_model: str = "deepseek-v4-flash-free") -> ArchitecturalAudit:
    schema_definition = ArchitecturalAudit.model_json_schema()
    system_prompt = f"""
    You are Project Naur, an ontological linter and Principal Architect. 
    Analyze the following project chat ledger. 
    Calculate the cross-domain blast radius, catch vague jargon, and identify if any vital engineering roles (Missing Chairs) are absent from the decision-making process.
    Be brutally objective and highly technical in your deep dives.
    
    You MUST respond in pure JSON format. Your output must strictly adhere to the following JSON schema:
    {json.dumps(schema_definition)}
    """

    response = client.chat.completions.create(
        model=target_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Here is the raw chat ledger:\n\n{chat_ledger}"}
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    raw_json_string = response.choices[0].message.content
    return ArchitecturalAudit.model_validate_json(raw_json_string)