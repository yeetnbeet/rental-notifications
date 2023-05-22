import json
import os
from flask import Flask, request
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)


EMAIL_SERVER = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USER = 'sam@contenderbicycles.com'
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")
FROM_EMAIL = 'sam@contenderbicycles.com'
TO_EMAILS = ['sam@contenderbicycles.com','alison@contenderbicycles.com','matt@contenderbicycles.com']


MONITORED_PRODUCT_IDS = [8048333422837,8048333717749,8048333783285,8048334930165,8051701252341,8051700859125,8051700760821,8051703906549]


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
    subject = f"RENTAL ALERT: {order_number} - {item['title']}"
    
    # Extract and format the extra options
    extra_options = ""
    if 'properties' in item:
        for prop in item['properties']:
            extra_options += f"<tr><td>{prop['name']}</td><td>{prop['value']}</td></tr>"
    
    body = f"""
<html>
<head>
<style>
    table {{
        border-collapse: collapse;
        width: 100%;
    }}
    th, td {{
        border: 1px solid black;
        padding: 8px;
        text-align: left;
    }}
    th {{
        background-color: #f2f2f2;
    }}
</style>
</head>
<body>
    <h3>Order Number: {order_number} - {item['title']}</h3>
    <p>Days: {item['quantity']}</p>
    <table>
        <thead>
            <tr>
                <th>Option</th>
                <th>Value</th>
            </tr>
        </thead>
        <tbody>
            {extra_options}
        </tbody>
    </table>
</body>
</html>
"""


    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = ', '.join(TO_EMAILS)  # Join the email addresses with a comma and a space
    
    msg.attach(MIMEText(body, 'html'))

    with smtplib.SMTP(EMAIL_SERVER, EMAIL_PORT) as server:
        server.starttls()
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)



if __name__ == "__main__":
    port = int(os.environ.get('PORT', 8000))
    app.run(debug=True, host='0.0.0.0', port=port)
