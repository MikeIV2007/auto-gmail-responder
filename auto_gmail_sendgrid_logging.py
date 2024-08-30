import os
import sys
import openai
import imaplib
import email
from time import sleep
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import csv
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
import logging  # Import the logging module

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    format='%(asctime)s - %(levelname)s - %(message)s',  # Customize the log message format
    handlers=[
        logging.FileHandler("email_autoresponder.log",  mode="w"),  # Log to a file with mode "w"(rewrite)
        logging.StreamHandler(sys.stdout)  # Also log to the console
    ]
)

class EmailAutoResponder:
    def __init__(self):
        # Get base directory
        self.base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
        self.env_file_path = os.path.join(self.base_dir, '.env')
        self.prompt_settings_file_path = os.path.join(self.base_dir, 'prompt_settings.csv')
        
        # Load environment variables
        load_dotenv(self.env_file_path)
        
        # Configurations
        self.openai_secret_key = os.getenv('openai_secret_key')
        self.gmail_address = os.getenv('gmail_address')
        self.gmail_app_password = os.getenv('gmail_app_password')
        self.gpt_auto_replied = 'gpt-auto-replied'
        self.check_every_n_seconds = int(os.getenv('check_every_n_seconds', 300))  # Default to 5 minutes if not set
        self.how_many_days_ago = int(os.getenv('how_many_days_ago', 0))  # Default to check today's emails only
        
        # Load prompt settings from CSV
        self.prompt_settings = self.load_prompt_settings()
        
        # SendGrid setup
        self.sendgrid_api_key = os.getenv('SENDGRID_API_KEY')
        self.sg = sendgrid.SendGridAPIClient(api_key=self.sendgrid_api_key)
        
        # List of sender emails for round-robin
        self.from_emails = ["mykhailoivanov97@gmail.com", "ivmv2007@gmail.com"]
        self.current_sender_index = 0

        logging.info('57, Initiating chatgpt gmail script...')
        self.check_minutes = round(self.check_every_n_seconds / 60, 1)
        logging.info('59, Init is done.')

    def load_prompt_settings(self):
        prompt_settings = []
        with open(self.prompt_settings_file_path) as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                prompt_settings.append(row)
        logging.debug(f'67,Loaded prompt settings: {prompt_settings}/n')
        return prompt_settings

    def get_next_sender_email(self):
        email = self.from_emails[self.current_sender_index]
        self.current_sender_index = (self.current_sender_index + 1) % len(self.from_emails)
        logging.debug(f'72 ,Next sender email for sendgrid: {email}')
        return email

    def send_gmail(self, receiver_address, mail_subject, mail_content):
        sender_address = self.get_next_sender_email()
        
        message = Mail(
            from_email=Email(sender_address),
            to_emails=To(receiver_address),
            subject=f"Re: {mail_subject}",
            plain_text_content=Content("text/plain", mail_content)
        )
        
        try:
            response = self.sg.send(message)
            logging.info(f"88, Sent email to {receiver_address} with subject: {mail_subject}. Response: {response.status_code}")
        except Exception as e:
            logging.error(f"90, Error sending email via SendGrid: {e}")

    def check_emails(self):
        while True:
            try:
                logging.info(f'95 Checking inbox every {self.check_minutes} minutes...')
                
                gmail_host = "imap.gmail.com"
                mail = imaplib.IMAP4_SSL(gmail_host)
                mail.login(self.gmail_address, self.gmail_app_password)
                mail.select("INBOX")

                current_date = datetime.now()
                date_since = current_date - timedelta(self.how_many_days_ago)
                date_str = date_since.strftime("%d-%b-%Y")

                for row in self.prompt_settings[1:]:  # Skip header row
                    self.process_prompt(row, mail, date_str)

                mail.logout()
                sleep(self.check_every_n_seconds)
            except Exception as e:
                logging.error(f"112, An error occurred: {e}")
                input("Please exit the window and restart the program...")
                break

    def process_prompt(self, row, mail, date_str):
        search_data = self.perform_search(row, mail, date_str)
        if search_data and len(search_data[0].split()) > 0:
            self.handle_search_results(row, mail, search_data)

    def perform_search(self, row, mail, date_str):
        search_data = None
        if row[0] == '1':
            _, search_data = mail.search(None, f'(SINCE "{date_str}" FROM "{row[1].strip()}")')
        elif row[0] == '2':
            _, search_data = mail.search(None, f'(SINCE "{date_str}" SUBJECT "{row[1].strip()}")')
        elif row[0] == '3':
            email_filter = row[1].split(';')[0].strip()
            subject_filter = ';'.join(row[1].split(';')[1:]).strip()
            _, search_data = mail.search(None, f'(SINCE "{date_str}" FROM "{email_filter}" SUBJECT "{subject_filter}")')
        logging.debug(f'130 Search data: {search_data}')
        return search_data

    def handle_search_results(self, row, mail, search_data):
        for num in search_data[0].split():
            typ, response_data = mail.fetch(num, '(RFC822)')
            if isinstance(response_data[0], tuple):
                msg = email.message_from_bytes(response_data[0][1])
                body = self.get_email_body(response_data)
                if body:
                    message_to_send = self.get_chatgpt_response(row, body)
                    if message_to_send:
                        self.send_response_email(msg, message_to_send, mail, num)
        logging.info(f"144, Search resalts hendeled.")

    def get_email_body(self, response_data):
        try:
            soup = BeautifulSoup(response_data[0][1].decode(), "html.parser")
            return soup.find('div').text
        except Exception as e:
            logging.warning(f"Error parsing email body: {e}")
            pass

        msg = email.message_from_bytes(response_data[0][1])
        if msg.is_multipart():
            for part in msg.walk():
                ctype = part.get_content_type()
                cdispo = str(part.get('Content-Disposition'))
                if ctype == 'text/plain' and 'attachment' not in cdispo:
                    logging.info("160, message is multipart")
                    return part.get_payload(decode=True)
                
        else:
            logging.info("160, message is not multipart")
            return msg.get_payload(decode=True)
        return None

    def get_chatgpt_response(self, row, body):
        try:
            openai.api_key = self.openai_secret_key
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": row[2] + body}
                ],
                temperature=0.9,
                max_tokens=1024,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0.6
            )
            logging.info('183, Generated response from ChatGPT')
            return response['choices'][0]['message']['content']
        except openai.OpenAIError as e:
            logging.error(f"186, OpenAI error: {e}")
        except Exception as e:
            logging.error(f"188, Unexpected error: {e}")
        return None

    def send_response_email(self, msg, message_to_send, mail, num):
        subject = msg['subject']
        from_email = msg['From'].split('<')[-1].split('>')[0]
        try:
            self.send_gmail(from_email, subject, message_to_send)
            self.move_email_to_folder(mail, num, self.gpt_auto_replied)
            logging.debug(f"197, response email sent to", mail)
        except Exception as e:
            logging.error(f"199, Error sending response: {e}")

    def move_email_to_folder(self, mail, num, folder_name):
        try:
            result, data = mail.fetch(num, '(UID)')
            uid = data[0].decode().split('(UID ')[1].split(')')[0]
            result = mail.uid('COPY', uid.encode(), folder_name)
            if result[0] == 'OK':
                mail.uid('STORE', uid.encode(), '+FLAGS', r'(\Deleted)')
                mail
        except Exception as e:
            # print(f"Error moving email: {e}")
            logging.error(f"211, Error moving email: {e}")

if __name__ == "__main__":
    responder = EmailAutoResponder()
    responder.check_emails()
