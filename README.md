

# PlainTextToGCal

A Flask web application to create Google Calendar events from plaintext inputs. The application makes use of Google OAuth2 for authentication and Google Calendar API to create events.

### Features

 - User authentication using Google OAuth2. Fetches a list of user's
 - Google Calendars. Input events as plain text and convert it to a
 - Google Calendar event. Extracts date and time information from plain text using Spacy and Dateparser.
 - Automatically detects the user's timezone using IP address.

### Getting Started
#### Prerequisites
Before you begin, ensure you have met the following requirements:

 - Python 3.6 or later
 - Pip (Python package manager)
 - Google API credentials (Client ID and Client Secret)
 - Spacy language model (en_core_web_sm)

#### Installation
Clone the repository

    git clone https://github.com/yourusername/PlainTextToGCal.git
    cd PlainTextToGCal

Install the required Python packages

    pip install -r requirements.txt

Download the Spacy language model

    python -m spacy download en_core_web_sm

Set the following environment variables:

    GOOGLE_CLIENT_ID: Your Google API client ID
    GOOGLE_CLIENT_SECRET: Your Google API client secret
    SECRET_KEY: A secret key for Flask application. This can be a random string.

Run the application

    python main.py

#### Usage

 - Open the application in your web browser. If running locally, go to
   http://localhost:8080.
 - Click the "Authenticate with Google" button to log in with your Google account. After authentication, input an event in the form 'Event title HH:MM DD/MM/YY', for example, 'Doctor appointment 10:30 01/01/24'. 
 - Click the "Create Event" button to add the event to your selected Google Calendar. 

Contributing Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

#### License
This project is licensed under the MIT License - see the LICENSE.md file for details.
