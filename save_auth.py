from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)  # Show browser so you can log in
    context = browser.new_context()
    page = context.new_page()
    page.goto("https://entertainment.capitalone.com/performers/759?home_or_away=home")

    input("👉 Log in manually, then press Enter here to save session...")
    
    context.storage_state(path="auth.json")
    browser.close()
