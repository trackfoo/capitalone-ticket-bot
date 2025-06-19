from playwright.sync_api import sync_playwright
import json, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/tmp/pw-browsers"

# 🔧 Email Config (replace these)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = "delliottflock@gmail.com"
EMAIL_PASSWORD = "onsiiismmjanmjzg"
EMAIL_RECIPIENT = "delliottflock@gmail.com"

# 🔗 The URL to monitor for new "Cardholder Exclusive" tickets
URL = "https://entertainment.capitalone.com/performers/759?home_or_away=home"

# 📁 Files used to persist state and log alerts
STATE_FILE = "state.json"     # Tracks which items we've already seen
ALERT_LOG = "alerts.log"      # Logs new items when they appear

# 📄 Load previously seen "Cardholder Exclusive" listings from state.json
def load_state():
    if os.path.exists(STATE_FILE):
        return json.load(open(STATE_FILE))
    else:
        return {"seen": []}

# 💾 Save updated list of seen listings to state.json
def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f)

# 🚨 Send an alert (right now just prints and logs to file)
def send_alert(item_text):
    print("ALERT:", item_text)

    # Prepare email
    subject = "🎟️ New Capital One Cardholder Exclusive Found"
    body = f"New item detected:\n\n{item_text}\n\n{URL}"
    msg = MIMEMultipart()
    msg['From'] = EMAIL_SENDER
    msg['To'] = EMAIL_RECIPIENT
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Send email
    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(EMAIL_SENDER, EMAIL_PASSWORD)
            server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
        print("Email sent.")
    except Exception as e:
        print("Error sending email:", e)

    # Still log to file
    with open(ALERT_LOG, "a") as f:
        f.write(f"{time.ctime()}: {item_text}\n")


# 🚀 Main routine that launches the browser and checks for new tickets
def main():
    state = load_state()  # Load existing state so we don't alert on old listings

    with sync_playwright() as p:  # Start Playwright in sync mode
        # 🔒 Launch browser and load saved login session from auth.json
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state="auth.json")

        # 🌐 Navigate to the Capital One MLB tickets page
        page = context.new_page()
        page.goto(URL)

        # ⏳ Wait for the page to load listings with the phrase "Cardholder Exclusive"
        page.wait_for_selector("text=Cardholder Exclusive", timeout=15000)

        # 🔍 Find all occurrences of "Cardholder Exclusive"
        elements = page.locator("text=Cardholder Exclusive")
        count = elements.count()

        new_items = []  # Store unseen items

        # 🔁 Loop through all matching elements
        for i in range(count):
            text = elements.nth(i).text_content()
            if text not in state["seen"]:
                new_items.append(text)           # New item found
                state["seen"].append(text)       # Add to state so we don't alert again

        # ✅ If we found new items, alert and update state
        if new_items:
            for item in new_items:
                send_alert(item)
            save_state(state)

        browser.close()  # Clean up the browser session

# 🏁 Entry point
if __name__ == "__main__":
    main()
