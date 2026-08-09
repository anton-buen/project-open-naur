import streamlit as st
import src.state_manager as sm
from src.api_engine import run_architectural_audit

# ---------------------------------------------------------
# 1. SESSION INITIALIZATION (Multi-Tenant Setup)
# ---------------------------------------------------------
st.set_page_config(page_title="Open Naur | Architectural Linter", layout="wide")

# Ensure the database schema exists
sm.init_db()

# Give every visitor their own isolated database session
if "session_id" not in st.session_state:
    st.session_state.session_id = sm.create_session()

session_id = st.session_state.session_id

# ---------------------------------------------------------
# 2. SIDEBAR: CHAT LEDGER & CONTROLS
# ---------------------------------------------------------
with st.sidebar:
    st.header("Project Communication")
    
    # Input for new architectural decisions
    role = st.selectbox("Role", ["Frontend Engineer", "Backend Engineer", "Product Manager", "Data Scientist", "UI/UX"])
    message = st.text_area("Technical Proposal / Update")
    
    if st.button("Submit Message"):
        if message:
            sm.append_message(session_id, role, message)
            st.success("Message committed to ledger.")
            
    st.divider()
    
    # The Execution Trigger
    if st.button("Run Architectural Audit", type="primary"):
        with st.spinner("Analyzing cross-domain blast radius..."):
            ledger = sm.get_chat_ledger(session_id)
            if ledger == "No communication logged yet.":
                st.warning("Add communication to the ledger first.")
            else:
                # Call Open Code API and save the Pydantic object
                audit_result = run_architectural_audit(ledger)
                sm.save_audit(session_id, audit_result)
                
                # We can store Missing Chairs in session state temporarily for display
                st.session_state.missing_chairs = audit_result.missing_chairs
                st.rerun()

    if st.button("Clear Session"):
        sm.clear_session_data(session_id)
        st.session_state.clear()
        st.rerun()

# ---------------------------------------------------------
# 3. MAIN DASHBOARD: THE LINTER OUTPUT
# ---------------------------------------------------------
st.title("Project Naur: Alignment Dashboard")

# Display the raw chat ledger
st.subheader("Raw Chat Ledger")
st.code(sm.get_chat_ledger(session_id), language="markdown")

st.divider()

# Fetch active constraints from the database
constraints = sm.get_domain_constraints(session_id)

if constraints:
    # Display Missing Chairs if caught during this run
    if "missing_chairs" in st.session_state and st.session_state.missing_chairs:
        st.error(f"🚨 **MISSING CHAIR RULE TRIGGERED:** The following disciplines are absent from this decision: {', '.join(st.session_state.missing_chairs)}")

    st.header("Architectural Constraints")
    
    # Separate Global Rationale from Domain Cards
    global_card = [c for c in constraints if c[0] == "GLOBAL"]
    domain_cards = [c for c in constraints if c[0] != "GLOBAL"]
    
    if global_card:
        st.info(f"**GLOBAL RISK LEVEL: {global_card[0][3]}**\n\n{global_card[0][1]}")

    # Render Domain Cards
    cols = st.columns(len(domain_cards)) if domain_cards else []
    for idx, card in enumerate(domain_cards):
        with cols[idx]:
            st.markdown(f"### {card[0]}")
            st.markdown(f"**Risk:** `{card[3]}`")
            st.markdown(f"Business Impact:")
            with st.expander("Deep Dive (Technical Blockers)"):
                st.code(card[2])
                
    st.divider()
    
    # Render Project Dictionary
    dictionary = sm.get_project_dictionary(session_id)
    if dictionary:
        st.subheader("Project Dictionary (Jargon Caught)")
        st.write(", ".join([f"`{term}`" for term in dictionary]))
else:
    st.write("No architectural constraints detected. Run an audit to analyze the ledger.")