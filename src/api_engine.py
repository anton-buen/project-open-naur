"""
LLM-powered architectural audit engine for cross-domain alignment analysis.

This module orchestrates structured reasoning over project communication ledgers
using the OpenAI API, extracting domain constraints, risk assessments, and terminology
normalization through Pydantic-validated JSON schemas.
"""

import json
import os
from typing import List, Literal

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel, Field

load_dotenv()

client = OpenAI(
    base_url="https://opencode.ai/zen/v1",
    api_key=os.getenv("OPENCODE_API_KEY"),
)


class JargonTerm(BaseModel):
    """Represents a caught terminology collision and its strict definition."""

    term: str = Field(description="The vague buzzword caught in the ledger")
    definition: str = Field(description="The strict, highly technical definition")


class DomainConstraint(BaseModel):
    """Represents an architectural constraint isolated to a specific engineering discipline."""

    domain: Literal["PROD", "FE", "BE", "DEVOPS", "DATA", "UI"] = Field(
        description="The discipline acronym"
    )
    business_impact: str = Field(
        description="The layman translation of the blocker"
    )
    deep_dive: str = Field(
        description="The hardcore, code-level architectural constraint"
    )
    risk_level: Literal["LOW", "MEDIUM", "HIGH"] = Field(description="Risk severity")


class ArchitecturalAudit(BaseModel):
    """
    Structured output of a complete architectural audit.

    Contains global risk assessment, missing disciplinary perspectives,
    isolated domain constraints, and terminology normalization results.
    """

    global_risk_score: Literal["LOW", "MEDIUM", "HIGH"] = Field(
        description="Overall risk"
    )
    global_rationale: str = Field(description="Executive summary")
    missing_chairs: List[str] = Field(description="Missing disciplines")
    constraints: List[DomainConstraint]
    jargon_caught: List[JargonTerm] = Field(description="Caught jargon")


def run_architectural_audit(
    chat_ledger: str, target_model: str = "deepseek-v4-flash-free"
) -> ArchitecturalAudit:
    """
    Execute a structured LLM-powered architectural audit over a project communication ledger.

    Analyzes cross-domain blast radius, identifies missing disciplinary perspectives
    ("Missing Chairs"), normalizes terminology collisions, and produces risk-scored
    architectural constraints.

    Args:
        chat_ledger (str): Raw chronological communication log from the project ledger.
        target_model (str): OpenAI model identifier. Defaults to deepseek-v4-flash-free.

    Returns:
        ArchitecturalAudit: Fully validated Pydantic model containing global risk,
            isolated constraints, missing roles, and normalized terminology.
    """
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
            {"role": "user", "content": f"Here is the raw chat ledger:\n\n{chat_ledger}"},
        ],
        response_format={"type": "json_object"},
        temperature=0.1,
    )

    raw_json_string = response.choices[0].message.content
    return ArchitecturalAudit.model_validate_json(raw_json_string)