import os
import io
import mimetypes
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
from fastapi import HTTPException
import json

# Define the scopes required for Drive and Docs APIs
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_drive_service():
    """Initializes and returns the Google Drive API service."""
    # Read token JSON from .env
    token_json_str = os.getenv("GOOGLE_OAUTH_TOKEN_JSON")
    
    if not token_json_str:
        raise HTTPException(
            status_code=500, 
            detail="Google OAuth token not found in .env. Please run get_google_token.py first."
        )
    
    try:
        creds_data = json.loads(token_json_str)
        creds = Credentials.from_authorized_user_info(creds_data, SCOPES)
        service = build('drive', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"[Google API Error] Failed to initialize Google Drive service: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize Google Drive service.")

from dotenv import load_dotenv

load_dotenv()
FOLDER_ID = os.getenv("GOOGLE_DRIVE_FOLDER_ID")

def upload_to_google_docs(file_content: bytes, filename: str) -> str:
    """
    Uploads a file content (e.g., .docx bytes) to Google Drive and converts it to a Google Doc.
    Returns the Google Doc ID.
    """
    service = get_drive_service()
    
    file_metadata = {
        'name': filename,
        'mimeType': 'application/vnd.google-apps.document'  # Force conversion to Google Docs
    }
    
    if FOLDER_ID:
        clean_folder_id = FOLDER_ID
        if "folders/" in clean_folder_id:
            clean_folder_id = clean_folder_id.split("folders/")[-1].split("?")[0].strip("/").strip()
        file_metadata['parents'] = [clean_folder_id]
        
    source_mimetype, _ = mimetypes.guess_type(filename)
    if not source_mimetype:
        # Default to docx if we can't guess, although it usually handles docx/pdf well
        source_mimetype = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'

    # We use io.BytesIO to upload from memory instead of a file on disk
    media = MediaIoBaseUpload(
        io.BytesIO(file_content),
        mimetype=source_mimetype,
        resumable=True
    )
    
    try:
        file = service.files().create(
            body=file_metadata,
            media_body=media,
            fields='id'
        ).execute()
        
        doc_id = file.get('id')
        print(f"[Google Drive] Successfully uploaded and converted. Document ID: {doc_id}")
        
        # Make the file readable by anyone with the link (so the user can open it)
        permission = {
            'type': 'anyone',
            'role': 'writer',  # 'writer' allows the user to edit the file when they open the link
        }
        service.permissions().create(
            fileId=doc_id,
            body=permission,
            fields='id'
        ).execute()
        
        return doc_id
    except Exception as e:
        print(f"[Google API Error] File upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to upload to Google Docs: {str(e)}")