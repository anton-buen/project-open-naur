import re
import html
import base64
import streamlit as st
import src.state_manager as sm
from src.api_engine import run_architectural_audit
from datetime import datetime

st.set_page_config(page_title="Open Naur", layout="wide", initial_sidebar_state="expanded")

def parse_markdown(text: str) -> str:
    if not text or str(text).strip().lower() == "none": return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<code style="background: rgba(128,128,128,0.2); padding: 2px 4px; border-radius: 4px; font-family: monospace; font-size: 0.85em;">\1</code>', text)
    lines = text.split('\n')
    return "<br>".join([line for line in lines if line])

def apply_adaptive_theme() -> None:
    st.markdown("""
    <style>
        @font-face { font-family: 'SuisseIntl'; src: url('SuisseIntl-Book.woff2') format('woff2'); font-weight: normal; font-style: normal; }
        :root {
            --naur-accent-prod: #5D5D81; --naur-accent-fe: #6B4A3A; --naur-accent-be: #2F3E3E;
            --naur-accent-ds: #A3A08E; --naur-accent-ui: #9E768F; --naur-accent-risk: #C48A4A;
        }
        html, body, .stApp { font-family: 'SuisseIntl', 'Helvetica Neue', Helvetica, Arial, sans-serif !important; }
        .brand-title { font-family: 'Charter', 'Palatino Linotype', serif !important; font-size: 2.6rem !important; font-weight: 700 !important; color: var(--naur-accent-risk); margin-bottom: 0 !important;}
        .subtext { opacity: 0.6; font-size: 0.9rem; margin-top: -5px; margin-bottom: 15px; }
        .header-container { display: flex; align-items: center; gap: 12px; margin-bottom: 1rem; flex-wrap: wrap; }
        .risk-badge { padding: 0.5rem 1rem; font-weight: 700; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.08em; border-radius: 4px; box-shadow: 0 2px 4px rgba(0,0,0,0.2); }
        .risk-high { background-color: #B33A3A; color: #FFFFFF; border-left: 4px solid #FF8A8A; }
        .risk-medium { background-color: #C48A4A; color: #111111; border-left: 4px solid #FFE0B2; }
        .risk-low { background-color: #4E6B4E; color: #FFFFFF; border-left: 4px solid #A5D6A7; }
        
        .mini-blast { padding: 0.2rem 0.5rem; font-weight: 700; font-size: 0.65rem; text-transform: uppercase; letter-spacing: 0.05em; border-radius: 4px; box-shadow: 0 1px 2px rgba(0,0,0,0.15); }
        .mini-HIGH { background-color: #B33A3A; color: #FFFFFF; }
        .mini-MEDIUM { background-color: #C48A4A; color: #111111; }
        .mini-LOW { background-color: #4E6B4E; color: #FFFFFF; }

        .tech-card { padding: 1.5rem; border-radius: 6px; border: 1px solid rgba(128, 128, 128, 0.2); background-color: rgba(128, 128, 128, 0.05); font-size: 0.9rem; line-height: 1.6; height: 100%; display: flex; flex-direction: column; }
        .card-prod { border-top: 4px solid var(--naur-accent-prod) !important; }
        .card-fe { border-top: 4px solid var(--naur-accent-fe) !important; }
        .card-be { border-top: 4px solid var(--naur-accent-be) !important; }
        .card-ds { border-top: 4px solid var(--naur-accent-ds) !important; }
        .card-ui { border-top: 4px solid var(--naur-accent-ui) !important; }
        
        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem; border-bottom: 1px solid rgba(128,128,128,0.1); padding-bottom: 0.5rem; }
        .card-title { font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; font-size: 0.75rem; opacity: 0.8; margin: 0; }

        .jargon-toggle { display: none; }
        .jargon-label { font-size: 0.65rem; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em; cursor: pointer; padding: 4px 8px; border-radius: 4px; background: rgba(128, 128, 128, 0.1); border: 1px solid rgba(128, 128, 128, 0.3); transition: 0.2s; user-select: none; }
        .jargon-toggle:checked ~ .card-header .jargon-label { background: var(--naur-accent-risk); color: #111; border-color: transparent; }
        
        .biz-text { display: none; font-size: 0.95rem; padding-top: 0.5rem; flex-grow: 1; }
        .tech-text { display: block; font-size: 0.9rem; padding-top: 0.5rem; flex-grow: 1; }
        .jargon-toggle:checked ~ .tech-text { display: none; }
        .jargon-toggle:checked ~ .biz-text { display: block; }

        details.deep-dive { margin-top: 1.5rem; border-radius: 4px; border: 1px solid rgba(128, 128, 128, 0.2); overflow: hidden; background: rgba(0,0,0,0.1); }
        details.deep-dive summary { padding: 0.75rem; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; cursor: pointer; outline: none; transition: background 0.2s; list-style: none; text-align: center; opacity: 0.8;}
        details.deep-dive summary::-webkit-details-marker { display: none; }
        details.deep-dive summary:hover { background: rgba(128, 128, 128, 0.1); opacity: 1; }
        details.deep-dive .deep-content { padding: 1rem; font-size: 0.85rem; line-height: 1.6; border-top: 1px solid rgba(128, 128, 128, 0.2); opacity: 0.9; }
        
        .glossary-section { border: 1px solid rgba(128, 128, 128, 0.2); border-top: 4px solid var(--naur-accent-risk); background-color: rgba(128, 128, 128, 0.05); border-radius: 6px; padding: 1.5rem; font-size: 0.9rem; }
        .glossary-term { font-weight: 700; font-size: 0.9rem; margin-top: 1rem; display: block; color: var(--naur-accent-risk); text-transform: uppercase; letter-spacing: 0.05em;}
        .glossary-definition { opacity: 0.8; margin-top: 0.25rem; margin-bottom: 1rem; display: block; }
        .missing-chair-alert { background-color: rgba(179, 58, 58, 0.15); border-left: 4px solid #B33A3A; padding: 1rem; margin-bottom: 1rem; border-radius: 4px; font-weight: 600; color: #ff9999; }

        /* Invisible Title Input Styles */
        div[data-testid="stTextInput"] div[data-baseweb="input"] { background-color: transparent !important; border: none !important; box-shadow: none !important; }
        div[data-testid="stTextInput"] input { font-size: 1.75rem !important; font-weight: 700 !important; padding: 0 !important; color: inherit !important; }
        
        /* Custom Chat Bubble Styles */
        .chat-row { display: flex; gap: 1rem; margin-bottom: 1.5rem; }
        .chat-avatar { flex-shrink: 0; width: 40px; height: 40px; border-radius: 50%; }
        .chat-content { flex-grow: 1; background-color: rgba(128, 128, 128, 0.05); padding: 1rem 1.25rem; border-radius: 2px 12px 12px 12px; border: 1px solid rgba(128, 128, 128, 0.15); }
        .chat-header { display: flex; justify-content: space-between; margin-bottom: 0.5rem; align-items: center;}
        .chat-role { font-weight: 700; font-size: 0.8rem; color: var(--naur-accent-risk); text-transform: uppercase; letter-spacing: 0.05em;}
        .chat-time { opacity: 0.4; font-size: 0.7rem; font-family: monospace;}
        .chat-text { font-size: 0.95rem; line-height: 1.5; opacity: 0.9; }

        /* Audit Line Separator */
        .audit-line { display: flex; align-items: center; text-align: center; color: var(--naur-accent-risk); font-size: 0.7rem; font-weight: 700; text-transform: uppercase; letter-spacing: 0.1em; margin: 2.5rem 0; opacity: 0.7; }
        .audit-line::before, .audit-line::after { content: ''; flex: 1; border-bottom: 1px dashed var(--naur-accent-risk); opacity: 0.5;}
        .audit-line:not(:empty)::before { margin-right: 1em; }
        .audit-line:not(:empty)::after { margin-left: 1em; }
    </style>
    """, unsafe_allow_html=True)

