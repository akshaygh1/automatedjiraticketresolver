import streamlit as st
import requests
import pandas as pd
from requests.auth import HTTPBasicAuth

# Sidebar inputs
st.sidebar.title("Jira Credentials & Filter")
jira_url = st.sidebar.text_input("Jira Base URL", "https://your-domain.atlassian.net")
email = st.sidebar.text_input("Email", "your-email@example.com")
api_token = st.sidebar.text_input("API Token", type="password")
project_key = st.sidebar.text_input("Project Key", "PROJ")
max_results = st.sidebar.slider("Max Tickets", 10, 100, 20)

# Main title
st.title("🚨 Jira Critical Severity Issues Dashboard")

if st.sidebar.button("Fetch Critical Tickets"):
    try:
        # JQL: project + severity = Critical
        jql = f'project = "{project_key}" AND labels = "Critical" ORDER BY created DESC'
        search_url = f"{jira_url}/rest/api/3/search"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        params = {
            "jql": jql,
            "maxResults": max_results,
            "fields": "summary,status,assignee,created,description,severity"
        }

        # Make request
        response = requests.get(
            search_url,
            headers=headers,
            params=params,
            auth=HTTPBasicAuth(email, api_token)
        )

        if response.status_code != 200:
            st.error(f"Failed to fetch issues: {response.status_code} - {response.text}")
            st.stop()

        issues = response.json().get("issues", [])

        # Build table data
        table_data = []
        st.subheader(f"Found {len(issues)} Critical Issues")

        for issue in issues:
            fields = issue["fields"]
            table_data.append({
                "Key": issue["key"],
                "Summary": fields.get("summary", ""),
                "Status": fields["status"]["name"] if fields.get("status") else "Unknown",
                "Assignee": fields["assignee"]["displayName"] if fields.get("assignee") else "Unassigned",
                "Created": fields.get("created", "")[:10],
            })

        df = pd.DataFrame(table_data)
        st.dataframe(df)

        # Show issue descriptions
        st.subheader("📝 Issue Descriptions (Critical)")
        for issue in issues:
            fields = issue["fields"]
            st.markdown(f"### 🔹 {issue['key']}: {fields.get('summary', '')}")
            st.write(fields.get("description", {}).get("content", [{}])[0].get("content", [{}])[0].get("text", "No Description"))

    except Exception as e:
        st.error(f"Error: {e}")
