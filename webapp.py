import streamlit as st
import json
from datetime import datetime, time, timedelta

from agent import compose_event_details
from google_calendar import get_calendar_service, create_event

# --- Constants and Configuration ---
st.set_page_config(
    page_title="Interview Scheduler",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Load custom CSS and hide code elements
with open('style.css') as f:
    st.markdown(f'''
        <style>
            {f.read()}
            /* Hide code elements and improve text visibility */
            code {{
                display: none !important;
            }}
            div.stMarkdown {{
                color: var(--text-primary) !important;
            }}
            .element-container {{
                color: var(--text-primary) !important;
            }}
            * {{
                -webkit-font-smoothing: antialiased;
            }}
            /* Hide deploy button */
            .stDeployButton {{
                display: none !important;
            }}
            /* Hide hamburger menu */
            #MainMenu {{
                visibility: hidden;
            }}
            /* Hide Streamlit footer */
            footer {{
                visibility: hidden;
            }}
        </style>
    ''', unsafe_allow_html=True)

DEFAULT_ATTENDEE = "sameer.khan@techcarrel.com"
OPTIONAL_ATTENDEES = ["believe.in.gaurav@gmail.com", "rishi.joshva@gmail.com"]

# --- Data Loading Function ---
@st.cache_data
def load_jds():
    """Loads job descriptions from the JSON file."""
    try:
        with open("job_descriptions.json", "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                return {"Error": {"location": "N/A", "description": "job_descriptions.json is empty or contains invalid JSON. Please check the file content."}}
    except FileNotFoundError:
        return {"Error": {"location": "N/A", "description": "job_descriptions.json not found. Please create it."}}

job_data = load_jds()
job_titles = list(job_data.keys())

# Helper function to render icons without visible code
def render_icon(name, text=""):
    return st.markdown(f'<span class="icon-text"><i class="ri-{name}" style="display: none;"></i>{text}</span>', unsafe_allow_html=True)

# --- UI Layout ---
st.markdown('<div class="main-header animate-fade-in"><h1>✨ Interview Scheduler</h1><p>Create perfectly formatted interview invitations in seconds</p></div>', unsafe_allow_html=True)

if 'generated_details' not in st.session_state:
    st.session_state.generated_details = None
if 'editable_body' not in st.session_state:
    st.session_state.editable_body = ""

col1, col2 = st.columns([1, 1.2])

# --- COLUMN 1: Input Form ---
with col1:
    with st.container():
        st.markdown('<div class="bento-card animate-slide-in">', unsafe_allow_html=True)
        st.subheader("📋 Interview Details")
        
        interview_type = st.selectbox(
            "Type",
            ["Interview", "Final Interview"]
        )
        
        selected_job_title = st.selectbox(
            "Position",
            options=job_titles
        )
        
        col_name, col_email = st.columns(2)
        with col_name:
            candidate_name = st.text_input("Name", placeholder="e.g., Anjali Sharma")
        with col_email:
            candidate_email = st.text_input("Email", placeholder="e.g., anjali@example.com")
        
        col_date, col_time = st.columns(2)
        with col_date:
            interview_date = st.date_input("Date")
        with col_time:
            interview_time = st.time_input("Time (IST)", value=time(14, 0))
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="bento-card animate-slide-in">', unsafe_allow_html=True)
    st.subheader("👥 Internal Team")
    st.success(f"✓ {DEFAULT_ATTENDEE}")
    
    optional_selection = []
    for attendee in OPTIONAL_ATTENDEES:
        if st.checkbox(f"📧 {attendee}", key=attendee):
            optional_selection.append(attendee)
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("✨ Generate Preview", type="primary", use_container_width=True):
        if not all([candidate_name, candidate_email]) or selected_job_title == "Error":
            st.error("⚠️ Please fill all required fields")
        else:
            with st.spinner("🎨 Crafting your invitation..."):
                try:
                    job_location = job_data[selected_job_title]['location']
                    job_description = job_data[selected_job_title]['description']
                    final_attendees = [DEFAULT_ATTENDEE, candidate_email] + optional_selection
                    interview_datetime = datetime.combine(interview_date, interview_time)
                    
                    composed_data = compose_event_details(
                        candidate_name, selected_job_title, job_location,
                        interview_datetime, job_description, interview_type
                    )
                    
                    st.session_state.generated_details = {
                        "title": composed_data.get("title"),
                        "attendees": final_attendees,
                        "start_time": interview_datetime,
                        "end_time": interview_datetime + timedelta(minutes=45)
                    }
                    st.session_state.editable_body = composed_data.get("event_body")
                except Exception as e:
                    st.error("❌ Action Failed")
                    st.exception(e)
                    st.session_state.generated_details = None

# --- COLUMN 2: Preview and Schedule ---
with col2:
    details = st.session_state.generated_details
    
    if details:
        st.markdown('<div class="bento-card animate-fade-in">', unsafe_allow_html=True)
        st.subheader("👁️ Preview")
        st.markdown(f'<div class="preview-section">{details["title"]}</div>', unsafe_allow_html=True)
        
        st.markdown('<div style="margin-top: 1rem;">', unsafe_allow_html=True)
        st.text_area(
            "📝 Invitation Content",
            value=st.session_state.editable_body,
            height=250
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.success("🎥 Google Meet link will be auto-generated")

        st.subheader("👥 Attendees")
        for attendee in details['attendees']:
            st.info(f"📧 {attendee}")

        if st.button("✈️ Schedule Now", type="primary", use_container_width=True):
            with st.spinner("⏳ Scheduling..."):
                try:
                    calendar_service = get_calendar_service()
                    if calendar_service:
                        create_event(
                            service=calendar_service,
                            summary=details['title'],
                            description=st.session_state.editable_body,
                            attendees=details['attendees'],
                            start_time=details['start_time'],
                            end_time=details['end_time']
                        )
                        st.success("✅ Interview scheduled successfully!")
                        st.balloons()
                        st.session_state.generated_details = None
                        st.session_state.editable_body = ""
                    else:
                        st.error("❌ Could not connect to Google Calendar")
                except Exception as e:
                    st.error("❌ Failed to schedule the event")
                    st.exception(e)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👈 Fill out the form to preview your invitation")