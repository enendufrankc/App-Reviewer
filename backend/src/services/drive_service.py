import io
import asyncio
import pandas as pd
from typing import Optional
from concurrent.futures import ThreadPoolExecutor
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import re

from src.config.settings import AppConfig

class GoogleDriveService:
    def __init__(self, config: AppConfig):
        self.config = config
        self._service = None
    
    def get_service(self):
        """Get or create Google Drive service instance"""
        if self._service is None:
            credentials = service_account.Credentials.from_service_account_file(
                self.config.service_account_file, 
                scopes=self.config.scopes
            )
            self._service = build('drive', 'v3', credentials=credentials)
        return self._service
    
    @staticmethod
    def extract_file_id(drive_url: str) -> Optional[str]:
        """Extract file ID from Google Drive URL"""
        if not drive_url or pd.isna(drive_url):
            return None
        
        patterns = [
            r'/file/d/([a-zA-Z0-9-_]+)',
            r'id=([a-zA-Z0-9-_]+)',
            r'/d/([a-zA-Z0-9-_]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, str(drive_url))
            if match:
                return match.group(1)
        return None
    
    async def download_file(self, file_id: str, destination_path: str) -> bool:
        """Download file from Google Drive asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    self._download_file_sync, 
                    file_id, 
                    destination_path
                )
            return result
        except Exception as e:
            print(f"Error downloading file {file_id}: {str(e)}")
            return False
    
    def _download_file_sync(self, file_id: str, destination_path: str) -> bool:
        """Synchronous file download helper"""
        try:
            service = self.get_service()
            request = service.files().get_media(fileId=file_id)
            file_io = io.BytesIO()
            downloader = MediaIoBaseDownload(file_io, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
            
            with open(destination_path, 'wb') as f:
                f.write(file_io.getvalue())
            
            return True
        except Exception as e:
            print(f"Sync download error: {str(e)}")
            return False
    
    async def upload_file(self, file_path: str, mime_type: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Upload a file to Google Drive asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                file_id = await loop.run_in_executor(
                    executor, 
                    self._upload_file_sync, 
                    file_path, 
                    mime_type, 
                    parent_id
                )
            return file_id
        except Exception as e:
            print(f"Error uploading file {file_path}: {str(e)}")
            return None
    
    def _upload_file_sync(self, file_path: str, mime_type: str, parent_id: Optional[str] = None) -> Optional[str]:
        """Synchronous file upload helper"""
        try:
            service = self.get_service()
            file_metadata = {
                'name': file_path.split('/')[-1],
                'mimeType': mime_type
            }
            if parent_id:
                file_metadata['parents'] = [parent_id]
            
            media = MediaFileUpload(file_path, mime_type=mime_type)
            file = service.files().create(
                body=file_metadata,
                media_body=media,
                fields='id'
            ).execute()
            
            return file.get('id')
        except Exception as e:
            print(f"Sync upload error: {str(e)}")
            return None
    
    async def delete_file(self, file_id: str) -> bool:
        """Delete a file from Google Drive asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                result = await loop.run_in_executor(
                    executor, 
                    self._delete_file_sync, 
                    file_id
                )
            return result
        except Exception as e:
            print(f"Error deleting file {file_id}: {str(e)}")
            return False
    
    def _delete_file_sync(self, file_id: str) -> bool:
        """Synchronous file delete helper"""
        try:
            service = self.get_service()
            service.files().delete(fileId=file_id).execute()
            return True
        except Exception as e:
            print(f"Sync delete error: {str(e)}")
            return False
    
    async def list_files(self, query: str = "", page_size: int = 10) -> list:
        """List files in Google Drive asynchronously"""
        try:
            loop = asyncio.get_event_loop()
            with ThreadPoolExecutor() as executor:
                files = await loop.run_in_executor(
                    executor, 
                    self._list_files_sync, 
                    query, 
                    page_size
                )
            return files
        except Exception as e:
            print(f"Error listing files: {str(e)}")
            return []
    
    def _list_files_sync(self, query: str = "", page_size: int = 10) -> list:
        """Synchronous file list helper"""
        try:
            service = self.get_service()
            results = service.files().list(
                q=query,
                pageSize=page_size,
                fields="nextPageToken, files(id, name, mimeType)"
            ).execute()
            items = results.get('files', [])
            
            files = []
            for item in items:
                files.append({
                    'id': item['id'],
                    'name': item['name'],
                    'mimeType': item['mimeType']
                })
            
            return files
        except Exception as e:
            print(f"Sync list error: {str(e)}")
            return []