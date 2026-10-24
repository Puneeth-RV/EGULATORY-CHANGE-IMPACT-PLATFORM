import json
from io import BytesIO
import streamlit as st
from dotenv import load_dotenv
from regimpact.analysis import analyze
from regimpact.documents import extract_document, parse_clauses
from regimpact.models import BusinessProfile
from regimpact.store import recent_reports, save_report
from regimpact.gemini import enrich_actions

load_dotenv()
st.set_page_config(page_title="Regulatory Change Impact", page_icon="⚖️", layout="wide")
st.title("Regulatory Change Impact")
st.caption("Evidence-backed answers to: what changed, does it affect me, and what must I do?")

def upload(label: str, key: str):
    return st.file_uploader(label, type=["pdf", "txt"], key=key, help="PDF or UTF-8 text. The official text remains the source of truth.")

with st.sidebar:
    st.header("Business profile")
    with st.form("profile"):
        name = st.text_input("Business name", "Acme Foods Pvt Ltd")
        industry = st.text_input("Industry / sector", "food processing")
        state = st.text_input("State / operating area", "Karnataka")
        employees = st.number_input("Employees", min_value=0, value=42)
        turnover = st.number_input("Annual turnover (₹ lakh)", min_value=0.0, value=180.0)
        activities = st.text_area("Key activities", "Packaged food manufacturing and retail sale")
        registrations = st.text_input("Registrations", "FSSAI, GST")
        save_profile = st.form_submit_button("Use this profile")
    profile = BusinessProfile(name=name, industry=industry, state=state, employee_count=employees, annual_turnover_lakh=turnover, activities=activities, registrations=registrations)

tab_analyze, tab_history = st.tabs(["Analyze update", "Report history"])
with tab_analyze:
    st.subheader("1. Supply the earlier and updated versions")
    left, right = st.columns(2)
    with left: old_file = upload("Earlier version", "old")
    with right: new_file = upload("Updated notification", "new")
    use_gemini = st.checkbox("Use Gemini to improve plain-language action wording (optional)", value=False, help="The deterministic evidence and change detection remain authoritative.")
    run = st.button("Analyze change impact", type="primary", disabled=not (old_file and new_file))
    if run:
        try:
            with st.status("Reading and comparing the documents…", expanded=True) as status:
                _, old_pages = extract_document(old_file.name, old_file.getvalue())
                _, new_pages = extract_document(new_file.name, new_file.getvalue())
                old_clauses, new_clauses = parse_clauses(old_pages), parse_clauses(new_pages)
                st.write(f"Parsed {len(old_clauses)} earlier and {len(new_clauses)} updated clauses.")
                report = analyze(old_clauses, new_clauses, profile)
                if use_gemini:
                    enhanced = enrich_actions(profile, report.changes)
                    if enhanced is None:
                        st.write("Gemini not used: add GEMINI_API_KEY to .env to enable it.")
                    else:
                        report.actions = enhanced
                        st.write("Gemini produced validated plain-language action wording.")
                report_id = save_report(profile, report)
                status.update(label=f"Analysis complete — report #{report_id}", state="complete")
            st.session_state.report = report.model_dump()
            st.session_state.profile_name = profile.name
        except Exception as exc:
            st.error(f"Could not process these documents: {exc}")
    report = st.session_state.get("report")
    if report:
        st.divider()
        st.subheader("2. Decision summary")
        c1, c2 = st.columns([1, 3])
        c1.metric("Applicability", report["applicability"])
        c2.info(report["rationale"])
        st.subheader("3. What changed")
        if report["changes"]:
            st.dataframe([{ "Type": x["change_type"].title(), "Clause": x["clause_id"], "Page": x["page"], "Plain summary": x["summary"]} for x in report["changes"]], use_container_width=True, hide_index=True)
            for x in report["changes"]:
                with st.expander(f"Evidence — {x['clause_id']} (page {x['page']})"):
                    st.write(x["evidence"])
                    if x.get("old_text"): st.caption("Earlier: " + x["old_text"])
                    if x.get("new_text"): st.caption("Updated: " + x["new_text"])
        else: st.success("No clause-level changes were detected.")
        st.subheader("4. What to do")
        if report["actions"]:
            st.dataframe([{ "Action": x["action"], "Deadline": x["deadline"], "Priority": x["priority"], "Suggested owner": x["owner"]} for x in report["actions"]], use_container_width=True, hide_index=True)
            with st.expander("Action evidence"):
                for x in report["actions"]: st.write("• " + x["evidence"])
        else: st.write("No action is recommended from the detected changes.")
        st.warning(report["caveat"])
        st.download_button("Download report JSON", data=json.dumps(report, indent=2), file_name="regulatory-impact-report.json", mime="application/json")

with tab_history:
    reports = recent_reports()
    if reports:
        st.dataframe([{ "Report": r["id"], "Created": r["created_at"], "Business": r["business_name"], "Applicability": r["report"]["applicability"], "Changes": len(r["report"]["changes"])} for r in reports], hide_index=True, use_container_width=True)
    else: st.caption("Run an analysis to create the first saved report.")
