

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

## 3. Architecture & AI Approach

I built Naur with a clear separation of concerns. The frontend presentation layer is entirely decoupled from the persistent relational ledger and the background AI orchestration loop.

**The Tech Stack**
| Component | Technology | Role in the Architecture |
| :--- | :--- | :--- |
| **Presentation Layer** | Streamlit (1.59.1), HTML5, CSS3 | Renders the team interface. Uses custom Markdown parsers and pure CSS pseudo-classes (`:checked`) to toggle technical/layman deep-dives with zero runtime lag. |
| **Persistence Ledger** | SQLite3 (Native Python) | Concurrency-safe relational database (`naur_state.db`) that acts as the single source of truth for chat histories, constraints, and the unified glossary. |
| **Protocol Engine** | `mcp` (1.28.1) | Exposes the SQLite ledger to the AI environment over standard input/output (`stdio`) channels, providing direct tool execution bindings. |
| **Logic Engine** | **IBM Bob** | The core AI model. Reads architectural threads, evaluates cross-domain friction, and fires tool parameters back to the persistence layer. |

<br> <br> 
**AI Integration: The Human-in-the-Loop Control Plane**
I wanted to push past the standard generative chatbot model. Naur utilizes agentic AI as an active, on-demand architectural validator. Because this is a ***localized proof of concept***, the orchestration engine relies on a human-in-the-loop trigger. Once initialized by the developer within the IDE workspace, the local agent executes a highly deterministic reasoning cycle.

It pulls the exact chronological communication log from the ledger via the MCP server tool. It then evaluates the active personas to determine if any vital engineering roles were missing from the conversation. Finally, the agent dispatches parallel tool calls with explicitly typed parameters back through the server, converting these payloads into atomic database mutations instantly.

<br> <br> 
**Architecture Diagram & System Flow**

This maps the live synchronization flow between the human interface, the database state, the protocol server, and the IDE linter.
<br>
```text
[ Team Member ] ➔ [ app.py (Streamlit UI) ]
                               │
               (Calls append_message, get_constraints)
                               │
                               ▼
                   [ src/state_manager.py ]
                               │
                        (SQL Read/Write)
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│               Persistence: naur_state.db (SQLite)               │
└─────────────────────────────────────────────────────────────────┘
                               ▲
                        (SQL Read/Write)
                               │
                   [ src/state_manager.py ]
                               ▲
                 (Executes sm.update_constraint())
                               │
                 [ src/mcp_server.py (stdio) ]
                               ▲
                  (Invokes Tools via stdio / MCP)
                               │
┌──────────────────────────────┴──────────────────────────────────┐
│                   IBM Bob Agent (VS Code)                       │
│    (Persona: .bob/system.md | Registration: .bob/mcp.json)      │
└─────────────────────────────────────────────────────────────────┘
```
<br>

--- 

## 4. The Quickstart Guide

Because Naur is deeply integrated with the local development environment via MCP, **it requires manual orchestration through the Bob IDE**. Consequently, there is no public URL; the application must be evaluated locally using the following:

**Prerequisites**

1. Python 3.10+
2. IBM Bob

**Phase 1: Installation & Environment Setup**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/anton-buen/Project-Naur
   cd Project-Naur

2. **Create the virtual environment:**
   Note: It must be named exactly venv as the local .bob/mcp.json schema looks for this precise
   execution path:
   ```bash
   python -m venv venv
    ```

3. **Activate the environment and install the pinned dependencies:**
   ```bash
   # Mac/Linux:
   source venv/bin/activate
   # Windows:
   venv\Scripts\activate
   pip install -r requirements.txt
   ```

**Phase 2: Execution Workflow**

The application requires two concurrent operations. You have to run the Streamlit frontend and execute the IBM Bob orchestration loop at the same time.

