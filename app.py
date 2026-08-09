import re
import html
import base64
import streamlit as st
import src.state_manager as sm
from src.api_engine import run_architectural_audit
from datetime import datetime

st.set_page_config(page_title="Open Naur", layout="wide", initial_sidebar_state="expanded")

# ---------------------------------------------------------
# 1. UI HELPERS & CSS THEME
# ---------------------------------------------------------

def parse_markdown(text: str) -> str:
    if not text or str(text).strip().lower() == "none": return ""
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'(?<!\*)\*(?!\*)(.*?)(?<!\*)\*(?!\*)', r'<i>\1</i>', text)
    text = re.sub(r'`([^`]+)`', r'<code style="background: rgba(128,128,128,0.2); padding: 2px 4px; border-radius: 4px; font-family: monospace; font-size: 0.85em;">\1</code>', text)
    # Basic paragraph splitting for simplicity in this merged view
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
        
        .chat-human { background-color: rgba(128, 128, 128, 0.1); padding: 1rem 1.25rem; border-radius: 12px 12px 12px 2px; font-size: 0.95rem; display: inline-block; border: 1px solid rgba(128, 128, 128, 0.2); }
        .glossary-section { border: 1px solid rgba(128, 128, 128, 0.2); border-top: 4px solid var(--naur-accent-risk); background-color: rgba(128, 128, 128, 0.05); border-radius: 6px; padding: 1.5rem; font-size: 0.9rem; }
        .glossary-term { font-weight: 600; font-size: 0.9rem; margin-top: 0.5rem; display: inline-block; background: rgba(128,128,128,0.1); padding: 2px 8px; border-radius: 4px; margin-right: 8px;}
    </style>
    """, unsafe_allow_html=True)

def make_avatar_uri(initials: str, bg: str, fg: str) -> str:
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="40" height="40"><circle cx="20" cy="20" r="20" fill="{bg}"/><text x="20" y="26" text-anchor="middle" font-size="13" font-weight="bold" font-family="sans-serif" fill="{fg}">{initials}</text></svg>'
    return "data:image/svg+xml;base64," + base64.b64encode(svg.encode()).decode()

_ROLE_AVATAR_MAP = {
    "Product Manager":   ("PM", "#2A2A2A", "#E9DDCF"),
    "Frontend Engineer": ("FE", "#2A2A2A", "#E9DDCF"),
    "Backend Engineer":  ("BE", "#2A2A2A", "#E9DDCF"),
    "Data Scientist":    ("DS", "#2A2A2A", "#E9DDCF"),
    "UI/UX Designer":    ("UI", "#2A2A2A", "#E9DDCF"),
}

# ---------------------------------------------------------
# 2. STATE & SESSION MANAGEMENT
# ---------------------------------------------------------
sm.init_db()
apply_adaptive_theme()

if "session_id" not in st.session_state:
    st.session_state.session_id = sm.create_session()
session_id = st.session_state.session_id

# ---------------------------------------------------------
# 3. SIDEBAR & TRIGGER CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.markdown("<h1 class='brand-title'>Open Naur</h1>", unsafe_allow_html=True)
    st.markdown('<p class="subtext">Align your team, skip the friction.</p>', unsafe_allow_html=True)

    st.markdown("<h3 style='font-size: 0.8rem; text-transform: uppercase; letter-spacing: 0.05em; opacity: 0.7; margin-top: 1rem;'>Role</h3>", unsafe_allow_html=True)
    role = st.selectbox("Role", options=["Product Manager", "Frontend Engineer", "Backend Engineer", "Data Scientist", "UI/UX Designer"], label_visibility="collapsed", key="active_role")

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
                st.rerun()

    if st.button("Clear Session", use_container_width=True):
        sm.clear_session_data(session_id)
        st.session_state.clear()
        st.rerun()

# ---------------------------------------------------------
# 4. DASHBOARD RENDERER
# ---------------------------------------------------------
current_date = datetime.now().strftime("%A, %b %d, %Y")
st.markdown(f"""
<div style="margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid rgba(128,128,128,0.2); display: flex; justify-content: space-between; align-items: flex-end;">
    <div><h2 style='margin-top: 0; margin-bottom: 0.25rem; font-size: 1.5rem;'>Workspace</h2>
    <p class="subtext" style="margin-bottom: 0;">Multi-tenant isolated session</p></div>
    <div style="text-align: right;"><div style="font-size: 0.7rem; text-transform: uppercase; letter-spacing: 0.05em; font-weight: 700; opacity: 0.5;">Session Date</div>
    <div style="font-size: 0.85rem; font-weight: 500; opacity: 0.8;">{current_date}</div></div>
