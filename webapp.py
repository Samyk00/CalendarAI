import streamlit as st
import json
from datetime import datetime, time, timedelta
import time as time_lib # To avoid conflict with datetime.time

# Local Imports
from agent import compose_event_details
from google_calendar import get_calendar_service, create_event

# --- PAGE CONFIGURATION & STYLING ---
st.set_page_config(page_title="TechCarrel AI Scheduler", page_icon="✨", layout="wide")

def load_css(file_name):
    """A function to load and apply a local CSS file."""
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        st.error(f"Critical Error: The stylesheet '{file_name}' was not found. Please ensure it's in the same directory.")

load_css("style.css")

# --- SVG ICONS (for headers only) ---
class Icons:
    details = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-file-text"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="16" y1="13" x2="8" y2="13"></line><line x1="16" y1="17" x2="8" y2="17"></line><polyline points="10 9 9 9 8 9"></polyline></svg>"""
    team = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-users"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path><circle cx="9" cy="7" r="4"></circle><path d="M23 21v-2a4 4 0 0 0-3-3.87"></path><path d="M16 3.13a4 4 0 0 1 0 7.75"></path></svg>"""
    preview = """<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="feather feather-eye"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"></path><circle cx="12" cy="12" r="3"></circle></svg>"""

# --- DATA LOADING ---
@st.cache_data
def load_jds():
    try:
        with open("job_descriptions.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except: return {}
job_data = load_jds()
job_titles = list(job_data.keys())

# --- SESSION STATE ---
if 'generated_details' not in st.session_state:
    st.session_state.generated_details = None
if 'editable_body' not in st.session_state:
    st.session_state.editable_body = ""
if 'editable_title' not in st.session_state:
    st.session_state.editable_title = ""

# --- HEADER ---
st.markdown("""
    <div class="header">
        <h1>✨ AI Interview Scheduler</h1>
        <p>The premium experience for crafting and sending perfect interview invitations.</p>
    </div>
""", unsafe_allow_html=True)

# --- MAIN APP LAYOUT (Two columns, no sidebar) ---
col1, col2 = st.columns([1, 1.2], gap="large")

# --- COLUMN 1: Input Form ---
with col1:
    with st.container(border=True):
        st.markdown(f"<h3><span class='icon'>{Icons.details}</span>1. Interview Details</h3>", unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            interview_type = st.selectbox("Interview Type", ["Interview", "Final Interview"])
        with c2:
            selected_job_title = st.selectbox("Job Position", options=job_titles)
        
        candidate_name = st.text_input("Candidate's Full Name", placeholder="e.g., Anjali Sharma")
        candidate_email = st.text_input("Candidate's Email Address", placeholder="e.g., anjali.s@example.com")
        
        c3, c4 = st.columns(2)
        with c3:
            interview_date = st.date_input("Interview Date")
        with c4:
            interview_time = st.time_input("Time (IST)", value=time(14, 0))

    with st.container(border=True):
        st.markdown(f"<h3><span class='icon'>{Icons.team}</span>2. Internal Attendees</h3>", unsafe_allow_html=True)
        
        default_attendee = "sameer.khan@techcarrel.com"
        optional_attendees_list = ["believe.in.gaurav@gmail.com", "rishi.joshva@gmail.com"]

        st.info(f"You (`{default_attendee}`) are automatically included.")
        optional_selection = []
        for attendee in optional_attendees_list:
            if st.checkbox(attendee, key=attendee):
                optional_selection.append(attendee)
    
    st.write("") # Spacer for the button
    # --- BUTTON ICONS FIXED ---
    if st.button("🚀 Generate & Preview Invitation", type="primary", use_container_width=True):
        if not all([candidate_name, candidate_email]) or selected_job_title == "Error":
            st.warning("Please complete all required fields.")
        else:
            with st.spinner("🤖 AI is composing the perfect invitation..."):
                try:
                    job_location = job_data[selected_job_title]['location']
                    job_description = job_data[selected_job_title]['description']
                    final_attendees = [default_attendee, candidate_email] + optional_selection
                    interview_datetime = datetime.combine(interview_date, interview_time)
                    
                    composed_data = compose_event_details(candidate_name, selected_job_title, job_location, interview_datetime, job_description, interview_type)
                    
                    st.session_state.generated_details = {
                        "attendees": final_attendees,
                        "start_time": interview_datetime,
                        "end_time": interview_datetime + timedelta(minutes=45)
                    }
                    st.session_state.editable_title = composed_data.get("title")
                    st.session_state.editable_body = composed_data.get("event_body")
                except Exception as e:
                    st.error("An error occurred with the AI Agent.")
                    st.exception(e)
                    st.session_state.generated_details = None

# --- COLUMN 2: Preview and Schedule ---
with col2:
    with st.container(border=True):
        st.markdown(f"<h3><span class='icon'>{Icons.preview}</span>3. Preview & Schedule</h3>", unsafe_allow_html=True)
        details = st.session_state.generated_details
        if details:
            st.session_state.editable_title = st.text_input("Title (Editable)", value=st.session_state.editable_title)
            st.session_state.editable_body = st.text_area("Invitation Body (Editable)", value=st.session_state.editable_body, height=275)
            st.success("A unique Google Meet link will be auto-generated.")

            # --- BUTTON ICONS FIXED ---
            if st.button("✅ Confirm & Schedule Interview", use_container_width=True):
                with st.spinner("Scheduler is contacting Google Calendar..."):
                    try:
                        calendar_service = get_calendar_service()
                        if calendar_service:
                            create_event(
                                service=calendar_service,
                                summary=st.session_state.editable_title,
                                description=st.session_state.editable_body,
                                attendees=details['attendees'],
                                start_time=details['start_time'],
                                end_time=details['end_time']
                            )
                            st.success("🎉 Invitation sent! The event is now on your calendar.")
                            st.balloons()
                            time_lib.sleep(2)
                            st.session_state.generated_details = None # Reset state
                            st.rerun()
                        else:
                            st.error("Could not connect to Google Calendar.")
                    except Exception as e:
                        st.error("Failed to schedule the event.")
                        st.exception(e)
        else:
            st.info("Fill out the form on the left to generate a preview here.")
