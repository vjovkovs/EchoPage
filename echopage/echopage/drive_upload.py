# echopage/drive_upload.py
import os
import pickle
from pathlib import Path

from dotenv import load_dotenv
from echopage.logger import setup_logger

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

load_dotenv()
logger = setup_logger()

# Drive API settings
SCOPES = ['https://www.googleapis.com/auth/drive.file']
CREDS_PATH = Path(os.getenv("GOOGLE_CREDENTIALS_PATH", "credentials.json"))
TOKEN_PATH = Path(os.getenv("GOOGLE_TOKEN_PATH", "token.pickle"))
DRIVE_PARENT_FOLDER_ID = os.getenv("DRIVE_PARENT_FOLDER_ID")  # put your root folder ID here

def authenticate() -> build:
    """Authenticate and return a Drive v3 service object."""
    creds = None
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDS_PATH), SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for next run
        with open(TOKEN_PATH, 'wb') as token_file:
            pickle.dump(creds, token_file)
    return build('drive', 'v3', credentials=creds)

def create_folder(service, name: str, parent_id: str = None) -> str:
    """Create a folder in Drive (if not exists) and return its ID."""
    # First, check if folder exists
    query = f"mimeType='application/vnd.google-apps.folder' and name='{name}'"
    if parent_id:
        query += f" and '{parent_id}' in parents"
    res = service.files().list(q=query, spaces='drive', fields='files(id,name)').execute()
    files = res.get('files', [])
    if files:
        folder_id = files[0]['id']
        logger.debug(f"Found existing folder '{name}' ({folder_id})")
        return folder_id

    # Create new folder
    metadata = {
        'name': name,
        'mimeType': 'application/vnd.google-apps.folder',
    }
    if parent_id:
        metadata['parents'] = [parent_id]
    folder = service.files().create(body=metadata, fields='id').execute()
    folder_id = folder.get('id')
    logger.info(f"Created folder '{name}' ({folder_id})")
    return folder_id

def upload_file(service, file_path: Path, parent_id: str):
    """Upload a single file to Drive under parent_id."""
    file_metadata = {
        'name': file_path.name,
        'parents': [parent_id]
    }
    media = MediaFileUpload(str(file_path), resumable=True)
    uploaded = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()
    logger.info(f"Uploaded {file_path.name} → {uploaded.get('id')}")

def upload_outputs(novel_title: str) -> None:
    """
    Uploads all files in output/<NovelTitle>/ to Google Drive.
    Creates a folder under DRIVE_PARENT_FOLDER_ID named <NovelTitle>.
    """
    service = authenticate()
    root_folder_id = DRIVE_PARENT_FOLDER_ID or None
    novel_folder_id = create_folder(service, novel_title, root_folder_id)

    local_dir = Path("output") / novel_title.replace(" ", "_")
    if not local_dir.exists():
        logger.error(f"Output directory not found: {local_dir}")
        return

    for file in sorted(local_dir.rglob('*')):
        if file.is_file():
            upload_file(service, file, novel_folder_id)

    logger.info(f"All files from {local_dir} uploaded to Drive folder '{novel_title}'")
