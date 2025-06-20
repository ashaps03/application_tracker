import os
import pickle
import google.auth.transport.requests
import google_auth_oauthlib.flow
import googleapiclient.discovery
import re
import hashlib
from db import db
from model import UserJobData, User
from sqlalchemy import and_
import base64
from bs4 import BeautifulSoup



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
PLATFORM_DOMAINS = [
    "gmail.com", "indeed.com", "bamboohr.com", "jobylon.com", "msg.jobylon.com",
    "outlook.com", "yahoo.com", "google.com", "apple.com"
]

def clean_company_name(from_email, subject="", snippet="", payload=None):
    if 'indeedapply@indeed.com' in from_email.lower() and payload:
        parts = payload.get("parts", [])

        # Unwrap nested structure
        for part in parts:
            if part.get("mimeType") == "multipart/alternative":
                parts = part.get("parts", [])
                break

        html_body = None
        for part in parts:
            if part.get("mimeType") == "text/html":
                body_data = part.get("body", {}).get("data", "")
                try:
                    decoded = base64.urlsafe_b64decode(body_data.encode("utf-8")).decode("utf-8")
                    html_body = decoded
                    break
                except Exception as e:
                    print(f"⚠️ Error decoding base64 HTML: {e}")
                    return "Unknown"

        if html_body:
            soup = BeautifulSoup(html_body, "html.parser")

            # 🧪 DEBUG: show first few characters of HTML body
            print("🧾 INDEED HTML PREVIEW:", html_body[:500])

            # Extract from <a> tag with company name
            for a in soup.find_all("a"):
                if a.text and len(a.text.strip().split()) <= 5:
                    href = a.get("href", "")
                    if "cmp" in href or "company" in href:
                        return a.text.strip()

    # Try extracting company from subject/snippet like: "Your Application at Cobalt"
    match = re.search(r'at ([A-Z][a-zA-Z0-9& ]{2,})', subject)
    if not match:
        match = re.search(r'from ([A-Z][a-zA-Z0-9& ]{2,})', subject)
    if match:
        return match.group(1).strip()

    # Fallback to email domain
    email_match = re.search(r'@([a-zA-Z0-9.-]+)', from_email)
    if email_match:
        domain = email_match.group(1).lower()
        if domain in PLATFORM_DOMAINS:
            return "Unknown"
        clean = domain.split(".")[0].replace("-", " ")
        return clean.title()

    return "Unknown"



def extract_position(subject_line, snippet=""):
    subject_line = subject_line.replace("RE:", "").replace("Re:", "").strip()

    patterns = [
        r'application for (?:the )?(.*?)(?: position| job| at|$)',
        r'for the position of (.*?)(?: at|$)',
        r'confirmed for .*?\((.*?)\)',
        r'position: (.*?)\s',
        r'indeed application: (.*?)(?:[\n\-:|]|$)',  # Match Indeed Application: <Position>
        r'apply for the (.*?)\s*(?:position|role)',  # Catches "apply for the Tier 1..." etc

    ]
    for pattern in patterns:
        match = re.search(pattern, subject_line, re.IGNORECASE)
        if match:
            return _clean_position(match.group(1))

    # Try snippet if subject fails
    snippet_patterns = [
        r'applying to the (.*?) position at',
        r'applying for the (.*?) position',
        r'application for the (.*?) role',
        r'apply for the (Tier.*?)(?:[\.,:\n]|$)',
        r'thank you .*? apply for the (.*?)(?:[\.,:\n]|$)',
        r'position is (.*?) at',
        r'the job (.*?) at',
        r'application for: (.*?) at',
        r'job (.*?)[\.,:]',
        r'application for the following position is in process:\s*\d+[,:\- ]+(.*?)(?:[\.\n]|$)',  # 🆕 Hubbell format
        r'thank you .*? apply for the (.*?)\s*(position|role)',      # 🆕 general fallback
        r'apply for (.*?)\s*[-–—]',  # <-- ✅ catches "Tier 1 - 2 IT Service..."
        r'position is in process:.*?,\s*(.*?)(?:[\.,\n]|$)'  # <-- ✅ better Hubbell fallback

    ]
    for pattern in snippet_patterns:
        match = re.search(pattern, snippet, re.IGNORECASE)
        if match:
            return _clean_position(match.group(1))

    return "Unknown"


