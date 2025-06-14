import requests

class FaceDetectionAgent:
    def __init__(self, api_url: str):
        self.api_url = api_url

    def get_face_count(self) -> int:
        """
        Calls the face detection API and returns the number of faces detected.
        Expects the API to return JSON: {"face_count": <int>}
        """
        try:
            response = requests.get(self.api_url, timeout=3)
            response.raise_for_status()
            data = response.json()
            return int(data.get("face_count", 0))
        except Exception:
            return 0 