def make_avatar_uri(initials: str, bg: str, fg: str) -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="{bg}"/><text x="20" y="26" text-anchor="middle" font-size="13" font-weight="bold" font-family="sans-serif" fill="{fg}">{initials}</text></svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

def generate_srs_markdown(title: str, global_sum: dict, domains: dict, glossary: list) -> str:
    md = f"# {title}\n\n"
    if global_sum:
        md += f"## 1. Global Architecture Summary\n**Risk Level:** {global_sum['risk']}\n\n**Velocity Impact:**\n{global_sum['biz']}\n\n**Architectural Blocker:**\n{global_sum['tech']}\n\n"
    md += "## 2. Domain Constraints\n\n"
    for dom, data in domains.items():
        md += f"### {dom} (Risk: {data['risk']})\n- **Business Impact:** {data['biz']}\n- **Engineering Deep Dive:** {data['tech']}\n\n"
    md += "## 3. Project Glossary\n\n"
    for term, dfn in glossary:
        md += f"- **{term}**: {dfn}\n"
    return md

_ROLE_AVATAR_MAP = {
    "Product Manager":   ("PM", "#2A2A2A", "#E9DDCF"),
    "Frontend Engineer": ("FE", "#2A2A2A", "#E9DDCF"),
    "Backend Engineer":  ("BE", "#2A2A2A", "#E9DDCF"),
    "Data Scientist":    ("DS", "#2A2A2A", "#E9DDCF"),
    "UI/UX Designer":    ("UI", "#2A2A2A", "#E9DDCF"),
}

sm.init_db()
apply_adaptive_theme()

