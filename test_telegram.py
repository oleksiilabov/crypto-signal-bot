import os
import requests

token = os.environ.get("TELEGRAM_BOT_TOKEN")
chat_id = os.environ.get("TELEGRAM_CHAT_ID")

print(f"Token present: {bool(token)}")
print(f"Chat ID present: {bool(chat_id)}")

if not token or not chat_id:
    print("❌ ERROR: Missing TELEGRAM_BOT_TOKEN or TELEGRAM_CHAT_ID secrets!")
else:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": "🔔 **Test Message:** Your Telegram connection is working successfully!",
        "parse_mode": "Markdown"
    }
    response = requests.post(url, json=payload)
    print(f"Status Code: {response.status_code}")
    print(f"Response Text: {response.text}")
