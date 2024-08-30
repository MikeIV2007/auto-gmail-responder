import os
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail
from dotenv import load_dotenv

# Load environment variables from the .env file
load_dotenv()

# Retrieve the SendGrid API key from environment variables
sendgrid_api_key = os.environ.get('SENDGRID_API_KEY')

# Initialize SendGrid client
sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)


sg = sendgrid.SendGridAPIClient(api_key=sendgrid_api_key)
response = sg.client.suppression.bounces.get()
print(response.status_code)
print(response.body)
print(response.headers)