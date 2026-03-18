import os
import requests

class PixeldrainUploader:
    BASE_URL = "https://pixeldrain.com/api"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.auth = ('', self.api_key)

    def __bool__(self) -> bool:
        try:
            print("Checking Pixeldrain API connection...")
            url = f"{self.BASE_URL}/user"
            response = requests.get(url, auth=self.auth)
            status = response.status_code == 200
            return status
        except requests.RequestException as e:
            print(f"API Connection Error: {e}")
            return False

    def upload_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            print(f"Upload error: File {file_path} not found.")
            raise FileNotFoundError(f"File not found: {file_path}")

        print(f"Uploading file to Pixeldrain: {file_path}...")
        url = f"{self.BASE_URL}/file"

        with open(file_path, 'rb') as f:
            response = requests.post(url, auth=self.auth, files={"file": f})

        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            file_id = data.get("id")
            print(f"Successfully uploaded! File ID: {file_id}")
            return file_id
        else:
            print(f"Pixeldrain upload failed: {data}")
            raise Exception(f"Upload failed: {data}")

    def get_download_link(self, file_id: str) -> str:
        return f"{self.BASE_URL}/file/{file_id}"

    def get_file_info(self, file_id: str) -> dict:
        print(f"Fetching info for file ID: {file_id}...")
        url = f"{self.BASE_URL}/file/{file_id}/info"
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()
        return response.json()

    def delete_file(self, file_id: str) -> bool:
        print(f"Deleting file from Pixeldrain (ID: {file_id})...")
        url = f"{self.BASE_URL}/file/{file_id}"
        response = requests.delete(url, auth=self.auth)
        response.raise_for_status()

        data = response.json()
        success = data.get("success", False)
        if success:
            print(f"File {file_id} deleted successfully from Pixeldrain.")
        else:
            print(f"Failed to delete file {file_id} from Pixeldrain.")
        return success