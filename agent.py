import streamlit as st
import os
import json
from datetime import datetime
from openai import OpenAI

# Securely loads the key from Streamlit secrets
OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def compose_event_details(candidate_name, job_title, job_location, interview_datetime, job_description, interview_type):
    interview_date_str = interview_datetime.strftime("%B %dth, %Y")
    interview_time_str = interview_datetime.strftime("%I:%M %p IST")
    prompt = f"""
    You are an expert HR assistant creating perfectly formatted calendar event details in JSON. Based on the data, create a "title" and "event_body".

    **Provided Data:**
    - Candidate's Name: "{candidate_name}"
    - Job Title: "{job_title}"
    - Job Location: "{job_location}"
    - Interview Date: "{interview_date_str}"
    - Interview Time: "{interview_time_str}"
    - Full Job Description: "{job_description}"
    - Interview Type: "{interview_type}"

    **Formatting Rules:**
    1.  Title Format: "Interview confirmed: {job_title} - {job_location} - TechCarrel"
    2.  Event Body Format: Use the correct template for the Interview Type.

        **IF `Interview Type` is "Interview":**
        ---
        Hi {candidate_name},

        This is to confirm your interview scheduled for {interview_date_str} at {interview_time_str}.
        A unique Google Meet link for joining the meeting will be automatically generated and included in this calendar invitation.

        Following this discussion, we will evaluate your candidature and move forward with the next steps accordingly.

        Please be prepared and ensure you join the interview on time. Let me know if you have any questions.


        Job Description:

        {job_description}
        ---

        **IF `Interview Type` is "Final Interview":**
        ---
        Hi {candidate_name},

        I’m pleased to confirm your final round interview scheduled for {interview_date_str} at {interview_time_str}.
        A unique Google Meet link for joining the meeting will be automatically generated and included in this calendar invitation.

        In this session, you will be meeting with the Director of the company, who will assess your in-depth expertise for this role. Based on this conversation, we will proceed with your candidature accordingly.

        Please be punctual and well-prepared for the discussion. Feel free to reach out if you need any assistance.


        Job Description:

        {job_description}
        ---
    
    Output ONLY the raw JSON object with "title" and "event_body" keys. Use `\\n` for newlines.
    """
    response = client.chat.completions.create(
        model="mistralai/mistral-nemo:free",
        messages=[{"role": "system", "content": "You are a helpful JSON formatting assistant."}, {"role": "user", "content": prompt}],
        temperature=0.0, timeout=60.0 )
    return json.loads(response.choices[0].message.content)
