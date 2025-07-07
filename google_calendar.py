import streamlit as st
import datetime
import os.path
import uuid
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_calendar_service():
    """
    Authenticates with Google Calendar API using secrets for deployment
    and local files for development.
    """
    creds = None
    # This is the path for local development
    token_path = "token.json"
    
    try:
        # --- DEPLOYMENT METHOD ---
        # Tries to load credentials from Streamlit Cloud's secrets
        creds_info = st.secrets["google_token"]
        creds = Credentials.from_authorized_user_info(creds_info, SCOPES)
    except (KeyError, FileNotFoundError):
        # --- LOCAL DEVELOPMENT METHOD ---
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This flow runs ONLY on your local machine to get the first token.
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_path, "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        st.error(f"An error occurred with the Google API: {error}")
        return None

def create_event(service, summary, start_time, end_time, attendees=None, description=None):
    """Creates a calendar event with a unique Google Meet link."""
    event = {
        "summary": summary, "description": description,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "attendees": [{'email': email} for email in attendees] if attendees else [],
        "conferenceData": { "createRequest": {
                "requestId": f"{uuid.uuid4().hex}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"}
            }
        }
    }
    try:
        event = service.events().insert(
            calendarId="primary", body=event, sendUpdates='all', conferenceDataVersion=1
        ).execute()
        return event
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
