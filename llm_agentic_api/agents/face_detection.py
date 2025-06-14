import os
import httpx

FACE_DETECTION_API_URL = os.getenv("FACE_DETECTION_API_URL", "http://localhost:8001/face-detect")

async def get_face_count(image_url: str) -> int:
    """
    Calls the face detection API and returns the number of faces detected in the image.
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(
            FACE_DETECTION_API_URL,
            json={"image_url": image_url},
            timeout=10.0
        )
        response.raise_for_status()
        data = response.json()
        return data.get("face_count", 0) 