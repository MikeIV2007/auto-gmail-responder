# import smtplib
# from email.mime.multipart import MIMEMultipart
# from email.mime.text import MIMEText

# def send_email(subject, body, to_email, from_email, smtp_server, smtp_port, smtp_user, smtp_password):
#     try:
#         # Create the email message
#         msg = MIMEMultipart()
#         msg['From'] = from_email
#         msg['To'] = to_email
#         msg['Subject'] = subject
#         msg.attach(MIMEText(body, 'plain'))

#         # Connect to the SMTP server
#         with smtplib.SMTP(smtp_server, smtp_port) as server:
#             server.starttls()  # Upgrade the connection to secure
#             server.login(smtp_user, smtp_password)  # Log in to the server
#             server.send_message(msg)  # Send the email

#         print('Email sent successfully.')

#     except Exception as e:
#         print(f'Failed to send email: {e}')

# # Example usage
# send_email(
#     subject='Test Subject',
#     body='This is a test email.',
#     to_email='ivmv@ukr.net',
#     from_email='mykhailoivanov97@gmail.com',
#     smtp_server='smtp.gmail.com',
#     smtp_port=587,
#     smtp_user='mykhailoivanov97@gmail.com',
#     smtp_password='acecvgwdyvvsvqav'
# )

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

# This gets the directory where the script (or bundled executable) is located
# base_dir = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))


base_dir = os.path.dirname(sys.executable if getattr(sys, 'frozen', False) else __file__)
parent_dir = os.path.dirname(base_dir)





# file paths
#script_dir = os.path.dirname(os.path.realpath(sys.argv[0]))
env_file_path = os.path.join(base_dir, 'settings.env')
load_dotenv(env_file_path)
prompt_settings_file_path = os.path.join(base_dir, 'prompt_settings.csv')

openai_secret_key = os.getenv('openai_secret_key')
gmail_address = os.getenv('gmail_address')
gmail_app_password = os.getenv('gmail_app_password')
gpt_auto_replied = 'gpt-auto-replied'
check_every_n_seconds = os.getenv('check_every_n_seconds')
    # default is set to 5 minutes ie 300 seconds. The shorter the check time, the more intensive this application will run

how_many_days_ago = os.getenv('how_many_days_ago')
    # If set to 0, this application will only respond to emails sent today. (default)
    # if set to 1, it will check yesterdays email as well.
    # if set to 2, it will check up to 2 days ago and so on. 

def send_gmail(sender_address, receiver_address, mail_subject, mail_content):
    
    message = MIMEMultipart()
    message['From'] = sender_address
    message['To'] = receiver_address
    message['Subject'] = f"Re: {mail_subject}"
    message.attach(MIMEText(mail_content, 'plain'))

    session = smtplib.SMTP('smtp.gmail.com', 587)
    session.starttls()
    session.login(sender_address, gmail_app_password)

    text = message.as_string()

    session.sendmail(sender_address, receiver_address, text)
    session.quit()
    print("Sent email to " + receiver_address, "with subject: " + mail_subject)

send_gmail(
    sender_address=gmail_address,
    receiver_address= 'ivmv@ukr.net',
    mail_subject='Test Subject',
    mail_content='This is a last test email.',
)
