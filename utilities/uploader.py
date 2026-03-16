import os
import requests

class PixeldrainUploader:
    BASE_URL = "https://pixeldrain.com/api"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.auth = ('', self.api_key)

    def __bool__(self) -> bool:
        try:
            url = f"{self.BASE_URL}/user"
            response = requests.get(url, auth=self.auth)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def upload_file(self, file_path: str) -> str:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        url = f"{self.BASE_URL}/file"

        with open(file_path, 'rb') as f:
            response = requests.post(url, auth=self.auth, files={"file": f})

        response.raise_for_status()
        data = response.json()

        if data.get("success"):
            return data.get("id")
        else:
            raise Exception(f"Upload failed: {data}")

    def get_download_link(self, file_id: str) -> str:
        return f"{self.BASE_URL}/file/{file_id}"

    def get_file_info(self, file_id: str) -> dict:
        url = f"{self.BASE_URL}/file/{file_id}/info"
        response = requests.get(url, auth=self.auth)
        response.raise_for_status()

        return response.json()

    def delete_file(self, file_id: str) -> bool:
        url = f"{self.BASE_URL}/file/{file_id}"
        response = requests.delete(url, auth=self.auth)
        response.raise_for_status()

        data = response.json()
        return data.get("success", False)