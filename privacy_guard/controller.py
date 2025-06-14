from privacy_guard.agents.face_detection import FaceDetectionAgent
from privacy_guard.agents.browser_extension import BrowserExtensionAgent
from privacy_guard.llm.sensitivity_checker import SensitivityChecker
from privacy_guard.config import FACE_API_URL, LLM_URL

# browser_data should be provided as input to the function

def should_dim_screen(browser_data: dict) -> bool:
    """
    Returns True if the screen should be dimmed (more than 1 face and sensitive content), else False.
    """
    face_agent = FaceDetectionAgent(FACE_API_URL)
    face_count = face_agent.get_face_count()

    browser_agent = BrowserExtensionAgent(browser_data)
    data = browser_agent.get_browser_data()
    url = data.get('url', '')
    dom = data.get('dom', '')

    if face_count > 1:
        checker = SensitivityChecker(LLM_URL)
        if checker.is_sensitive(dom, url):
            return True
    return False
