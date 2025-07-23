import os
os.environ["PLAYWRIGHT_BROWSERS_PATH"] = "/tmp/pw-browsers"

import asyncio
from playwright.async_api import async_playwright
import json, time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# 🔧 Email Config (use environment variables for sensitive info)
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
EMAIL_SENDER = os.environ.get("EMAIL_SENDER", "delliottflock@gmail.com")
EMAIL_PASSWORD = os.environ.get("EMAIL_PASSWORD", "")
EMAIL_RECIPIENT = os.environ.get("EMAIL_RECIPIENT", "delliottflock@gmail.com")

# 🔗 The URL to monitor for new "Cardholder Exclusive" tickets
URL = "https://entertainment.capitalone.com/performers/759?home_or_away=home"

# 📁 Files used to persist state and log alerts
STATE_FILE = "state.json"     # Tracks which items we've already seen
ALERT_LOG = "alerts.log"      # Logs new items when they appear

# 📄 Load previously seen "Cardholder Exclusive" listings from state.json
def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE) as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading state file: {e}")
            return {"seen": []}
    else:
        return {"seen": []}

# 💾 Save updated list of seen listings to state.json
def save_state(state):
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f)
    except Exception as e:
        print(f"Error saving state file: {e}")

# 🚨 Send an alert (prints, logs, and emails)
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
    if EMAIL_PASSWORD:
        try:
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
                server.starttls()
                server.login(EMAIL_SENDER, EMAIL_PASSWORD)
                server.sendmail(EMAIL_SENDER, EMAIL_RECIPIENT, msg.as_string())
            print("Email sent.")
        except Exception as e:
            print("Error sending email:", e)
    else:
        print("Email password not set. Skipping email.")

    # Log to file
    try:
        with open(ALERT_LOG, "a") as f:
            f.write(f"{time.ctime()}: {item_text}\n")
    except Exception as e:
        print(f"Error writing to alert log: {e}")

# 🚀 Main routine that launches the browser and checks for new tickets
async def main():
    state = load_state()  # Load existing state

    try:
        async with async_playwright() as p:
            try:
                browser = await p.chromium.launch(headless=True)
                context = await browser.new_context(storage_state="auth.json")
            except Exception as e:
                print(f"Error launching browser or loading auth.json: {e}")
                return

            page = await context.new_page()
            try:
                await page.goto(URL)
                await page.wait_for_selector("text=Cardholder Exclusive", timeout=15000)
            except Exception as e:
                print(f"Error loading page or waiting for selector: {e}")
                await browser.close()
                return

            elements = page.locator("text=Cardholder Exclusive")
            try:
                count = await elements.count()
            except Exception as e:
                print(f"Error counting elements: {e}")
                await browser.close()
                return

            new_items = []
            for i in range(count):
                try:
                    text = await elements.nth(i).text_content()
                    if text and text not in state["seen"]:
                        new_items.append(text)
                        state["seen"].append(text)
                except Exception as e:
                    print(f"Error reading element text: {e}")

            if new_items:
                for item in new_items:
                    send_alert(item)
                save_state(state)

            await browser.close()
    except Exception as e:
        print(f"Unexpected error: {e}")

# 🏁 Entry point for notebook or script
if __name__ == "__main__":
    asyncio.run(main())