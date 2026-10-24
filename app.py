import json
import streamlit as st
from dotenv import load_dotenv
from regimpact.analysis import analyze
from regimpact.documents import extract_document, parse_clauses
from regimpact.models import BusinessProfile
from regimpact.store import recent_reports, save_report

load_dotenv()
st.set_page_config(page_title="Regulatory Change Impact", page_icon="⚖️", layout="wide")
st.markdown("""
<style>
  .stApp { background: #f7f8fc; }
  [data-testid="stSidebar"] { background: #101b36; }
  [data-testid="stSidebar"] * { color: #f4f7ff; }
  [data-testid="stSidebar"] .stTextInput input,
  [data-testid="stSidebar"] .stTextArea textarea,
  [data-testid="stSidebar"] .stNumberInput input { background: #20305a; color: white; border-color: #40547e; }
  .brand-kicker { color: #64748b; font-size: .78rem; font-weight: 700; letter-spacing: .09em; text-transform: uppercase; margin-bottom: .25rem; }
  .hero { background: linear-gradient(115deg, #10204a, #244d83); color: white; padding: 2rem 2.25rem; border-radius: 18px; margin: .3rem 0 1.5rem; }
  .hero h1 { color: white; margin: 0 0 .35rem; font-size: 2.25rem; }
  .hero p { color: #d7e5ff; margin: 0; font-size: 1.05rem; }
  .workflow-step { background: white; border: 1px solid #e3e8f2; border-radius: 12px; padding: .9rem 1rem; min-height: 85px; }
  .workflow-step b { color: #183a70; display: block; margin-bottom: .2rem; }
  .evidence-note { border-left: 4px solid #3b82f6; background: #eff6ff; padding: .8rem 1rem; border-radius: 0 8px 8px 0; color: #1e3a5f; }
  div[data-testid="stMetric"] { background: white; border: 1px solid #e3e8f2; border-radius: 12px; padding: 1rem; }
  .stButton > button[kind="primary"] { border-radius: 9px; font-weight: 700; padding: .58rem 1.15rem; }
</style>
""", unsafe_allow_html=True)

st.markdown("<div class='brand-kicker'>Compliance review for Indian SMEs</div>", unsafe_allow_html=True)
st.markdown("""<div class="hero"><h1>What changed — and does it affect you?</h1><p>Compare regulatory updates, check the business impact, and prepare the next steps with source evidence.</p></div>""", unsafe_allow_html=True)

def upload(label: str, key: str):
    return st.file_uploader(label, type=["pdf", "txt"], key=key, help="PDF or UTF-8 text. The official text remains the source of truth.")

with st.sidebar:
    st.markdown("## ⚖️ Compliance Review")
    st.caption("Your business context is used only to assess the supplied update.")
    st.divider()
    st.header("Business profile")
    with st.form("profile"):
        name = st.text_input("Business name", "Acme Foods Pvt Ltd")
        industry = st.text_input("Industry / sector", "food processing")
        state = st.text_input("State / operating area", "Karnataka")
        employees = st.number_input("Employees", min_value=0, value=42)
        turnover = st.number_input("Annual turnover (₹ lakh)", min_value=0.0, value=180.0)
        activities = st.text_area("Key activities", "Packaged food manufacturing and retail sale")
        registrations = st.text_input("Registrations", "FSSAI, GST")
        st.form_submit_button("Update profile")
    profile = BusinessProfile(name=name, industry=industry, state=state, employee_count=employees, annual_turnover_lakh=turnover, activities=activities, registrations=registrations)

tab_analyze, tab_history = st.tabs(["Analyze update", "Report history"])
with tab_analyze:
    step1, step2, step3 = st.columns(3)
    with step1: st.markdown("<div class='workflow-step'><b>01 · Compare</b>Upload the earlier and updated versions.</div>", unsafe_allow_html=True)
    with step2: st.markdown("<div class='workflow-step'><b>02 · Assess</b>Match the change to your SME profile.</div>", unsafe_allow_html=True)
    with step3: st.markdown("<div class='workflow-step'><b>03 · Act</b>Review evidence, owners, and deadlines.</div>", unsafe_allow_html=True)
    st.markdown("#### Upload source documents")
    st.caption("Use official PDF or text copies. Rule, section, and clause headings make matching more precise.")
    left, right = st.columns(2)
    with left:
        st.markdown("**Earlier version**")
        old_file = upload("Earlier version", "old")
    with right:
        st.markdown("**Updated notification**")
        new_file = upload("Updated notification", "new")
    if not (old_file and new_file):
        st.info("Add both versions to unlock the impact analysis.", icon="ℹ️")
    run = st.button("Create impact report  →", type="primary", disabled=not (old_file and new_file))
    if run:
        try:
            with st.status("Reading and comparing the documents…", expanded=True) as status:
                _, old_pages = extract_document(old_file.name, old_file.getvalue())
                _, new_pages = extract_document(new_file.name, new_file.getvalue())
                old_clauses, new_clauses = parse_clauses(old_pages), parse_clauses(new_pages)
                st.write(f"Parsed {len(old_clauses)} earlier and {len(new_clauses)} updated clauses.")
                report = analyze(old_clauses, new_clauses, profile)
                report_id = save_report(profile, report)
                status.update(label=f"Analysis complete — report #{report_id}", state="complete")
            st.session_state.report = report.model_dump()
            st.session_state.profile_name = profile.name
        except Exception as exc:
            st.error(f"Could not process these documents: {exc}")
    report = st.session_state.get("report")
    if report:
        st.divider()
        st.markdown("### Decision summary")
        c1, c2 = st.columns([1, 3], vertical_alignment="center")
        c1.metric("Applicability", report["applicability"])
        c2.markdown(f"<div class='evidence-note'><b>Why we think this:</b><br>{report['rationale']}</div>", unsafe_allow_html=True)
        st.markdown("### What changed")
        if report["changes"]:
            st.dataframe([{ "Type": x["change_type"].title(), "Clause": x["clause_id"], "Page": x["page"], "Plain summary": x["summary"]} for x in report["changes"]], use_container_width=True, hide_index=True)
            for x in report["changes"]:
                with st.expander(f"Evidence — {x['clause_id']} (page {x['page']})"):
                    st.write(x["evidence"])
                    if x.get("old_text"): st.caption("Earlier: " + x["old_text"])
                    if x.get("new_text"): st.caption("Updated: " + x["new_text"])
        else: st.success("No clause-level changes were detected.")
        st.markdown("### What you need to do")
        if report["actions"]:
            st.dataframe([{ "Action": x["action"], "Deadline": x["deadline"], "Priority": x["priority"], "Suggested owner": x["owner"]} for x in report["actions"]], use_container_width=True, hide_index=True)
            with st.expander("Action evidence"):
                for x in report["actions"]: st.write("• " + x["evidence"])
        else: st.write("No action is recommended from the detected changes.")
        st.warning(report["caveat"])
        st.download_button("Download report JSON", data=json.dumps(report, indent=2), file_name="regulatory-impact-report.json", mime="application/json")

with tab_history:
    st.markdown("### Saved analyses")
    st.caption("The ten most recent reports stored on this device.")
    reports = recent_reports()
    if reports:
        st.dataframe([{ "Report": r["id"], "Created": r["created_at"], "Business": r["business_name"], "Applicability": r["report"]["applicability"], "Changes": len(r["report"]["changes"])} for r in reports], hide_index=True, use_container_width=True)
    else: st.caption("Run an analysis to create the first saved report.")