1. **Boot the Presentation Workspace**
   Run the Streamlit application from your active terminal. Upon execution, `src/state_manager.py`
   automatically runs `init_db()` to generate a clean `naur_state.db` file in your root folder.
   ```bash
   streamlit run app.py
   ```
   *The UI will open in your browser, typically at `http://localhost:8501`.*

2. **Connect the Orchestration Engine**
   Open the `naur` project folder inside your IBM Bob-enabled IDE. Because the `.bob/mcp.json` file
   is present, Bob automatically registers the local MCP server, granting it secure access to the
   SQLite database via standard input/output (stdio).

3. **Run the Live Alignment Loop**
To see the autonomous linter in action, follow this exact loop:

   3.1. **Human Step:** In the Streamlit UI, select a Role from the dropdown (e.g., *Frontend
      Engineer*), provide context (e.g. Tech Stack), adjust the Governance phase slider,
<br>
<img width="477" height="876" alt="Sidebar Context and Role Selection" src="https://github.com/user-attachments/assets/449523a1-6d82-4e08-b440-ac1c978fc17b" />
<br>
<br>
type a technical proposal into the chat box, and submit the message.
<br>
<img width="1387" height="306" alt="Chat Workspace Interface" src="https://github.com/user-attachments/assets/cdea994e-d92d-4149-95b6-ac2de5c69796" />
<br>
<br>

  3.2. **AI Step:** Switch to your IDE and open the IBM Bob chat interface. To initialize the
  linter's exact reasoning constraints, submit this initial execution prompt with the **MCP and read permissions**:
<br><br><br>
<img width="507" height="1001" alt="IDE MCP Setup Verification" src="https://github.com/user-attachments/assets/4f295490-bf88-47ca-8694-5be5ea11ebfa" /> <img width="326" height="542" alt="Bob Orchestration Panel" src="https://github.com/user-attachments/assets/1fe8c222-5a96-4b46-a191-ad201299b4ce" />




<br>
<br>

```
 "Bob, act as the Ontological Linter and Principal Architect for Project Naur. Execute the following observation loop exactly 2 times, pausing for 10 seconds between each iteration. After the 2nd iteration, halt completely and explicitly say 'Loop Complete.'

Action Chain:
1. Invoke read_architecture_thread.
2. Analyze new messages for risks across ALL five domains (FE, BE, DS, UI, PROD).
3. If technical friction exists, invoke update_domain_constraint (Separate tool call for each domain using the arguments: text, business_impact, deep_dive, risk_level).
4. You MUST execute a separate tool call to update_domain_constraint with the domain set to 'GLOBAL' for the rationale.
5. If vague buzzwords exist, invoke upsert_project_dictionary." 
```

  3.3 **Sync Step** Wait for Bob to finish calling the parallel MCP tools and declare "Loop Complete." Return to the Streamlit UI and click the **SYNC** button in the sidebar.


  3.4. **Continue Thread?** If you are continuing an existing thread and simply want Bob to re-evaluate new messages without burning unnecessary Bobcoins on the full prompt:
> *"Execute your observation loop exactly 2 times, then halt."*

3.5. **Review:** The UI instantly ingests the database mutations, rendering the updated **Alignment Risk Score**, populating the **Domain Constraint Cards**, and injecting any newly captured terminology into the **Project Dictionary**.
<br>
<br>
<img width="337" height="182" alt="Dashboard State Mutations Re-cached" src="https://github.com/user-attachments/assets/172f2cdb-e008-4097-b199-91f7eb200661" />
<br>
<br>

>NOTE: I intentionally limited Bob's execution prompt to exactly two iterations. This gives the agent just enough cycles to double-check its own reasoning and outputs, while strictly budgeting our Bobcoin expenditure.
>
>
**State Reset**
If the SQLite ledger accumulates too much chat history or test data, simply click the **CLEAR** button in the sidebar. This triggers `sm.clear_ledger()`, performing a clean transaction wipe across all three database tables instantly.

<br><br>


---

## 5. Track Alignment: The Future of Work

