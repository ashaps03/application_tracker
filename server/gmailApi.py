import os
import pickle
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery

# Path to your credentials.json file from Google Cloud Console
CREDENTIALS_FILE = 'path/to/your/credentials.json'  # Replace with actual path
TOKEN_FILE = 'token.pickle'  # Used to save user's access token

def run_gmail_scraper():
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']
    creds = None

    # Load token if it exists
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)

    # If no valid creds, request login
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=0)

        # Save token for next time
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    # Connect to Gmail API
    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

    # 🔍 Search for job application–related emails from the last 6 months (180 days)
    query = '("thank you for applying" OR subject:application OR subject:interview) AND newer_than:180d'

    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])

    print(f"\n📥 Found {len(messages)} messages related to job applications in the last 6 months.\n")

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_detail.get('snippet', '')
        headers = msg_detail.get('payload', {}).get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')

        print(f"📧 From: {from_email}")
        print(f"📌 Subject: {subject}")
        print(f"📆 Date: {date}")
        print(f"📝 Snippet: {snippet}")
        print("=" * 60)

