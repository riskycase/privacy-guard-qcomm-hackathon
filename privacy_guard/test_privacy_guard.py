from privacy_guard.controller import should_dim_screen

# Example browser data (replace with actual data from your browser extension)
browser_data = {
    "url": "https://example.com",
    "dom": "<html><body>Account Number: 1234567890</body></html>"
}

# Call the function to check if the screen should be dimmed
if should_dim_screen(browser_data):
    print("Screen should be dimmed (sensitive content detected with multiple faces).")
else:
    print("Screen does NOT need to be dimmed.") 