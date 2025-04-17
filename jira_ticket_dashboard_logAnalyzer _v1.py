import streamlit as st
from jira import JIRA
import pandas as pd
import re
import requests
import os
import openai

# Set your OpenAI API key
# openai.api_key = "your-api-key"

# Sidebar - Jira credentials
st.sidebar.title("🔐 Jira Credentials")
jira_server = st.sidebar.text_input("Jira Server", "https://akshayb.atlassian.net")
email = st.sidebar.text_input("Email", "akshay.vjti81@gmail.com")
api_token = st.sidebar.text_input("API Token", type="password")
project_key = st.sidebar.text_input("Project Key", "TelcoAI")
max_results = st.sidebar.slider("Max Tickets", 1, 100, 10)

# Main app
st.title("📋 Jira Tickets Analyzer")


def parse_log_link(description):
    # Simple pattern to detect file path or URL
    # match = re.search(r"(https?://[^\s]+|/[\w\-/]+\.log)", description)
    #return match.group(0) if match else None
    return "C:\\server.log"


def analyze_logs_with_gpt(log_text, prompt_instruction="Analyze the logs and identify errors, warnings, or performance issues."):
    """
    Analyzes a given log file text using OpenAI GPT.

    Parameters:
    - log_text (str): The content of the log file.
    - prompt_instruction (str): Instruction to guide the GPT analysis.

    Returns:
    - str: GPT's analysis/summary of the logs.
    """
    try:
        # Truncate log if it's too large
        max_log_length = 4000  # Adjust based on token limit
        truncated_log = log_text[:max_log_length]

        messages = [
            {"role": "system", "content": "You are a log analysis expert."},
            {"role": "user", "content": f"{prompt_instruction}\n\n{truncated_log}"}
        ]

        response = openai.ChatCompletion.create(
            model="gpt-4",  # or "gpt-3.5-turbo"
            messages=messages,
            temperature=0.3,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"❌ Error during GPT log analysis: {str(e)}"

if st.sidebar.button("Fetch Tickets"):
    try:
        jira = JIRA({"server": jira_server}, basic_auth=(email, api_token))

        jql = f"project={project_key} ORDER BY created DESC"
        issues = jira.search_issues(jql, maxResults=max_results)

        # display issues in a table
        st.write(f"**Displaying all tickets:**\n")

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


        # styling the table

        # Styling functions
        def highlight_severity(val):
            color = {
                'Critical': 'red',
                'High': 'orange',
                'Medium': 'lightblue',
                'Low': 'green'
            }.get(val, 'white')
            return f'background-color: {color}; color: black'

        def highlight_status(val):
            return 'background-color: lightgreen' if val == 'Closed' else ''

        styled_df = (
        df.style
        .applymap(highlight_severity, subset=['Severity'])
        .applymap(highlight_status, subset=['Status'])
        .format({'Error Count': "{:.0f}"})
        .set_table_styles(
            [{
                'selector': 'th',
                'props': [('font-weight', 'bold'), ('background-color', '#f0f0f0')]
            }]
        )
        )

        st.dataframe(df)
        #st.dataframe(styled_df, use_container_width=True)

        st.write(f"**Displaying CRITICAL tickets:**\n")
        critical_tickets = []
        for issue in issues:
            desc = issue.fields.description or ""            
            if "critical" in desc.lower():
                # st.write("description", desc)
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
            #st.dataframe(styled_df, use_container_width=True)

            for ticket in critical_tickets:
                with st.expander(f"🔎 {ticket['Key']} - {ticket['Summary']}"):
                    # st.write(f"**Description:**\n{ticket['Description']}")
                    log_path = ticket["Log Path"]
                    if log_path:
                        st.write(f"**Log File:** {log_path}")
                        if st.button(f"📥 Download Logs for {ticket['Key']}", key=ticket['Key']+"_download"):
                             st.write("Downloading logs...")                           
                    if st.button(f"🧠 Run Analysis on {ticket['Key']}", key=ticket['Key']+"_analyze"):
                        st.info("🔍 Analysis would be performed here. (Add GPT/LLM logic if needed.)")
                        if os.path.exists(file_name):
                            with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
                                log_content = f.read()
                                st.info("⏳ Analyzing logs with GPT...")
                                summary = analyze_logs_with_gpt(log_content)
                                st.success("✅ Analysis Complete")
                                st.markdown(f"### 🔍 GPT Summary for {ticket['Key']}")
                                st.write(summary)
                        else:
                            st.warning("Log file not downloaded or not found.")
    except Exception as e:
        st.error(f"❌ Error fetching Jira issues: {e}")

col1, col2, col3 = st.columns(3)

#with col1:
#    st.markdown("""<a href="#" style="background-color:#e74c3c;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block;">🔴 Analyze Application Logs</a>""", unsafe_allow_html=True)

#with col2:
#    st.markdown("""<a href="#" style="background-color:#f39c12;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block;">🟠 Analyze Thread Dump</a>""", unsafe_allow_html=True)

#with col3:
#    st.markdown("""<a href="#" style="background-color:#27ae60;color:white;padding:10px 20px;border-radius:8px;text-decoration:none;display:inline-block;">🟢 Analyze Heap Dumps</a>""", unsafe_allow_html=True)


with st.container():
    st.markdown("### 🚨 Actions")
    if st.button("🔴Analyze Application Logs"):    
        # Your action here
        st.success("🎉 Button was clicked! Performing action...")
        st.write("Downloading logs...")

        file_name = "C:\\server.log"
        st.info("🔍 Analysis would be performed here. (Add GPT/LLM logic if needed.)")
        if os.path.exists(file_name):
            with open(file_name, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()
                st.info("⏳ Analyzing logs with GPT...")
                summary = analyze_logs_with_gpt(log_content)
                st.success("✅ Analysis Complete")
                st.markdown(f"### 🔍 GPT Summary for ticket")
                st.write(summary)
        else:
            st.warning("Log file not downloaded or not found.")

        # Example action
        with st.spinner("Doing something..."):
            import time
            time.sleep(2)  # Simulate some processing
            st.write("✅ Action complete!")
    #else:
    #    st.info("Click the button to start an action.")

    if st.button("🟠Analyze Thread Dumps"):
        st.write("Analysis ongoing..")
        st.info("📥 Downloading thread dumps...")
        #st.info("⏳ Analyzing logs with GPT...")

        thread_dump_file = "C:\\thread.txt"

        if os.path.exists(thread_dump_file):
            with open(thread_dump_file, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()
                st.info("⏳ Analyzing logs with GPT...")
                summary = analyze_logs_with_gpt(log_content)
                st.success("✅ Analysis Complete")
                st.markdown(f"### 🔍 GPT Summary for ticket")
                st.write(summary)
        else:
            st.warning("Thread dump file not downloaded or not found.")

            # Example action
            with st.spinner("Doing something..."):
                import time
                time.sleep(2)  # Simulate some processing
                st.write("✅ Action complete!")

    if st.button("🟢Analyze Heap Dumps"):
        st.write("Analysis ongoing..")
        st.info("📥 Downloading Heap dumps...")
        #st.info("⏳ Analyzing logs with GPT...")

        heap_dump_file = "C:\\java_pid21072.hprof"

        if os.path.exists(heap_dump_file):
            with open(heap_dump_file, "r", encoding="utf-8", errors="ignore") as f:
                log_content = f.read()
                st.info("⏳ Analyzing Heap dumps with GPT...")
                summary = analyze_logs_with_gpt(log_content)
                st.success("✅ Analysis Complete")
                st.markdown(f"### 🔍 GPT Summary for ticket")
                st.write(summary)
        else:
            st.warning("Heap dump file not downloaded or not found.")

            # Example action
            with st.spinner("Doing something..."):
                import time
                time.sleep(2)  # Simulate some processing
                st.write("✅ Action complete!")

    if st.button("🟡Analyze GC Logs"):
        st.write("Analysis ongoing..")

    if st.button("🔵Analyze JFR Logs"):
        st.write("Analysis ongoing..")

# Display a button and check if it's clicked
# if st.button("Analyze logs..."):

# if st.button("Analyze thread dump"):
    
#else:
#    st.info("Click the button to start an action.")


#if st.button("Analyze Heap dump"):


#else:
#    st.info("Click the button to start an action.")
