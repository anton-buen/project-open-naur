# TODO: Implement FastAPI webhook receiver for GitHub PR payloads
import os
import httpx
from fastapi import FastAPI, Request, BackgroundTasks, Header
from dotenv import load_dotenv
from src.api_engine import run_architectural_audit

load_dotenv()

app = FastAPI(title="Open Naur CI/CD Gatekeeper")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

def process_pull_request(pr_data: dict):
    """Parses the PR, runs the Open Naur audit, and posts a comment back to GitHub."""
    
    pr_number = pr_data["number"]
    repo_full_name = pr_data["repository"]["full_name"]
    pr_title = pr_data["pull_request"]["title"]
    pr_body = pr_data["pull_request"]["body"] or "No description provided."
    
    # Simulate a ledger entry using the PR context
    simulated_ledger = f"[Frontend Engineer] Proposed Architecture in PR: {pr_title}\n\nDescription: {pr_body}"
    
    # 1. Trigger the autonomous brain
    try:
        audit = run_architectural_audit(simulated_ledger)
    except Exception as e:
        print(f"Audit failed: {e}")
        return
    
    # 2. Format the Naur Markdown response for GitHub
    comment_body = f"## 🛑 Open Naur Architectural Audit\n\n"
    comment_body += f"**Global Alignment Risk:** `{audit.global_risk_score}`\n\n"
    comment_body += f"> {audit.global_rationale}\n\n"
    
    if audit.missing_chairs:
        comment_body += f"**🚨 MISSING CHAIRS DETECTED:** {', '.join(audit.missing_chairs)} absent from this PR context.\n\n"
        
    comment_body += "### 🧱 Domain Constraints\n\n"
    for constraint in audit.constraints:
        comment_body += f"- **{constraint.domain} (`{constraint.risk_level}`)**: {constraint.business_impact}\n"
        
    if audit.jargon_caught:
        comment_body += "\n### 📖 Project Dictionary (Jargon Caught)\n\n"
        for term in audit.jargon_caught:
            comment_body += f"- **{term.term}**: {term.definition}\n"
            
    # 3. Post the Naur analysis back to the PR
    url = f"https://api.github.com/repos/{repo_full_name}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }
    
    with httpx.Client() as client:
        response = client.post(url, headers=headers, json={"body": comment_body})
        if response.status_code != 201:
            print(f"Failed to post comment: {response.text}")

@app.post("/webhook/github")
async def github_webhook(request: Request, background_tasks: BackgroundTasks, x_github_event: str = Header(None)):
    """Listens for GitHub PR events and queues the audit in the background."""
    if x_github_event == "pull_request":
        payload = await request.json()
        action = payload.get("action")
        
        # Only run the heavy audit on creation or major edits
        if action in ["opened", "edited", "reopened"]:
            background_tasks.add_task(process_pull_request, payload)
            return {"status": "Naur Audit Triggered"}
            
    return {"status": "Event Ignored"}