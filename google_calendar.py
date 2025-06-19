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
    """Shows basic usage of the Google Calendar API."""
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        print(f"An error occurred: {error}")
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
        # --- THE FIX IS HERE ---
        # The 'conferenceDataVersion=1' parameter is required to process the conferenceData request.
        event = service.events().insert(
            calendarId="primary",
            body=event,
            sendUpdates='all',
            conferenceDataVersion=1  # <-- This line is critical and was missing.
        ).execute()
        
        print(f"Event created: {event.get('htmlLink')}")
        print(f"Google Meet Link: {event.get('hangoutLink')}") # The link is available here *after* creation
        return event
    except HttpError as error:
        print(f"An error occurred: {error}")
        return None