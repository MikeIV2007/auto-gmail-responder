import os
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail
from dotenv import load_dotenv

class SendGridEmailSender:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv()
        # Retrieve the SendGrid API key from environment variables
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        # Initialize SendGrid client
        self.sg = sendgrid.SendGridAPIClient(api_key=self.api_key)

    def send_email(self, from_email, to_email, subject, content):
        # Create the email components
        from_email_obj = Email(from_email)
        to_email_obj = To(to_email)
        content_obj = Content("text/plain", content)
        
        # Create a Mail object
        mail = Mail(from_email_obj, to_email_obj, subject, content_obj)
        
        # Send the email and return the response
        response = self.sg.client.mail.send.post(request_body=mail.get())
        return response

# Usage example
if __name__ == "__main__":
    email_sender = SendGridEmailSender()
    
    #from_email = "ivmv2007@gmail.com"
    from_email = "mykhailoivanov97@gmail.com"
    #to_email = "ivmv@ukr.net"
    to_email = "ivmv@meta.ua"
    subject = "Sending with SendGrid is Fun"
    content = "and easy to do anywhere, even with Python"
    
    response = email_sender.send_email(from_email, to_email, subject, content)
    
    print(response.status_code)
    print(response.body)
    print(response.headers)
