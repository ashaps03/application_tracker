import os
import pickle
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import re


from model import User, UserJobData
from db import db

CREDENTIALS_FILE = 'credentialsGmail.json'

def infer_status(subject):
    subj = subject.lower()
    if "interview" in subj:
        return "Interviewing"
    if "offer" in subj:
        return "Offer"
    if "unfortunately" in subj or "not selected" in subj:
        return "Rejected"
    return "Applied"

def clean_company_name(from_email):
    # Handle formats like "Name <user@company.domain.com>"
    email_match = re.search(r'<([^>]+)>', from_email)
    email = email_match.group(1) if email_match else from_email
    domain_match = re.search(r'@([a-zA-Z0-9\-]+)', email)
    if domain_match:
        domain = domain_match.group(1)
        domain = domain.replace("careers", "").replace("notifications", "").replace("jobs", "")
        domain = domain.replace("app", "").replace("-", " ")
        return domain.strip().title()
    return "Unknown"


def extract_position(subject_line):
    subject_line = subject_line.replace("RE:", "").replace("Re:", "").strip()
    if ":" in subject_line:
        return subject_line.split(":", 1)[-1].strip().title()
    return subject_line.title()


def run_gmail_scraper(firebase_uid=None):
    SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

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
    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if not user:
        print("❌ No user found in DB for Gmail UID:", firebase_uid)
        return []

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_detail.get('snippet', '')
        headers = msg_detail.get('payload', {}).get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')

        # Junk filter
        if any(ex in snippet.lower() for ex in [
            "university", "college", "scholarship", "loan", "insurance", "tuition",
            "enrollment", "student", "course", "policy", "soundcloud", "sweetwater",
            "spotify", "youtube", "apple", "quora", "music", "video", "streaming",
            "playlist", "gear", "visa", "newsletter", "articles", "SHOP", "Weekly"
        ]) or any(ex in from_email.lower() for ex in [
            "quora", "newsletter", "reddit", "soundcloud", "sweetwater", "spotify",
            "youtube", "apple", "music", "video", "streaming", "playlist", "gear",
            "visa", "articles"
        ]):
            continue

        # Check for duplicates
        cleaned_company = clean_company_name(from_email)
        position_title = extract_position(subject)

        # Check for duplicates using cleaned data
        already_exists = UserJobData.query.filter_by(
            company=cleaned_company,
            position=position_title,
            user_id=user.id
        ).first()
        if already_exists:
            continue



        # Save to DB   

        new_app = UserJobData(
            company=cleaned_company,
            position=position_title,
            status=infer_status(subject),
            user_id=user.id,
            firebase_uid=user.firebase_uid
        )

        db.session.add(new_app)
        applications.append({
            "from": from_email,
            "subject": subject,
            "date": date,
            "snippet": snippet
        })

    db.session.commit()
    return applications
