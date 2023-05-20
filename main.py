import os
import datetime
import re
import requests
from dateutil import parser
from flask import Flask, jsonify, request, session, redirect, url_for, render_template
from flask_cors import CORS
from flask_session import Session
from google_auth_oauthlib.flow import Flow
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
import spacy
import dateparser
from functools import wraps

os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

# Constants
AUTH_URL = "https://accounts.google.com/o/oauth2/auth"
TOKEN_URL = "https://oauth2.googleapis.com/token"
AUTH_PROVIDER_CERT_URL = "https://www.googleapis.com/oauth2/v1/certs"
REDIRECT_URI = "https://PlainTextToGCal--anonymort.repl.co/auth/callback"
ORIGIN_URL = "https://PlainTextToGCal--anonymort.repl.co"
IP_API_URL = "https://ipapi.co/{}/timezone/"
SCOPES = ["https://www.googleapis.com/auth/calendar"]

# Load the Spacy model
nlp = spacy.load("en_core_web_sm")

app = Flask(__name__, static_folder="static", template_folder="templates")
CORS(app)

app.config.update(
    SECRET_KEY=os.getenv("SECRET_KEY"),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_TYPE="filesystem",
    PREFERRED_URL_SCHEME="https",
)

Session(app)

client_info = {
    "web": {
        "client_id": os.getenv("GOOGLE_CLIENT_ID"),
        "project_id": "plaintexttogcal",
        "auth_uri": AUTH_URL,
        "token_uri": TOKEN_URL,
        "auth_provider_x509_cert_url": AUTH_PROVIDER_CERT_URL,
        "client_secret": os.getenv("GOOGLE_CLIENT_SECRET"),
        "redirect_uris": [REDIRECT_URI],
        "javascript_origins": [ORIGIN_URL],
    }
}

flow = Flow.from_client_config(client_info, scopes=SCOPES, redirect_uri=REDIRECT_URI)

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "credentials" not in session:
            return jsonify(error="User not authenticated"), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/check_auth", methods=["GET"])
def check_auth():
    return jsonify(authenticated="credentials" in session)

@app.route("/auth", methods=["GET"])
def auth():
    auth_url, _ = flow.authorization_url(prompt="consent")
    return jsonify(authUrl=auth_url), 200

@app.route("/auth/callback", methods=["GET"])
def auth_callback():
    flow.fetch_token(authorization_response=request.url)
    credentials = flow.credentials
    session["credentials"] = credentials_to_dict(credentials)
    return redirect(url_for("home"))

@app.route("/calendars", methods=["GET"])
@login_required
def get_calendars():
    credentials = Credentials(**session["credentials"])
    service = build("calendar", "v3", credentials=credentials, static_discovery=False)

    calendar_list = service.calendarList().list().execute()
    return jsonify(calendar_list["items"]), 200

def get_user_timezone(user_ip):
    try:
        response = requests.get(IP_API_URL.format(user_ip))
        response.raise_for_status()
    except requests.exceptions.RequestException as err:
        app.logger.error(f"Unexpected Error: {err}")
        return 'UTC'
    
    return response.text

def parse_event_text(event_text, timezone):
    dateparser_settings = {
        'TIMEZONE': timezone,
        'RETURN_AS_TIMEZONE_AWARE': True
    }

    doc = nlp(event_text)

    title, event_time, event_date = None, None, None

    for ent in doc.ents:
        if ent.label_ == "DATE":
            event_date = dateparser.parse(ent.text, settings=dateparser_settings)
        elif ent.label_ == "TIME":
            event_time = dateparser.parse(ent.text, settings=dateparser_settings).time()

    title = event_text.replace(str(event_time), "").replace(str(event_date), "").strip()

    return title, event_time, event_date

@app.route("/create_event", methods=["POST"])
@login_required
def create_event():
    event_text = request.json.get("eventText")
    calendar_id = request.json.get("calendarId")

    pattern = r".+\s[0-2][0-3]:[0-5][0-9]\s[0-3][0-9]/[0-1][0-9]/\d{2,4}"
    if not re.match(pattern, event_text):
        return jsonify(error="Invalid input format. Please follow 'Event title' HH:MM DD/MM/YY"), 400

    user_ip = request.remote_addr if request.access_route[-1] == '127.0.0.1' else request.access_route[-1]

    timezone = get_user_timezone(user_ip)

    title, event_time, event_date = parse_event_text(event_text, timezone)

    if event_date is None:
        event_date = datetime.datetime.now()
    if event_time is None:
        event_time = datetime.datetime.now().time()

    event_start = datetime.datetime.combine(event_date.date(), event_time)
    event_end = event_start + datetime.timedelta(hours=1)

    event = {
        "summary": title,
        "start": {
            "dateTime": event_start.isoformat(),
            "timeZone": timezone,
        },
        "end": {
            "dateTime": event_end.isoformat(),
            "timeZone": timezone,
        },
    }

    try:
        credentials = Credentials(**session["credentials"])
        service = build("calendar", "v3", credentials=credentials, static_discovery=False)
        service.events().insert(calendarId=calendar_id, body=event).execute()
        return jsonify(success=True), 200
    except Exception as e:
        app.logger.error(f"Error creating event: {str(e)}")
        return jsonify(error="Failed to create event"), 500

@app.route("/logout", methods=["GET"])
def logout():
    session.pop("credentials", None)
    return jsonify(success=True), 200

def credentials_to_dict(credentials):
    return {
        "token": credentials.token,
        "refresh_token": credentials.refresh_token,
        "token_uri": credentials.token_uri,
        "client_id": credentials.client_id,
        "client_secret": credentials.client_secret,
        "scopes": credentials.scopes,
    }

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
