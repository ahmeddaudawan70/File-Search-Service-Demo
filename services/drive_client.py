from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
import io
from abc import ABC, abstractmethod
from typing import List, Dict
from config.settings import GOOGLE_DRIVE_SCOPES, CREDENTIALS_FILE
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DriveService(ABC):
    @abstractmethod
    def list_files(self) -> List[Dict]:
        pass

    @abstractmethod
    def download_file_content(self, file: Dict) -> bytes:
        pass

class DriveClient(DriveService):
    def __init__(self):
        self.service = self._authenticate()

    def _authenticate(self):
        creds = None
        try:
            creds = Credentials.from_authorized_user_file('token.json', GOOGLE_DRIVE_SCOPES)
            logger.info("Authenticated with existing token.json")
        except FileNotFoundError:
            logger.info("No token.json found, initiating OAuth flow")
            flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_FILE, GOOGLE_DRIVE_SCOPES)
            creds = flow.run_local_server(port=3000)
            with open('token.json', 'w') as token:
                token.write(creds.to_json())
            logger.info("OAuth flow completed, token.json saved")
        except Exception as e:
            logger.error("Authentication failed: %s", e)
            raise
        return build('drive', 'v3', credentials=creds, cache_discovery=False)

    def list_files(self) -> List[Dict]:
        folder_id = "1AvumiwFUj9c0fHsrlYze5NRcdww0wloJ"  # Replace with your actual folder ID
        try:
            logger.info("Fetching files from Google Drive folder ID: %s", folder_id)
            results = self.service.files().list(
                q=f"'{folder_id}' in parents and (mimeType='text/csv' or mimeType='text/plain' or mimeType='application/pdf' or mimeType='image/png')",
                fields="files(id, name, mimeType, webViewLink)"
            ).execute()
            files = results.get('files', [])
            if not files:
                logger.warning("No files found in folder ID: %s", folder_id)
            else:
                logger.info("Files retrieved from Google Drive:")
                for file in files:
                    logger.info(f"Name: {file['name']}, ID: {file['id']}, MIME Type: {file['mimeType']}, URL: {file.get('webViewLink', 'N/A')}")
            return files
        except Exception as e:
            logger.error("Error listing files: %s", e)
            return []

    def download_file_content(self, file: Dict) -> bytes:
        try:
            logger.info("Downloading content for file: %s (ID: %s)", file['name'], file['id'])
            request = self.service.files().get_media(fileId=file['id'])
            fh = io.BytesIO()
            downloader = MediaIoBaseDownload(fh, request)
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            fh.seek(0)
            content = fh.read()
            logger.info("Downloaded content for %s (length: %d bytes)", file['name'], len(content))
            return content
        except Exception as e:
            logger.error("Error downloading file %s: %s", file.get('name', 'unknown'), e)
            return b""