import os
import json
from datetime import datetime
from openai import OpenAI

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"] 
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

def compose_event_details(candidate_name, job_title, job_location, interview_datetime, job_description, interview_type):
    """
    Takes structured data and uses an LLM to compose the title and event body
    based on the selected interview type.
    """

    interview_date_str = interview_datetime.strftime("%B %dth, %Y") # e.g., June 20th, 2025
    interview_time_str = interview_datetime.strftime("%I:%M %p IST") # e.g., 12:00 PM IST

    prompt = f"""
    You are an expert HR assistant who creates perfectly formatted calendar event details in JSON.
    Your task is to take the provided structured data and create a "title" and "event_body" according to the rules.

    **Provided Data:**
    - Candidate's Name: "{candidate_name}"
    - Job Title: "{job_title}"
    - Job Location: "{job_location}"
    - Interview Date: "{interview_date_str}"
    - Interview Time: "{interview_time_str}"
    - Full Job Description: "{job_description}"
    - Interview Type: "{interview_type}"

    **Formatting Rules:**

    1.  **Title Format:** The title MUST be: "Interview confirmed: {job_title} - {job_location} - TechCarrel"

    2.  **Event Body Format:** You MUST use the correct template based on the "Interview Type" provided.

        **IF `Interview Type` is "Interview":**
        Use this exact template, replacing bracketed variables.
        ---
        Hi {candidate_name},

        This is to confirm your interview scheduled for {interview_date_str} at {interview_time_str}.

        Following this discussion, we will evaluate your candidature and move forward with the next steps accordingly.

        Please be prepared and ensure you join the interview on time. Let me know if you have any questions.


        Job Description:

        {job_description}
        ---

        **IF `Interview Type` is "Final Interview":**
        Use this exact template, replacing bracketed variables.
        ---
        Hi {candidate_name},

        I’m pleased to confirm your final round interview scheduled for {interview_date_str} at {interview_time_str}.

        In this session, you will be meeting with the Director of the company, who will assess your in-depth expertise for this role. Based on this conversation, we will proceed with your candidature accordingly.

        Please be punctual and well-prepared for the discussion. Feel free to reach out if you need any assistance.


        Job Description:

        {job_description}
        ---
    
    **Output:**
    Your output MUST be ONLY the raw JSON object with two keys: "title" and "event_body". Use `\\n` for newlines in the `event_body`.
    """
    
    response = client.chat.completions.create(
        model="mistralai/mistral-nemo:free",
        messages=[
            {"role": "system", "content": "You are an HR assistant that generates perfectly formatted JSON for calendar events based on structured data and strict conditional rules."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.0,
        timeout=60.0,
    )
    composed_details_str = response.choices[0].message.content
    return json.loads(composed_details_str)