def _clean_position(raw):
    # Remove job ID numbers like "96089," at the start
    raw = re.sub(r'^\d+[,:\-\s]*', '', raw)

    # Truncate if there's a hyphen followed by letters (not numbers)
    if '-' in raw:
        parts = raw.split('-', 1)
        after = parts[1].strip()
        if after and not after[0].isdigit():
            raw = parts[0]

    # Truncate at punctuation or newline
    match = re.match(r'(.{5,100}?)([\.\n\r]|$)', raw)
    if match:
        raw = match.group(1)

    return raw.strip().title()





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
        'OR from:indeedapply@indeed.com OR "thank you for applying") '
        'newer_than:180d '
        '-from:forms-receipts-noreply@google.com '
        '-from:english-personalized-digest@quora.com '
        '-subject:(university OR college OR scholarship OR insurance OR enrollment OR loan OR tuition) '
        '-from:reddit.com'
    )

    results = service.users().messages().list(userId='me', q=query, maxResults=30).execute()
    messages = results.get('messages', [])

    total_fetched = len(messages)
    print(f"\n📬 Total emails fetched from Gmail API: {total_fetched}\n")

    if not messages:
        print("📭 No relevant emails found.")
        return []

    user = User.query.filter_by(firebase_uid=firebase_uid).first()
    if not user:
        print("❌ Firebase user not found.")
        return []

    seen_hashes = set()
    saved_count = 0

    for msg in messages:
        msg_detail = service.users().messages().get(userId='me', id=msg['id']).execute()
        snippet = msg_detail.get('snippet', '')


        headers = msg_detail.get('payload', {}).get('headers', [])

        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        from_email = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')

        if 'indeedapply@indeed.com' in from_email.lower():
            print("📌 INDEED SNIPPET PREVIEW:", snippet)

        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'No Date')

        company = clean_company_name(from_email, subject, snippet, msg_detail.get("payload"))
        position = extract_position(subject, snippet)
        status = infer_status(subject)

        # Filtering
        if any(ex in snippet.lower() for ex in [
            "university", "college", "scholarship", "loan", "insurance", "tuition",
            "enrollment", "student", "course", "policy", "soundcloud", "sweetwater",
            "spotify", "youtube", "apple", "quora", "music", "video", "streaming",
            "playlist", "gear", "visa", "newsletter", "articles", "shop", "weekly"
        ]) or any(ex in from_email.lower() for ex in [
            "quora", "newsletter", "reddit", "soundcloud", "sweetwater", "spotify",
            "youtube", "apple", "music", "video", "streaming", "playlist", "gear",
            "visa", "articles"
        ]):
            print(f"🚫 Filtered out: {from_email} | {subject}")

            continue

        dedup_string = f"{date.strip().lower()}|{company.strip().lower()}|{subject.strip().lower()}|{snippet.strip().lower()}"
        dedup_hash = hashlib.md5(dedup_string.encode('utf-8')).hexdigest()

        if dedup_hash in seen_hashes:
            continue
        seen_hashes.add(dedup_hash)

        print(f"📨 Email: {company} | {position} | {status}")

        existing = UserJobData.query.filter(
            and_(
                UserJobData.firebase_uid == firebase_uid,
                UserJobData.company == company,
                UserJobData.position == position,
                UserJobData.status == status
            )
        ).first()

        if not existing:
            new_entry = UserJobData(
                firebase_uid=firebase_uid,
                company=company,
                position=position,
                status=status,
                user_id=user.id
            )
            db.session.add(new_entry)
            db.session.commit()
            saved_count += 1

            print("✅ SAVED to DB:")
            print("📧 From:", from_email)
            print("📌 Subject:", subject)
            print("📆 Date:", date)
            print("🏢 Company:", company)
            print("💼 Position:", position)
            print("📊 Status:", status)
            print("📝 Snippet:", snippet)
            print("=" * 80)

    print(f"\n💾 Total emails saved to DB (no duplicates): {saved_count}")
    return []
