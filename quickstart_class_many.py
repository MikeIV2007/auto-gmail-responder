import os
import sendgrid
from sendgrid.helpers.mail import Email, To, Content, Mail
from dotenv import load_dotenv
import time


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


if __name__ == "__main__":
    email_sender = SendGridEmailSender()

    # List of sender email addresses
    from_emails = ["ivmv2007@gmail.com", "mykhailoivanov97@gmail.com"]
    
    # List of recipient email addresses
    to_emails = ["ivmv@ukr.net", "ivmv@meta.ua", "elenaivanova758@gmail.com"]

    # Email subject and content
    subject = "Sending with SendGrid is Fun"
    content = "And easy to do anywhere, even with Python"

    # Send emails using a round-robin approach
    sender_index = 0  # Start with the first sender
    start_time = time.perf_counter()

    for to_email in to_emails:
        # Select the sender email based on the current index
        from_email = from_emails[sender_index]

        # Send the email
        response = email_sender.send_email(from_email, to_email, subject, content)
        
        print(f"Sent email from {from_email} to {to_email}")
        print(response.status_code)
        print(response.body)
        print(response.headers)
        
        # Update the sender index to rotate through the senders
        sender_index = (sender_index + 1) % len(from_emails)

    # End timing the execution
    end_time = time.perf_counter()
    
    # Calculate the total time taken
    total_time = end_time - start_time
    print(f"Total time taken to send emails: {total_time:.2f} seconds")
