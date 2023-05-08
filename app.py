import json
import os
from flask import Flask, request
import smtplib
from email.mime.text import MIMEText

app = Flask(__name__)

# Replace the following with your own email credentials and settings
EMAIL_SERVER = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'sam@contenderbicycles.com'
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_EMAIL = 'sam@contenderbicycles.com'
TO_EMAIL = 'sam@contenderbicycles.com'

# Replace this with the product ID(s) you want to monitor
MONITORED_PRODUCT_IDS = [1234567890,8048333422837]


@app.route('/webhook', methods=['POST'])
def handle_webhook():
    data = json.loads(request.data)
    print(f"Received webhook data: {data}")
    line_items = data['line_items']
    
    for item in line_items:
        if item['product_id'] in MONITORED_PRODUCT_IDS:
            send_email_notification(item, data['order_number'])
            break

    return '', 200


def send_email_notification(item, order_number):
    subject = f"RENTAL ALERT: {item['title']}"
    
    # Extract and format the extra options
    extra_options = ""
    if 'properties' in item:
        for prop in item['properties']:
            extra_options += f"{prop['name']}: {prop['value']}\n"
    
    body = f"Order Number: {order_number} - {item['title']} has been sold. Quantity: {item['quantity']}\n{extra_options}"

    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = TO_EMAIL

    with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
