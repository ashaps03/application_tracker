import os
import pickle
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery

# Path to your credentials.json file from Google Cloud Console
CREDENTIALS_FILE = 'credentialsGmail.json'  # Replace with actual path
  # Used to save user's access token

def run_gmail_scraper(firebase_uid=None):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

    # Use token file specific to user if UID is provided
    if firebase_uid:
        os.makedirs("tokens", exist_ok=True)
        token_path = f'tokens/{firebase_uid}_token.pickle'
    else:
        token_path = 'token.pickle'

    creds = None
    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(google.auth.transport.requests.Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                CREDENTIALS_FILE, SCOPES
            )
            creds = flow.run_local_server(port=8081)

        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)

    service = googleapiclient.discovery.build('gmail', 'v1', credentials=creds)

    ## make this query as specific as possible.
    query = (
        '(subject:"job application" OR subject:"interview" '
        'OR "thank you for applying" OR "we received your application" '
        'OR "next steps in your application" OR "application update" OR "invitation to interview") '
        'newer_than:180d '
        '-from:forms-receipts-noreply@google.com '
        '-from:english-personalized-digest@quora.com '
        '-subject:(university OR college OR scholarship OR insurance OR enrollment OR loan OR tuition) '
        '-from:reddit.com'
    )

    results = service.users().messages().list(userId='me', q=query, maxResults=10).execute()
    messages = results.get('messages', [])

    applications = []
    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_detail.get('snippet', '')
        headers = msg_detail.get('payload', {}).get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')

        if any(ex in snippet.lower() for ex in [
            "university", "college", "scholarship", "loan", "insurance",
            "tuition", "enrollment", "student", "course", "policy", "soundcloud", 
            "sweetwater", "spotify", "youtube", "apple", "quora", "music", "video", 
            "streaming", "playlist", "gear", "visa", "newsletter", "articles", "SHOP", "Weekly"
        ]):
            continue

        if any(ex in from_email.lower() for ex in [
            "quora", "newsletter", "reddit", 
            "soundcloud", "sweetwater", "spotify", "youtube", "apple", "quora", "music", 
            "video", "streaming", "playlist", "gear", "visa", "newsletter", "articles"
        ]): continue 

        print(f"📧 From: {from_email}")
        print(f"📌 Subject: {subject}")
        print(f"📆 Date: {date}")
        print(f"📝 Snippet: {snippet}")
        print("=" * 60)
        applications.append({
                "from": from_email,
                "subject": subject,
                "date": date,
                "snippet": snippet
            })

    return applications