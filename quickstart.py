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

# Set up email details
from_email = Email("ivmv2007@gmail.com")
to_email = To("mykhailoivanov97@gmail.com")
subject = "Sending with SendGrid is Fun"
content = Content("text/plain", "and easy to do anywhere, even with Python")

# Create a Mail object and send the email
mail = Mail(from_email, to_email, subject, content)
response = sg.client.mail.send.post(request_body=mail.get())

# Print the response
print(response.status_code)
print(response.body)
print(response.headers)
