# jira_dashboard.py
import streamlit as st
from jira import JIRA
import pandas as pd

# Sidebar - Jira credentials and input
st.sidebar.title("🔐 Jira Credentials")
jira_server = st.sidebar.text_input("Jira Server URL", "https://your-domain.atlassian.net")
email = st.sidebar.text_input("Email", "your-email@example.com")
api_token = st.sidebar.text_input("API Token", type="password")
project_key = st.sidebar.text_input("Project Key", "PROJ")
max_results = st.sidebar.slider("Max Tickets", 1, 100, 10)

if st.sidebar.button("Fetch Tickets"):
    try:
        st.title("📋 Jira Tickets Dashboard")

        # Jira connection
        options = {"server": jira_server}
        jira = JIRA(options, basic_auth=(email, api_token))

        # Fetch issues
        jql = f"project={project_key} ORDER BY created DESC"
        issues = jira.search_issues(jql, maxResults=max_results)

        # Convert to DataFrame
        data = []
        for issue in issues:
            data.append({
                "Key": issue.key,
                "Summary": issue.fields.summary,
                "Status": issue.fields.status.name,
                "Assignee": issue.fields.assignee.displayName if issue.fields.assignee else "Unassigned",
                "Created": issue.fields.created[:10],
                "Updated": issue.fields.updated[:10],
            })

        df = pd.DataFrame(data)
        st.dataframe(df)

        # Optional: Show status count
        st.subheader("📊 Ticket Status Overview")
        st.bar_chart(df['Status'].value_counts())

    except Exception as e:
        st.error(f"Error fetching Jira issues: {e}")
