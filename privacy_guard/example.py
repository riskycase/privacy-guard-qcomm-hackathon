"""
Example script demonstrating how to use the Privacy Guard package with screen brightness control.
"""
from controller import should_dim_screen, dim_screen, restore_brightness

def main():
    """
    Main function demonstrating Privacy Guard usage.
    """
    print("Privacy Guard Example")
    print("=====================")
    
    # Example browser data - in a real application, this would come from the browser extension
    browser_data = {
        "url": "https://example.com/sensitive-financial-data",
        "dom": "<html><body><h1>Sensitive Financial Information</h1><p>Account: 123456789</p><p>Balance: $10,000</p></body></html>"
    }
    
    print("Checking if screen should be dimmed...")
    should_dim = should_dim_screen(browser_data)
    
    if should_dim:
        print("Screen has been dimmed due to sensitive content and multiple faces detected.")
    else:
        print("Screen brightness maintained at normal level.")
    
    # Example of manual control
    print("\nManual Control Examples:")
    print("------------------------")
    print("Dimming screen to 20% brightness...")
    dim_screen(20)
    
    input("Press Enter to restore brightness...")
    
    print("Restoring screen to original brightness...")
    restore_brightness()
    
    print("\nExample completed.")

if __name__ == "__main__":
    main()
