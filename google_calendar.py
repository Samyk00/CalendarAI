import streamlit as st
import datetime
import os.path
import uuid

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.events"]

def get_calendar_service():
    """
    Authenticates with Google Calendar API using secrets for deployment.
    This version is simplified and ONLY uses secrets, it will not work locally.
    """
    try:
        # Load credentials directly from the google_token secret.
        creds_info = st.secrets["google_token"]
        creds = Credentials.from_authorized_user_info(creds_info, SCOPES)

        # If the token is expired, refresh it
        if not creds.valid and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        service = build("calendar", "v3", credentials=creds)
        return service
    except (KeyError, FileNotFoundError):
         st.error("Google credentials are not configured correctly in Streamlit Secrets.")
         return None
    except Exception as e:
        st.error(f"An error occurred with Google API authentication: {e}")
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
