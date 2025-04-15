import streamlit as st
from jira import JIRA
import pandas as pd
import re
import requests
import os

# Sidebar - Jira credentials
st.sidebar.title("🔐 Jira Credentials")
jira_server = st.sidebar.text_input("Jira Server", "https://your-domain.atlassian.net")
email = st.sidebar.text_input("Email", "your-email@example.com")
api_token = st.sidebar.text_input("API Token", type="password")
project_key = st.sidebar.text_input("Project Key", "PROJ")
max_results = st.sidebar.slider("Max Tickets", 1, 100, 10)

# Main app
st.title("📋 Jira Ticket & Log Analyzer")

def parse_log_link(description):
    # Simple pattern to detect file path or URL
    match = re.search(r"(https?://[^\s]+|/[\w\-/]+\.log)", description)
    return match.group(0) if match else None

if st.sidebar.button("Fetch Tickets"):
    try:
        jira = JIRA({"server": jira_server}, basic_auth=(email, api_token))

        jql = f"project={project_key} ORDER BY created DESC"
        issues = jira.search_issues(jql, maxResults=max_results)

        critical_tickets = []
        for issue in issues:
            desc = issue.fields.description or ""            
            if "critical" in desc.lower():
                st.write("description", desc)
                log_link = parse_log_link(desc)
                critical_tickets.append({
                    "Key": issue.key,
                    "Summary": issue.fields.summary,
                    "Severity": "Critical",
                    "Assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                    "Created": issue.fields.created[:10],
                    "Description": desc,
                    "Log Path": log_link
                })

        if not critical_tickets:
            st.info("No critical tickets found.")
        else:
            df = pd.DataFrame(critical_tickets)
            st.dataframe(df)

            for ticket in critical_tickets:
                with st.expander(f"🔎 {ticket['Key']} - {ticket['Summary']}"):
                    st.write(f"**Description:**\n{ticket['Description']}")
                    log_path = ticket["Log Path"]
                    if log_path:
                        st.write(f"**Log File:** {log_path}")
                        if st.button(f"📥 Download Logs for {ticket['Key']}", key=ticket['Key']+"_download"):
                            try:
                                if log_path.startswith("http"):
                                    response = requests.get(log_path)
                                    file_name = log_path.split("/")[-1]
                                    with open(file_name, "wb") as f:
                                        f.write(response.content)
                                    st.success(f"Downloaded {file_name}")
                                else:
                                    st.warning("Non-URL log paths need manual fetching or secure server integration.")
                            except Exception as e:
                                st.error(f"Failed to download: {e}")

                    if st.button(f"🧠 Run Analysis on {ticket['Key']}", key=ticket['Key']+"_analyze"):
                        st.info("🔍 Analysis would be performed here. (Add GPT/LLM logic if needed.)")

    except Exception as e:
        st.error(f"❌ Error fetching Jira issues: {e}")
