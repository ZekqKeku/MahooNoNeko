import os
import requests
import asyncio

class PixeldrainUploader:
    BASE_URL = "https://pixeldrain.com/api"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.auth = ('', self.api_key)

    async def check_connection(self) -> bool:
        try:
            print("Checking Pixeldrain API connection...")
            url = f"{self.BASE_URL}/user"
            
            def _check():
                return requests.get(url, auth=self.auth)
            
            response = await asyncio.to_thread(_check)
            status = response.status_code == 200
            return status
        except Exception as e:
            print(f"API Connection Error: {e}")
            return False

    async def upload_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            print(f"Upload error: File {file_path} not found.")
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Uploading file to Pixeldrain: {file_path}...")
        url = f"{self.BASE_URL}/file"

        def _upload():
            with open(file_path, 'rb') as f:
                return requests.post(url, auth=self.auth, files={"file": f})

        response = await asyncio.to_thread(_upload)
        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            file_id = data.get("id")
            print(f"Successfully uploaded! File ID: {file_id}")
            return file_id
        else:
            print(f"Pixeldrain upload failed: {data}")
            raise Exception(f"Upload failed: {data}")

    def get_download_direct_link(self, file_id: str) -> str:
        return f"{self.BASE_URL}/file/{file_id}"

    def get_download_link(self, file_id: str) -> str:
        return f"https://pixeldrain.com/u/{file_id}"