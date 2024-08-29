import os
import sys
import asyncio
import httpx
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
import time

base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
parent_dir = os.path.dirname(base_dir)

# file paths
#script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
env_file_path = os.path.join(base_dir, '.env')

class AsyncSendGridEmailSender:
    def __init__(self):
        # Load environment variables from the .env file
        load_dotenv(env_file_path)
        # Retrieve the SendGrid API key from environment variables
        self.api_key = os.environ.get('SENDGRID_API_KEY')
        # SendGrid base URL
        self.base_url = "https://api.sendgrid.com/v3/mail/send"
        # HTTP headers for SendGrid API
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def send_email(self, from_email, to_email, subject, content):
        # Create the email components
        mail = Mail(
            from_email=Email(from_email),
            to_emails=To(to_email),
            subject=subject,
            plain_text_content=Content("text/plain", content)
        )
        
        # Send the email asynchronously using httpx
        async with httpx.AsyncClient() as client:
            response = await client.post(self.base_url, headers=self.headers, json=mail.get())
            return response

    async def send_emails_in_round_robin(self, from_emails, to_emails, subject, content):
        tasks = []
        for i, to_email in enumerate(to_emails):
            from_email = from_emails[i % len(from_emails)]  # Round-robin selection
            task = self.send_email(from_email, to_email, subject, content)
            tasks.append(task)
        
        # Gather and run all tasks asynchronously
        responses = await asyncio.gather(*tasks)
        for response in responses:
            print(response.status_code)
            if response.status_code == 202:
                print("Email accepted for processing.")
            else:
                # Safely print the response content without assuming it's JSON
                try:
                    print(response.json())
                except ValueError:
                    print(response.text)

# Usage example
if __name__ == "__main__":
    email_sender = AsyncSendGridEmailSender()
    
    from_emails = ["ivmv2007@gmail.com", "mykhailoivanov97@gmail.com"]
    to_emails = ["ivmv@ukr.net", "ivmv@meta.ua", "elenaivanova758@gmail.com"]
    subject = "Sending with SendGrid is Fun"
    content = "And easy to do anywhere, even with Python!"
    
    # Start timing the execution
    start_time = time.perf_counter()
    
    # Run the async email sending
    asyncio.run(email_sender.send_emails_in_round_robin(from_emails, to_emails, subject, content))
    
    # End timing the execution
    end_time = time.perf_counter()
    
    # Calculate the total time taken
    total_time = end_time - start_time
    print(f"Total time taken to send emails: {total_time:.2f} seconds")
