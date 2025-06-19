import streamlit as st # <-- THIS LINE WAS MISSING. IT IS NOW FIXED.
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
    Authenticates with Google Calendar API using secrets for deployment.
    """
    # Load credentials from Streamlit's secrets.
    creds_info = {
        "token": st.secrets["google_token"]["token"],
        "refresh_token": st.secrets["google_token"]["refresh_token"],
        "token_uri": st.secrets["google_oauth"]["token_uri"],
        "client_id": st.secrets["google_oauth"]["client_id"],
        "client_secret": st.secrets["google_oauth"]["client_secret"],
        "scopes": SCOPES
    }

    creds = Credentials.from_authorized_user_info(creds_info, SCOPES)

    # If the token is expired, refresh it
    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        st.error(f"An error occurred with Google API: {error}")
        return None

def create_event(service, summary, start_time, end_time, attendees=None, description=None):
    """
    Creates an event in the user's calendar, sends invitations,
    and automatically generates a Google Meet link.
    """
    event = {
        "summary": summary,
        "description": description,
        "start": {"dateTime": start_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "end": {"dateTime": end_time.isoformat(), "timeZone": "Asia/Kolkata"},
        "conferenceData": {
            "createRequest": {
                "requestId": f"{uuid.uuid4().hex}",
                "conferenceSolutionKey": {"type": "hangoutsMeet"},
            }
        },
    }
    if attendees:
        event["attendees"] = [{"email": email} for email in attendees]

    try:
        event = service.events().insert(
            calendarId="primary", 
            body=event, 
            sendUpdates='all',
            conferenceDataVersion=1
        ).execute()
        return event
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None
