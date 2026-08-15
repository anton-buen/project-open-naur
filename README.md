

# Open Naur

> **Catch cross-domain architectural blast radius before shipping code.**
> *Inspired by Peter Naur’s "Programming as Theory Building".*

---

### The Problem: Alignment Tax

Software projects rarely fail because engineers lack the technical ability to write code—they fail because disciplines operate in isolated mental models. A single unvalidated assumption (e.g., using a 1Hz polling interval or database-level 2PC locking) cascades into thread pool exhaustion, stale data pipelines, and broken UX.

This is the **Alignment Tax**: hours wasted in debate, uncoordinated constraints, and late-stage integration rewrites. Accelerating execution with AI code generators without addressing underlying alignment simply builds the wrong software faster.

Open Naur intercepts architectural friction upstream before code is merged.

---

### The Evolution: Project Naur vs. Open Naur

What started as **Project Naur**—a local, human-in-the-loop hackathon proof-of-concept built for the **IBM Bob AI Builders Challenge**—has evolved into **Open Naur**: an autonomous, zero-friction web application and CI/CD gatekeeper accessible to any team.

| Dimension | Project Naur (PoC) | Open Naur (Current) |
| --- | --- | --- |
| **Execution Plane** | Local IDE only (VS Code / IBM Bob) | Live Web Application + Cloud CI/CD Gatekeeper |
| **Protocol & Trigger** | Manual human-in-the-loop MCP triggers | Autonomous LLM execution engine & Webhook listeners |
| **Interface** | IDE terminal + local Streamlit UI | Responsive Web UI + automated GitHub PR comments |
| **Output / Utility** | Local database view | Full Markdown Spec Exports (`.md`) + Live GitHub Audits |

---

### Core Capabilities

* **Multi-Domain Risk Assessment:** Evaluates architectural discussions across 6 key disciplines (`PROD`, `FE`, `BE`, `DEVOPS`, `DATA`, `UI`).
* **"Missing Chairs" Detection:** Automatically identifies absent team disciplines (e.g., Backend or Data Engineering) when high-stakes decisions are made.
* **Instant Jargon Translation:** Features interactive "Translate" toggles to convert complex engineering blockers into business impacts for stakeholders.
* **SRS Markdown Export:** Compiles global summaries, domain card constraints, and project glossaries into executive-ready `.md` architectural specs.
* **Autonomous GitHub PR Gatekeeper:** Monitors incoming Pull Requests via Webhook and automatically posts zero-emoji architectural audit comments directly to PR discussions.

---

### System Architecture & Flow

Open Naur runs on a decoupled architecture separating the interactive Streamlit workspace from the asynchronous FastAPI webhook gatekeeper. Both components share a single, typed LLM orchestration engine (`src/api_engine.py`) backed by Pydantic schema validation.

```text
[ User / Web UI ]                       [ GitHub Pull Request Event ]
        │                                             │
        ▼                                             ▼
[ app.py (Streamlit Workspace) ]       [ src/webhook_listener.py (FastAPI) ]
        │                                             │
        ├──────────────────────┬──────────────────────┤
        │                      │                      │
        ▼                      ▼                      ▼
[ src/state_manager.py ]  [ src/api_engine.py ]  [ GitHub REST API ]
  (SQLite Persistence)    (Pydantic Schema)       (PR Audit Comments)
                               │
                               ▼
                    [ DeepSeek / OpenAI API ]

```

---

### Tech Stack

| Layer | Technology | Function |
| --- | --- | --- |
| **Frontend Workspace** | Streamlit, HTML5, CSS3 | Renders multi-role chat ledger, domain risk cards, and markdown export engine. |
| **CI/CD Gatekeeper** | FastAPI, Uvicorn, httpx | Ingests GitHub `pull_request` webhooks and posts automated audit comments. |
| **AI Orchestration** | OpenAI SDK, Pydantic | Executes structured JSON prompting and enforces strict type signatures on LLM outputs. |
| **Persistence** | SQLite3 (Native) | Handles session isolation, message ledgers, and project dictionary glossary states. |

---

### Quickstart Setup

#### Prerequisites

* Python 3.10 or higher
* OpenAI or OpenCode API Key

#### 1. Clone & Install Dependencies

```bash
git clone https://github.com/anton-buen/project-open-naur.git
cd project-open-naur

python -m venv venv
# On Windows:
venv\Scripts\activate
# On Mac/Linux:
source venv/bin/activate

pip install -r requirements.txt

```

#### 2. Configure Environment Secrets

Create a `.env` file in the root directory:

```env
OPENCODE_API_KEY=your_llm_api_key_here
GITHUB_TOKEN=your_github_personal_access_token_here

```

#### 3. Run the Web Application

```bash
streamlit run app.py

```

*Access the interactive app at `http://localhost:8501`.*

#### 4. Run the CI/CD Webhook Listener (Optional)

```bash
uvicorn src.webhook_listener:app --reload --port 8000

```

*Connect to GitHub PR webhooks using `ngrok http 8000` or deploy to a cloud container.*

---

### GitHub PR Gatekeeper Setup

1. Expose your local webhook listener via `ngrok` or deploy `src/webhook_listener.py` to a cloud server.
2. In your GitHub repository, go to **Settings > Webhooks > Add webhook**.
3. Set **Payload URL** to `[https://your-domain.com/webhook/github](https://your-domain.com/webhook/github)`.
4. Set **Content type** to `application/json`.
5. Under **Which events would you like to trigger this webhook?**, select **Let me select individual events** and check **Pull requests**.
6. Save the webhook. Every opened or updated Pull Request will now automatically receive an Open Naur architectural audit comment.

---

## 7. Team & License

**Built for:** AI Builders Challenge with IBM Bob (Wildcard Challenge - Build Intelligent Systems for the Future of Work)

**The Team:**
* **Antonio III Buenafe** – Developer
* **Links:** [GitHub Profile](https://github.com/anton-buen) | [LinkedIn Profile](www.linkedin.com/in/antonio-iii-buenafe-488a1936b)

**Tech Stack:** IBM Bob, Model Context Protocol (MCP), Python 3.10+, SQLite, Streamlit 

**License:** Distributed under the [MIT License](https://opensource.org/licenses/MIT).
<br>
> *"Programming properly should be regarded as an activity by which the programmers form or achieve a certain kind of insight, a theory, of the matters at hand."* — Peter Naur

<br>

---

### 8. Project Evolution & History

Great software is discovered through trial, error, and a stubborn belief that teams can always find a better way to work together. Naur is the proud result of those necessary failures and architectural pivots. If you want to explore the journey of how this tool evolved from a raw, ambitious concept into the deterministic MCP protocol it is today, you can read the original build history here:

**[Explore how it started differently](https://github.com/anton-buen/cognitive-alignment-engine)**

