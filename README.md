

# Open Naur
Different LLM integration: This version leverages a different large language model than the original.

No human-in-the-loop: The design removes the human moderation layer, making the system more streamlined and accessible.

Public accessibility: A public URL is provided to make the project easier to access and test.

Work in progress: Development is ongoing, and features may evolve as the project matures.

## 1. What's the big idea?

>**Project Title:** Naur (Inspired by **Peter Naur's** *Programming is Theory Building*)  
>**Challenge Theme:** Intelligent Systems for the Future of Work
<br> <br> 
### **The Problem: Alignment Tax.**

I am a CS student, and I built Naur because I’ve watched development teams fail in real-time. We rarely fail because someone lacks the technical talent to write a loop or configure a server; we fail because humans are remarkably bad at understanding each other.

In every project, you have specialists—frontend engineers, backend engineers, and product managers. They look at the software through completely different professional lenses. When a team sits down to plan, a simple choice often splinters into disjointed mental models. A word like "state" or "cache" means entirely different things depending on who you ask.

This creates what I call the **Alignment Tax**. Teams waste hours trying to explain their domains to one another, struggling to hold cross-domain constraints in their heads. This comprehension debt hits like a train during integration week, leading to painful late-stage rewrites. Current industry workflows rely heavily on autonomous AI agents to generate code faster, but accelerating execution without addressing underlying human alignment simply helps a team build the wrong software at record speeds. Naur intercepts this friction upstream.
<br> <br> 

### **The Solution: ***An Agent-Driven Architectural Auditor*****
Look, calling this an "Ontological Linter" might sound like a hackathon play to sound smart, but it isn't a static compiler analyzing the nature of cosmic existence. It is a highly specialized LLM orchestration strategy running over a local Model Context Protocol (MCP) server.

Instead of forcing an AI to blindly guess your code intent, Naur exposes your team's communication ledger directly to your local IDE agent workspace. It consolidates the time teams waste teaching each other into explicit, data-driven design constraints by running three structural checks on command.

First, it calculates the cross-domain blast radius of any technical proposal to see what breaks across other disciplines. Second, it enforces a "Missing Chair" rule—if Product and Frontend are making a decision in the chat but Backend is absent, Naur autonomously steps in to write strict constraints on behalf of that missing discipline. Finally, it catches terminology collisions, normalizing vague jargon into a centralized project dictionary to enforce ubiquitous language.
<br> <br> <br> 


## **Naur  — Dashboard and Features** 
<img width="1917" height="1017" alt="Naur Dashboard Overview" src="https://github.com/user-attachments/assets/b95ee00f-f1d2-458e-b272-cec2d04ed74a" />
 <br> <br>
Instead of dumping a wall of text into the chat, the AI synthesizes its background analysis into a real-time, interactive dashboard that serves as the team's single source of truth.


<br><br> 

**1. Alignment Risk & Blast Radius:**<br> 
<img width="582" height="120" alt="Alignment Risk Score" src="https://github.com/user-attachments/assets/0365819f-bbe1-44f2-b4c6-1c1628e97987" />
- Dynamic badges (PROD, FE, BE, DS, UI) light up at the top of the UI to map exact dependencies and calculate a global risk score (LOW, MEDIUM, HIGH).

<br><br> 

**2. The Global Rationale:**<br> 
<img width="1492" height="390" alt="Global Rationale Card" src="https://github.com/user-attachments/assets/a1522b94-96e8-4962-9dde-e66ff310d9ab" />
- Sitting immediately below the risk score, this master card provides the executive summary. It justifies the total risk score by synthesizing all the cross-domain friction into a single, unified view.

<br><br> 

**3. Domain Constraint Cards:**<br> 
<img width="1537" height="777" alt="Domain Constraint Cards Breakdown" src="https://github.com/user-attachments/assets/db1faeca-68a9-4a45-866e-2bca4a02e418" />
- The specific blast radius is then isolated into individual discipline cards (Product, Frontend, Backend, Data Science, UI/UX). Each card outlines the exact Engineering Requirements and Business Impacts justifying its respective badge.

<br><br> 

**4. Zero-Latency "Translate" & "Deep Dive" Toggles:**<br> 
<img width="1001" height="692" alt="Pure CSS Translation Toggle View" src="https://github.com/user-attachments/assets/e34c825f-95c9-4866-bee0-e01756d26c16" />
- Every single card—both the Global Rationale and the individual Domain Cards—is equipped with a pure-CSS "Translate" toggle to instantly flip technical jargon into layman's terms, and a "Deep Dive" expander to reveal the raw code-level strict blockers.

<br><br> 

**5. The Project Dictionary:**<br> 
<img width="1542" height="611" alt="Persistent Glossary State" src="https://github.com/user-attachments/assets/2c50de9e-9796-4a9a-9811-1bac5c2a88e6" />
- A persistent, centralized glossary pinned to the bottom of the dashboard that houses the normalized terms caught by the Ubiquitous Language check.

<br> <br> 
**The ultimate goal is to force shared understanding across domains, ensuring that whether a human or an AI agent ultimately writes the code, the underlying structural blueprint is “actually correct”. Any change or addition moving forward is also forced to be understood across said domains.**
<br>
<br>
<br>

---

## 2. What did IBM Bob do?

I wanted to genuinely push the boundaries of what an IDE agent could do. Instead of relying on the easy path of pre-built LangFlow templates or hosted web wrappers, I undertook a tedious, highly customized local configuration to leverage IBM Bob as the backbone for my local MCP server. I wanted to see if Bob could coordinate and reason across an entire local codebase without breaking existing structures.

I used Bob as a core engineering partner to build this system. Halfway through the build, I realized a flat JSON file wouldn't survive concurrent agent operations. I deployed Bob to completely rewire the Streamlit frontend to connect seamlessly to a new transactional SQLite API, decoupling the active chat history from the presentation logic without introducing a single regression. I also used Bob to bypass Streamlit's native layout limitations, providing exact hex codes to rewrite the CSS theme engine.

Most importantly, I prompted Bob to act as a ruthless systems auditor against my own codebase. Bob successfully caught data-contract aliasing gaps and transaction isolation vulnerabilities in my initial drafts, allowing me to systematically refactor the pipeline to achieve full end-to-end type safety and offline air-gap independence.

Today, Naur uses IBM Bob as its active processing brain. Under a strict prompt routine, Bob processes incoming communication logs, isolates domain boundaries, and dispatches parallel tool mutations back to the SQLite database.
<br> <br> 

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

