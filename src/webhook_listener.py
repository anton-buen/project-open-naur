"""
GitHub pull request webhook listener and autonomous architectural audit responder.

Listens for GitHub PR events, extracts PR metadata, runs structured architectural
audits, and posts analysis results back to the PR as formatted comments.
"""

import os
from typing import Dict, Any

import httpx
from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, Request

from src.api_engine import run_architectural_audit

load_dotenv()

app = FastAPI(title="Open Naur CI/CD Gatekeeper")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def process_pull_request(pr_data: Dict[str, Any]) -> None:
    """
    Extract PR metadata, execute architectural audit, and post results to GitHub.

    Parses the GitHub PR payload, constructs a simulated ledger from PR title and
    description, runs the LLM-powered audit, formats results as Markdown, and
    posts them as a comment back to the PR.

    Args:
        pr_data (Dict[str, Any]): Deserialized GitHub webhook payload.
    """
    pr_number = pr_data["number"]
    repo_full_name = pr_data["repository"]["full_name"]
    pr_title = pr_data["pull_request"]["title"]
    pr_body = pr_data["pull_request"]["body"] or "No description provided."

    simulated_ledger = (
        f"[Frontend Engineer] Proposed Architecture in PR: {pr_title}\n\n"
        f"Description: {pr_body}"
    )

    try:
        audit = run_architectural_audit(simulated_ledger)
    except Exception as e:
        print(f"Audit failed: {e}")
        return

    comment_body = "## Open Naur Architectural Audit\n\n"
    comment_body += f"**Global Alignment Risk:** `{audit.global_risk_score}`\n\n"
    comment_body += f"> {audit.global_rationale}\n\n"

    if audit.missing_chairs:
        comment_body += f"**MISSING:** {', '.join(audit.missing_chairs)}\n\n"

    comment_body += "### Domains\n\n"
    for constraint in audit.constraints:
        comment_body += (
            f"- **{constraint.domain} (`{constraint.risk_level}`)**: "
            f"{constraint.business_impact}\n"
        )

    if audit.jargon_caught:
        comment_body += "\n### Glossary\n\n"
        for term in audit.jargon_caught:
            comment_body += f"- **{term.term}**: {term.definition}\n"

    url = (
        f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    )
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }

    with httpx.Client() as client:
        response = client.post(url, headers=headers, json={"body": comment_body})
        if response.status_code != 201:
            print(f"Failed to post comment: {response.text}")


@app.post("/webhook/github")
async def github_webhook(
    request: Request,
    background_tasks: BackgroundTasks,
    x_github_event: str = Header(None),
) -> Dict[str, str]:
    """
    Listen for GitHub PR events and queue architectural audit in background.

    Only processes pull_request events with actions in ["opened", "edited", "reopened"]
    to avoid redundant audits on minor activity (e.g., comment additions).

    Args:
        request (Request): FastAPI request object containing JSON payload.
        background_tasks (BackgroundTasks): FastAPI background task queue.
        x_github_event (str): GitHub event type header.

    Returns:
        Dict[str, str]: Status message indicating whether event was processed.
    """
    if x_github_event == "pull_request":
        payload = await request.json()
        action = payload.get("action")

        if action in ["opened", "edited", "reopened"]:
            background_tasks.add_task(process_pull_request, payload)
            return {"status": "Naur Audit Triggered"}

    return {"status": "Event Ignored"}