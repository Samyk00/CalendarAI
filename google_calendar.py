# In google_calendar.py

def get_calendar_service():
    """
    Authenticates with Google Calendar API using secrets for deployment.
    """
    # Load credentials from Streamlit's secrets
    creds_json = {
        "web": {
            "client_id": st.secrets["google_oauth"]["client_id"],
            "project_id": st.secrets["google_oauth"]["project_id"],
            "auth_uri": st.secrets["google_oauth"]["auth_uri"],
            "token_uri": st.secrets["google_oauth"]["token_uri"],
            "auth_provider_x509_cert_url": st.secrets["google_oauth"]["auth_provider_x509_cert_url"],
            "client_secret": st.secrets["google_oauth"]["client_secret"],
            "redirect_uris": st.secrets["google_oauth"]["redirect_uris"]
        }
    }
    
    token_json = {
        "token": st.secrets["google_token"]["token"],
        "refresh_token": st.secrets["google_token"]["refresh_token"],
        "token_uri": st.secrets["google_token"]["token_uri"],
        "client_id": st.secrets["google_token"]["client_id"],
        "client_secret": st.secrets["google_token"]["client_secret"],
        "scopes": st.secrets["google_token"]["scopes"],
        "expiry": st.secrets["google_token"]["expiry"]
    }

    creds = Credentials.from_authorized_user_info(token_json, SCOPES)

    if not creds.valid:
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # This part should ideally not be reached if the token is valid or refreshable
            st.error("Google authentication failed. Please check your token secrets.")
            return None
    
    try:
        service = build("calendar", "v3", credentials=creds)
        return service
    except HttpError as error:
        st.error(f"An error occurred: {error}")
        return None