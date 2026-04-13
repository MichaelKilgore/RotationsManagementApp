from google_auth_oauthlib.flow import InstalledAppFlow
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
import os
import sys
from pathlib import Path


def _app_data_dir() -> Path:
    """Writable directory for token + credentials, works both dev and bundled."""
    d = Path.home() / '.rotations_management_app'
    d.mkdir(exist_ok=True)
    return d


def _credentials_path() -> Path:
    """
    Find credentials.json. Checks (in order):
      1. ~/.rotations_management_app/credentials.json  (user-placed copy)
      2. Next to the bundled executable (PyInstaller sys._MEIPASS)
      3. Next to this source file (dev mode)
    """
    user_path = _app_data_dir() / 'credentials.json'
    if user_path.exists():
        return user_path
    if getattr(sys, 'frozen', False):
        bundle_path = Path(sys._MEIPASS) / 'credentials.json'  # type: ignore[attr-defined]
        if bundle_path.exists():
            return bundle_path
    return Path(__file__).parent / 'credentials.json'


def init_auth():
    SCOPES = [
        'https://www.googleapis.com/auth/presentations',
        'https://www.googleapis.com/auth/drive'
    ]
    TOKEN_FILE = str(_app_data_dir() / 'token.json')
    CREDS_FILE = str(_credentials_path())

    creds = None

    # Reuse saved token if available
    if os.path.exists(TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    # If no valid credentials, do the login flow
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CREDS_FILE, SCOPES)
            creds = flow.run_local_server(port=0)  # Opens browser

        # Save token for next run
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())
    slides_service = build('slides', 'v1', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    return slides_service, drive_service

def create_google_slides(template_slide_id: str, replacements: dict) -> None:
    slides_service, drive_service = init_auth()

    copy = drive_service.files().copy(
        fileId=template_slide_id,
        body={'name': 'Rotations Management App Output'}
    ).execute()
    copy_id = copy['id']

    requests = [
        {
            'replaceAllText': {
                'containsText': {'text': placeholder},
                'replaceText': value
            }
        }
        for placeholder, value in replacements.items()
    ]

    slides_service.presentations().batchUpdate(
        presentationId=copy_id,
        body={'requests': requests}
    ).execute()

    print(f'Created: https://docs.google.com/presentation/d/{copy_id}/edit')



if __name__ == '__main__':
    create_google_slides('1oQ8zrRGx5s-LbDCpxb8FOg0e62y_bsJ_OOQo1np555Y', {'{{test}}': 'asdf'})