</div>
""", unsafe_allow_html=True)

# Fetch API data from SQLite
raw_constraints = sm.get_domain_constraints(session_id)
glossary = sm.get_project_dictionary(session_id)

constraints_dict = {c[0]: {"biz": c[1], "tech": c[2], "risk": c[3]} for c in raw_constraints}
global_summary = constraints_dict.pop("GLOBAL", None)
active_domains = list(constraints_dict.keys())

# Render Missing Chairs Warning
if st.session_state.get("missing_chairs"):
    st.error(f"🚨 **MISSING CHAIR RULE TRIGGERED:** {', '.join(st.session_state.missing_chairs)} absent from decision.")

# Render Risk Header
if raw_constraints:
    highest_risk = global_summary["risk"] if global_summary else "LOW"
    risk_class = {"HIGH": "risk-high", "MEDIUM": "risk-medium", "LOW": "risk-low"}.get(highest_risk, "risk-low")

    header_html = f"<div class='header-container'><div class='risk-badge {risk_class}'>Alignment Risk: {highest_risk}</div>"
    if active_domains:
        header_html += "<div style='display: flex; gap: 6px; align-items: center; border-left: 1px solid rgba(128,128,128,0.2); padding-left: 12px; margin-left: 4px;'>"
        for dom in active_domains:
            dom_risk = constraints_dict[dom]["risk"]
            header_html += f"<div class='mini-blast mini-{dom_risk}' title='{dom} Risk: {dom_risk}'>{dom}</div>"
        header_html += "</div>"
    header_html += "</div>"
    st.markdown(header_html, unsafe_allow_html=True)

    # Global Summary
    if global_summary:
        with st.expander("RATIONALE", expanded=False):
            tech_text = parse_markdown(html.escape(global_summary["tech"]))
            biz_text  = parse_markdown(html.escape(global_summary["biz"]))
            st.markdown(f"""
            <div class='tech-card' style='border-top: 4px solid var(--naur-accent-risk);'>
                <input type='checkbox' id='toggle-global' class='jargon-toggle'>
                <div class='card-header'>
                    <div class='card-title'>Global Summary</div>
                    <label for='toggle-global' class='jargon-label'>Translate</label>
                </div>
                <div class='tech-text'><b>Architectural Blocker:</b><br>{tech_text}</div>
                <div class='biz-text'><b>Velocity Impact:</b><br>{biz_text}</div>
            </div>
            """, unsafe_allow_html=True)

    # Domain Cards
    if active_domains:
        with st.expander("DOMAIN CONSTRAINTS", expanded=True):
            domain_config = {
                "PROD": {"name": "Product", "class": "card-prod"},
                "FE": {"name": "Frontend", "class": "card-fe"},
                "BE": {"name": "Backend", "class": "card-be"},
                "DS": {"name": "Data Science", "class": "card-ds"},
                "UI": {"name": "UI/UX", "class": "card-ui"},
            }
            
            items = list(constraints_dict.items())
            for i in range(0, len(items), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(items):
                        domain, data = items[i + j]
                        conf = domain_config.get(domain, {"name": domain, "class": "card-be"})
                        tech_text = parse_markdown(html.escape(data["tech"]))
                        biz_text = parse_markdown(html.escape(data["biz"]))
                        
                        cols[j].markdown(f"""
                        <div class='tech-card {conf['class']}'>
                            <input type='checkbox' id='toggle-{domain}' class='jargon-toggle'>
                            <div class='card-header'>
                                <div class='card-title'>{conf['name']}</div>
                                <label for='toggle-{domain}' class='jargon-label'>Translate</label>
                            </div>
                            <div class='tech-text'><b>Engineering Req:</b><br>{tech_text}</div>
                            <div class='biz-text'><b>Business Impact:</b><br>{biz_text}</div>
                        </div>
                        """, unsafe_allow_html=True)

    # Glossary
    if glossary:
        with st.expander("PROJECT DICTIONARY (Caught Jargon)", expanded=False):
            terms_html = "".join([f"<div class='glossary-term'>{html.escape(t)}</div>" for t in glossary])
            st.markdown(f"<div class='glossary-section'>{terms_html}</div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. CHAT THREAD RENDERER
# ---------------------------------------------------------
st.markdown("<hr>", unsafe_allow_html=True)
st.subheader("Communication Ledger")

chat_messages = sm.get_chat_messages(session_id)
for role_tag, msg in chat_messages:
    initials, bg, fg = _ROLE_AVATAR_MAP.get(role_tag, ("U", "#2A2A2A", "#E9DDCF"))
    avatar_uri = make_avatar_uri(initials, bg, fg)
    with st.chat_message("human", avatar=avatar_uri):
        st.markdown(f"<div class='chat-human'><b>[{role_tag}]</b><br>{html.escape(msg)}</div>", unsafe_allow_html=True)

st.markdown("<div style='height: 100px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 6. INPUT
# ---------------------------------------------------------
if user_intent := st.chat_input("Join the discussion..."):
    active_role = st.session_state.get("active_role", "Product Manager")
    sm.append_message(session_id, active_role, user_intent)
    st.rerun()