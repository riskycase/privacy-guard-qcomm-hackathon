from privacy_guard.agents.face_detection import FaceDetectionAgent
from privacy_guard.agents.browser_extension import BrowserExtensionAgent
from privacy_guard.llm.sensitivity_checker import SensitivityChecker
from privacy_guard.screen_control import ScreenController
from privacy_guard.config import FACE_API_URL, LLM_URL

# Global screen controller instance to maintain state
_screen_controller = None

def get_screen_controller():
    """
    Returns a singleton instance of the ScreenController.
    """
    global _screen_controller
    if _screen_controller is None:
        _screen_controller = ScreenController()
    return _screen_controller

def should_dim_screen(browser_data: dict) -> bool:
    """
    Returns True if the screen should be dimmed (more than 1 face and sensitive content), else False.
    Also dims the screen if conditions are met.
    """
    face_agent = FaceDetectionAgent(FACE_API_URL)
    face_count = face_agent.get_face_count()

    browser_agent = BrowserExtensionAgent(browser_data)
    data = browser_agent.get_browser_data()
    url = data.get('url', '')
    dom = data.get('dom', '')

    screen_controller = get_screen_controller()
    
    if face_count > 1:
        checker = SensitivityChecker(LLM_URL)
        if checker.is_sensitive(dom, url):
            # Actually dim the screen
            screen_controller.dim_screen()
            return True
    
    # If we get here, we should ensure the screen is restored to normal brightness
    screen_controller.restore_brightness()
    return False

def dim_screen(dim_percentage=None):
    """
    Manually dim the screen to the specified percentage.
    """
    screen_controller = get_screen_controller()
    return screen_controller.dim_screen(dim_percentage)

def restore_brightness():
    """
    Manually restore the screen brightness to its original value.
    """
    screen_controller = get_screen_controller()
    return screen_controller.restore_brightness()
