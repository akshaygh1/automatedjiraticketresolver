import streamlit as st
from datetime import datetime, time, timedelta
import re
import openai

st.set_page_config(page_title="JBoss Log Analyzer", layout="wide")
st.title("📂 JBoss Log Filter & Analyzer")


# Load API key from environment variable or Streamlit secrets
# openai.api_key = st.secrets.get("xxxxxxxxx", None)

# Upload log file
uploaded_file = st.file_uploader("Upload JBoss log file", type=["log", "txt"])

# Ask for date and time with second + millisecond accuracy
col1, col2 = st.columns(2)

with col1:
    start_date = st.date_input("Start Date", datetime(2025, 3, 18).date())
    start_time_str = st.text_input("Start Time (HH:MM:SS,ms)", "12:50:00,000")

with col2:
    end_date = st.date_input("End Date", datetime(2025, 3, 18).date())
    end_time_str = st.text_input("End Time (HH:MM:SS,ms)", "12:52:29,999")

# Combine date and time string to datetime
def parse_datetime(date_part, time_str):
    full_str = f"{date_part} {time_str}"
    return datetime.strptime(full_str, "%Y-%m-%d %H:%M:%S,%f")

try:
    start_dt = parse_datetime(start_date, start_time_str)
    end_dt = parse_datetime(end_date, end_time_str)
except ValueError:
    st.error("Invalid time format. Please use HH:MM:SS,ms (e.g., 12:50:00,000)")
    st.stop()

# Log level filtering
selected_levels = st.multiselect(
    "Select Log Levels", ["ERROR", "WARN", "INFO", "DEBUG"], default=["ERROR", "WARN", "INFO"]
)

level_colors = {
    "ERROR": "red",
    "WARN": "orange",
    "INFO": "blue",
    "DEBUG": "green"
}

# Regex timestamp matcher: ^YYYY-MM-DD HH:MM:SS,mmm
timestamp_pattern = re.compile(r"^(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2},\d{3})")

# Highlight function
def highlight_levels(line):
    for level in selected_levels:
        if level in line:
            color = level_colors.get(level, "black")
            return f"<span style='color:{color}; font-family: monospace;'>{line}</span>"
    return f"<span style='color:gray; font-family: monospace;'>{line}</span>"

# Main logic
if uploaded_file:
    content = uploaded_file.read().decode("utf-8", errors="ignore")
    lines = content.splitlines()
    filtered_lines = []

    for line in lines:
        match = timestamp_pattern.match(line)
        if match:
            timestamp_str = match.group(1)
            try:
                log_time = datetime.strptime(timestamp_str, "%Y-%m-%d %H:%M:%S,%f")
                if start_dt <= log_time <= end_dt:
                    if any(level in line for level in selected_levels):
                        filtered_lines.append(line)
            except ValueError:
                continue  # Skip malformed timestamp lines

    st.success(f"✅ Found {len(filtered_lines)} matching log entries.")

    if filtered_lines:
        st.markdown("<br>".join([highlight_levels(line) for line in filtered_lines]), unsafe_allow_html=True)
        st.download_button("📥 Download Filtered Logs", "\n".join(filtered_lines), file_name="filtered_jboss_logs.log")

    # --- OpenAI Log Analysis ---
    openai_api_key = st.text_input("🔑 Enter OpenAI API Key", type="password")
    if openai_api_key:
        openai.api_key = openai_api_key

        if st.button("🧠 Analyze Logs with OpenAI"):
            sample_logs = "\n".join(filtered_lines[:100])  # Keep prompt manageable

            prompt = f"""
                You are a senior Java backend engineer analyzing JBoss server logs.
                Identify problems, errors, stack traces or performance issues in these logs.
                Suggest likely causes and potential resolutions.

                Logs:
                {sample_logs}
            """

            with st.spinner("Analyzing logs with GPT-4..."):
                try:
                    response = openai.ChatCompletion.create(
                        model="gpt-4",
                        messages=[
                            {"role": "system", "content": "You are an expert in Java backend and JBoss server logs."},
                            {"role": "user", "content": prompt}
                        ],
                        temperature=0.3
                    )
                    result = response.choices[0].message.content.strip()
                    st.subheader("🔍 GPT-4 Analysis")
                    st.markdown(result)
                except Exception as e:
                    st.error(f"❌ OpenAI API error: {e}")
    else:
        st.warning("🔐 Please enter your OpenAI API key to run log analysis.")    
