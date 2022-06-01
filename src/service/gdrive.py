import os
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload

CREDENTIALS_JSON = 'src/credentials.json'

TOKEN_JSON = 'token.json'


class GDrive:
    SCOPES = ['https://www.googleapis.com/auth/drive']

    def __init__(self):
        creds = None
        if os.path.exists(TOKEN_JSON):
            creds = Credentials.from_authorized_user_file(TOKEN_JSON, self.SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(CREDENTIALS_JSON, self.SCOPES)
                creds = flow.run_local_server(port=0)

            with open(TOKEN_JSON, 'w') as fw:
                fw.write(creds.to_json())
        self.service = build('drive', 'v3', credentials=creds)

    def list_files(self, page_size: int = 20, fields: list[str] = None) -> list[dict]:
        try:
            fields_str = ', '.join(fields) if fields else 'id, name, mimeType, size'
            response = self.service.files().list(
                pageSize=page_size,
                fields=f'nextPageToken, files({fields_str})'
            ).execute()
            return response.get('files', [])
        except HttpError as e:
            print(f'Error occurred while fetching the files list: {e.content}')

    def upload_file(self, file_path: str, mime_type: str = None):
        try:
            file_metadata = {'name': Path(file_path).name}
            media = MediaFileUpload(file_path, mimetype=mime_type, resumable=True)
            response = self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
            print(response)
        except HttpError as e:
            print(f'Error occurred while uploading the file: {e.content}')