if "session_id" not in st.session_state:
    st.session_state.session_id = sm.create_session()
session_id = st.session_state.session_id

with st.sidebar:
    st.markdown("<h1 class='brand-title'>Open Naur</h1>", unsafe_allow_html=True)
    st.markdown('<p class="subtext">Align your team, skip the friction.</p>', unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; margin-top: 1rem;'>Role</h3>", unsafe_allow_html=True)
    role = st.selectbox("Role", options=["Product Manager", "Frontend Engineer", "Backend Engineer", "Data Scientist", "UI/UX Designer"], label_visibility="collapsed", key="active_role")
    
    st.markdown("<h3 style='font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; margin-top: 1rem;'>Context</h3>", unsafe_allow_html=True)
    global_context = st.text_area("Context", key="global_context", placeholder="e.g. Serverless AWS. HIPAA Compliance.", height=120, label_visibility="collapsed")
    
    st.markdown("<h3 style='font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; margin-top: 1rem;'>Governance</h3>", unsafe_allow_html=True)
    gov_phase = st.select_slider("Governance", options=["Ideation", "Architecture", "Pre-Flight"], value="Architecture", label_visibility="collapsed")

    st.markdown("<hr style='margin: 1.5rem 0; opacity: 0.2;'>", unsafe_allow_html=True)
    st.markdown("<h3 style='font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7;'>Actions</h3>", unsafe_allow_html=True)
    
    if st.button("Run Audit", use_container_width=True, type="primary"):
        with st.spinner("Analyzing blast radius..."):
            ledger = sm.get_chat_ledger(session_id)
            if ledger == "No communication logged yet.":
                st.warning("Add communication first.")
            else:
                audit_result = run_architectural_audit(ledger)
                sm.save_audit(session_id, audit_result)
                st.session_state.missing_chairs = audit_result.missing_chairs
                sm.append_message(session_id, "SYSTEM", "AUDIT_RUN")
                st.rerun()

    if st.button("Clear", use_container_width=True):
        sm.clear_session_data(session_id)
        st.session_state.clear()
        st.rerun()

raw_constraints = sm.get_domain_constraints(session_id)
glossary = sm.get_project_dictionary(session_id) 
constraints_dict = {c[0]: {"biz": c[1], "tech": c[2], "risk": c[3]} for c in raw_constraints}
global_summary = constraints_dict.pop("GLOBAL", None)
active_domains = list(constraints_dict.keys())

current_title = st.session_state.get("project_title", "Untitled Architecture")
srs_export_data = generate_srs_markdown(current_title, global_summary, constraints_dict, glossary)

# HEADER: Precisely aligned Title, Date, and Export Button
current_date = datetime.now().strftime("%b %d, %Y")
col1, col2, col3 = st.columns([5, 1.2, 1.2])

with col1:
    st.text_input("Project Title", value="Untitled Architecture", key="project_title", label_visibility="collapsed")
with col2:
    st.markdown(f"<div style='text-align: right; padding-top: 10px;'><div style='font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; opacity: 0.5;'>Date</div><div style='font-size: 0.85rem; font-weight: 500; opacity: 0.8;'>{current_date}</div></div>", unsafe_allow_html=True)
with col3:
    st.markdown("<div style='padding-top: 15px;'></div>", unsafe_allow_html=True)
    st.download_button(label="Export Doc", data=srs_export_data, file_name=f"{current_title.replace(' ', '_')}_Architecture.md", mime="text/markdown", use_container_width=True)

st.markdown("<div style='border-bottom: 1px solid rgba(128,128,128,0.2); margin-bottom: 1.5rem; margin-top: -10px;'></div>", unsafe_allow_html=True)

if st.session_state.get("missing_chairs"):
    st.markdown(f"<div class='missing-chair-alert'>MISSING: {', '.join(st.session_state.missing_chairs)}</div>", unsafe_allow_html=True)

if raw_constraints:
    highest_risk = global_summary["risk"] if global_summary else "LOW"
    risk_class = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}.get(highest_risk, "risk-low")

    header_html = f"<div class='header-container'><div class='risk-badge {risk_class}'>Risk: {highest_risk}</div>"
    if active_domains:
        header_html += "<div style='display: flex; gap: 6px; align-items: center; border-left: 1px solid rgba(128,128,128,0.2); padding-left: 12px; margin-left: 4px;'>"
        for dom in active_domains:
            dom_risk = constraints_dict[dom]["risk"]
            header_html += f"<div class='mini-blast mini-{dom_risk}' title='{dom} Risk: {dom_risk}'>{dom}</div>"
        header_html += "</div>"
    header_html += "</div>"
    st.markdown(header_html, unsafe_allow_html=True)

    if global_summary:
        with st.expander("RATIONALE", expanded=False):
            biz_text = parse_markdown(html.escape(global_summary["biz"]))
            tech_text = parse_markdown(html.escape(global_summary["tech"]))
            
            st.markdown(f"""
            <div class='tech-card' style='border-top: 4px solid var(--naur-accent-risk);'>
                <input type='checkbox' id='toggle-global' class='jargon-toggle'>
                <div class='card-header'>
                    <div class='card-title'>Global Summary</div>
                    <label for='toggle-global' class='jargon-label'>Translate</label>
                </div>
                <div class='tech-text'>{tech_text}</div>
                <div class='biz-text'>{biz_text}</div>
            </div>
            """, unsafe_allow_html=True)

    if active_domains:
        with st.expander("DOMAINS", expanded=True):
            domain_config = {
                "PROD": {"name": "Product", "class": "card-prod"},
                "FE": {"name": "Frontend", "class": "card-fe"},
                "BE": {"name": "Backend", "class": "card-be"},
                "DS": {"name": "Data Science", "class": "card-ds"},
                "UI": {"name": "UI/UX", "class": "card-ui"},
                "DEVOPS": {"name": "DevOps", "class": "card-be"},
                "DATA": {"name": "Data Eng", "class": "card-ds"}
            }
            
            items = list(constraints_dict.items())
            for i in range(0, len(items), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(items):
                        domain, data = items[i + j]
                        conf = domain_config.get(domain, {"name": domain, "class": "card-be"})
                        
                        biz_text = parse_markdown(html.escape(data["biz"]))
                        tech_text = parse_markdown(html.escape(data["tech"]))
                        
                        deep_dive_html = f"<details class='deep-dive'><summary>Deep Dive</summary><div class='deep-content'>{tech_text}</div></details>" if tech_text else ""
                        
                        st.markdown(f"""
                        <style>
                        #toggle-{domain}:checked ~ .tech-text {{ display: none; }}
                        #toggle-{domain}:checked ~ .biz-text {{ display: block; }}
                        </style>
                        """, unsafe_allow_html=True)

                        cols[j].markdown(f"""
                        <div class='tech-card {conf['class']}'>
                            <input type='checkbox' id='toggle-{domain}' class='jargon-toggle'>
                            <div class='card-header'>
                                <div class='card-title'>{conf['name']}</div>
                                <label for='toggle-{domain}' class='jargon-label'>Translate</label>
                            </div>
                            <div class='tech-text'>{tech_text}</div>
                            <div class='biz-text'>{biz_text}</div>
                            {deep_dive_html}
                        </div>
                        """, unsafe_allow_html=True)

    if glossary:
        with st.expander("GLOSSARY", expanded=False):
            terms_html = ""
            for term, definition in glossary:
                clean_def = parse_markdown(html.escape(definition))
                terms_html += f"<div class='glossary-term'>{html.escape(term)}</div><div class='glossary-definition'>{clean_def}</div>"
            st.markdown(f"<div class='glossary-section'>{terms_html}</div>", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Ledger")

chat_messages = sm.get_chat_messages(session_id)
for row in chat_messages:
    # Safely unpack in case the database returns rows without a timestamp
    role_tag = row[0]
    msg = row[1]
    ts = row[2] if len(row) > 2 else ""

    if role_tag == "SYSTEM" and msg == "AUDIT_RUN":
        st.markdown("<div class='audit-line'><span>Audit Executed</span></div>", unsafe_allow_html=True)
        continue

    clean_content = re.sub(r'\n?\[Context: .*?\]', '', msg)
    clean_content = re.sub(r'\n?\[Governance: .*?\]', '', clean_content)
    
    try:
        parsed_ts = datetime.strptime(ts, "%Y-%m-%d %H:%M:%S").strftime("%I:%M %p")
    except:
        parsed_ts = str(ts)[11:16] if ts else ""

    initials, bg, fg = _ROLE_AVATAR_MAP.get(role_tag, ("U", "#2A2A2A", "#E9DDCF"))
    avatar_uri = make_avatar_uri(initials, bg, fg)
    
    st.markdown(f"""
    <div class='chat-row'>
        <img class='chat-avatar' src='{avatar_uri}'>
        <div class='chat-content'>
            <div class='chat-header'>
                <span class='chat-role'>{role_tag}</span>
                <span class='chat-time'>{parsed_ts}</span>
            </div>
            <div class='chat-text'>{parse_markdown(html.escape(clean_content.strip()))}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

if user_intent := st.chat_input("Join the discussion..."):
    active_role = st.session_state.get("active_role", "Product Manager")
    ctx_value = st.session_state.get("global_context", "").strip()
    
    stamped_intent = user_intent
    if ctx_value:
        stamped_intent += f"\n[Context: {ctx_value} | Governance: {gov_phase}]"
    else:
        stamped_intent += f"\n[Governance: {gov_phase}]"
        
    sm.append_message(session_id, active_role, stamped_intent)
    st.rerun()