The Wildcard track strictly demands intelligent systems that evolve AI from a simple utility into a true workspace collaborator. Naur achieves this not by generating code faster, but by optimizing the collective intelligence of the human team before execution begins.

Traditional workflows waste immense capital on manual alignment checking. Naur eliminates this cognitive overhead. While the execution loop is currently triggered on-demand to maintain developer control, the data processing is completely automated. The local agent parses the raw communication stream, extracts domain requirements, and populates a localized database ledger without a human having to manually map architectural dependencies.

Projects rarely stall because engineers cannot code fast enough; they stall because specialized disciplines operate in disconnected silos. By providing proactive workflow orchestration upstream—like flagging missing disciplinary perspectives via the "Missing Chair" validation—Naur forces cross-domain synchronization. When high-stakes proposals surface, human teams are susceptible to cognitive bias. Naur provides objective decision support by synthesizing technical requirements and business impacts into a clear, data-driven dashboard, giving teams the exact visibility they need to make rapid, risk-aware choices.

>NOTE: Per the official rules of "AI Builders Challenge with IBM Bob", Naur's architecture directly serves the high-velocity requirements of professional ***racing*** environments by eliminating communication latency and ensuring multi-disciplinary teams maintain peak operational speed without internal friction.
>
>>
<br>
<br>

---

## 6. Realities of the Proof of Concept & What's Next

### Why There’s No Live URL

Let’s be real: you cannot click a live website link to test Naur in your browser, and that is entirely by design. I built this to stress-test IBM Bob's native workspace capabilities. It is a local MCP server communicating via standard input/output channels directly inside the IDE. A generic, hosted web sandbox simply cannot replicate a local SQLite transaction environment. The AI engine handles the complex reasoning automatically, but I am keeping a human hand on the ignition switch for this proof of concept.
<br>

### The Prompt Trade-Off:
Building an AI agent that evaluates other architecture creates a unique context-window challenge. During development, I put IBM Bob through dozens of prompt iterations to perfectly sterilize its output. I discovered that aggressively locking down the model with strict negative constraints successfully stopped the agent from narrating its own loops, but it completely suffocated the model's technical reasoning.

>The reality of this PoC is a deliberate engineering compromise: **I chose to optimize for high-quality, actionable architectural insights over perfectly sterile metadata.** I rolled the prompt back to a loosely constrained version. Bob might occasionally leak an internal execution phrase into the UI, but in exchange, it delivers **senior-level, highly specific technical deep-dives.**

<br>
Because I am executing this as a solo developer, I had to make practical design trade-offs. I proved the underlying engine works flawlessly—now here is how I plan to scale it:

### Where I Am Taking Naur Next:
* **Zero-Prompt Ambient Mode (Solving the Manual Trigger)**  —  Manually copying prompts into the IDE chat is a temporary workaround. My immediate next milestone is turning Naur into a continuous background daemon process. The AI engine will passively track the communication ledger and autonomously intervene *only* when an alignment risk score crosses a critical threshold. No prompting required.
* **Blocking Bad Merges at the Gate (CI/CD Integration)** —  I want to move Naur out of the local IDE and straight into code review pipelines as a native GitHub Action. If a developer attempts to merge a pull request containing structural code changes that conflict with the domain constraints established during the planning phase, Naur will automatically flag it and freeze the merge until the team resolves the communication gap.
* **Bi-Directional Task Syncing** —  Teams talk in chat apps but live in task managers. I plan to connect the local SQLite ledger directly to platforms like Jira or Linear. Naur will ingest verified chat consensus and automatically translate messy developer debates into clean, actionable project tickets without human intervention.
* **Multi-Agent Pressure Testing** —  For high-risk architectural proposals, Naur will spin up specialized, competing AI personas in the background (think a hyper-conservative Security Engineer vs. a high-velocity Frontend Developer). They will actively debate the proposal from their respective lenses and present a unified, stress-tested recommendation to the human team.

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

