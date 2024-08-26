# -*- coding: utf-8 -*-
"""
@author: Underground AI | https://undergroundai.substack.com/

"""
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


################################################################################
################################# OPTIONS ######################################


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

################################################################################
################################################################################



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



prompt_settings = []

# Open the CSV file
with open(prompt_settings_file_path) as csvfile:
    # Create a CSV reader object
    reader = csv.reader(csvfile)

    # Iterate over each row in the CSV file
    for row in reader:
        prompt_settings.append(row)

print('initiating chatgpt gmail script...')

check_minutes = round(int(check_every_n_seconds) / 60,1)


try:

    while True:
        
        gmail_host = "imap.gmail.com"
        mail = imaplib.IMAP4_SSL(gmail_host)
        mail.login(gmail_address, gmail_app_password)
        mail.select("INBOX")
    
        print('checking inbox every ' + str(check_minutes) + ' minutes...' )
        
        current_date = datetime.now()
        date_since = current_date - timedelta(int(how_many_days_ago))
        # format dates to DD-Mon-YYYY
        date_str = date_since.strftime("%d-%b-%Y")
    
        first_row = True
    
        for row in prompt_settings:
            
            if first_row == True:
                first_row = False
                continue
            
            search_data = None
            
            if row[0] == '1':
                result, search_data = mail.search( None, '(SINCE "' + date_str + '" FROM "' + row[1].strip() + '")')
            elif row[0] == '2':
                result, search_data = mail.search( None, '(SINCE "' + date_str + '" SUBJECT "' + row[1].strip() + '")')
            elif row[0] == '3':

                email_filter = row[1].split(';')[0].strip()
                section = row[1].split(';')

                if len(section) == 2:
                    subject_filter = section[1].strip()
                elif len(section) > 2:
                    subject_filter = ' '.join(section[1:]).strip()
                else:
                    raise Exception('There is an issue with a filter_type 3 values. Please check to see if you have the correct format. Remember to split the email address and subject value with the ; symbol')

                    
                result, search_data = mail.search( None, '(SINCE "' + date_str + '" FROM "' + email_filter + '" SUBJECT "' + subject_filter + '")')
            print(139,result)
            print (140, search_data)

            if len(search_data[0].split()) > 0 :
                
    
                if row[0] == '1':
                    print('found email for filter : ' +  '(SINCE "' + date_str + '" FROM "' + row[1].strip()+ '")')
                elif row[0] == '2':
                    print('found email for filter : ' +  '(SINCE "' + date_str + '" SUBJECT "' + row[1].strip() + '")')
                elif row[0] == '3':
                    print('found email for filter : ' +   '(SINCE "' + date_str + '" FROM "' + email_filter + '" SUBJECT "' + subject_filter + '")')
    
                        
                for num in search_data[0].split():
                    
                    typ, response_data = mail.fetch(num, '(RFC822)')
    
                    #print(157, response_data[0])
    
                    if isinstance(response_data[0], tuple):
                        print (160, response_data[0])
    
                        msg = email.message_from_bytes(response_data[0][1])
                        subject = msg['subject']
                        from_email = msg['From'].split('<')[len(msg['From'].split('<'))-1].split('>')[0]
    
                        #== body parser
                        body = None
                        # text/html
                        try:
                            soup = BeautifulSoup(response_data[0][1].decode(), "html.parser")
                            body = soup.find('div').text
                            print (172,body)
                        except:
                            body = None
    
                        if body == None:
                            print (177,"I am hear")
                            if msg.is_multipart():
                                print(179, 'I ma here')
                                for part in msg.walk():
                                    print (181, "I am here")
                                    ctype = part.get_content_type()
                                    cdispo = str(part.get('Content-Disposition'))
    
                                # skip any text/plain (txt) attachments
                                if ctype == 'text/plain' and 'attachment' not in cdispo:
                                    print(187, 'I am here')
                                    body = part.get_payload(decode=True)  # decode
    
    
                            # not multipart - i.e. plain text, no attachments, keeping fingers crossed
                            else:
                                print(193, "I am here")
                                body = msg.get_payload(decode=True)
                                print(191,"i am here")
    
                        if body == None:
                            print (198, "I am here")
                            continue
    
                        # openai.api_key = openai_secret_key
                        # response = openai.Completion.create(
                        #     engine="text-davinci-003", 
                        #     prompt= row[2] + body,
                        #     temperature=0.9,
                        #     max_tokens=1024,
                        #     top_p=1,
                        #     frequency_penalty=0,
                        #     presence_penalty=0.6,
                        #     n=1,
                        # )
    
                        # message_to_send = response['choices'][0]['text']

                        # openai.api_key = openai_secret_key
                        # response = openai.ChatCompletion.create(
                        #     model="gpt-3.5-turbo",
                        #     messages=[
                        #         {"role": "system", "content": "You are a helpful assistant."},
                        #         {"role": "user", "content": row[2] + body}
                        #     ],
                        #     temperature=0.9,
                        #     max_tokens=1024,
                        #     top_p=1,
                        #     frequency_penalty=0,
                        #     presence_penalty=0.6,
                        #     )
                        

                        # message_to_send = response['choices'][0]['message']['content']

                        try:
                            openai.api_key = openai_secret_key
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

                            #message_to_send = response['choices'][0]['message']['content']
                            message_to_send = "it is my hand made message"

                            print(message_to_send)

                        except openai.APIConnectionError as e:
                            print(f"Connection error: {e}")
                        except openai.APITimeoutError as e:
                            print(f"Request timed out: {e}")
                        except openai.AuthenticationError as e:
                            print(f"Authentication error: {e}")
                        except openai.BadRequestError as e:
                            print(f"Bad request error: {e}")
                        except openai.ConflictError as e:
                            print(f"Conflict error: {e}")
                        except openai.InternalServerError as e:
                            print(f"Internal server error: {e}")
                        except openai.NotFoundError as e:
                            print(f"Resource not found: {e}")
                        except openai.PermissionDeniedError as e:
                            print(f"Permission denied: {e}")
                        except openai.RateLimitError as e:
                            print(f"Rate limit exceeded: {e}")
                        except openai.UnprocessableEntityError as e:
                            print(f"Unprocessable entity: {e}")
                        except Exception as e:
                            print(f"An unexpected error occurred: {e}")

                            
                        try:
        
                            result, data = mail.fetch(num, '(UID)')
                            # uid = data[0].decode().split(' ')[2]
                            uid = data[0].decode().split('(UID ')[1].split(')')[0]
                            # print(f"Message number {num.decode()} has UID {uid}")
                            
                            result = mail.uid('COPY', uid.encode(), gpt_auto_replied)
                            if result[0] == 'OK':
                                # mark the message for deletion
                               # mov, data = mail.uid('STORE', uid.encode() , '+FLAGS', '(\Deleted)')
                                mov, data = mail.uid('STORE', uid.encode() , '+FLAGS', r'(\Deleted)')
                                #mov, data = mail.uid('STORE', uid.encode() , '+FLAGS', '(\\Deleted)')
                                # permanently remove mails that are marked for deletion
                                mail.expunge()
                                
                                print('this email has been moved to the gpt-auto-replied inbox')
    
                        except Exception as e:
                            print(e)
                        
                        
    
                        #send email
                        try:
                            send_gmail(gmail_address, from_email, subject, message_to_send)
                            # print('sending email')
                        except Exception as e:
                            print(e)
    
    
        mail.logout()
        sleep(int(check_every_n_seconds))
        
except Exception as e:
    print(e)
    input("An error has occured, please exit the window and restart the program...")

finally:
    
    try:
        mail.logout()
    except:
        pass

# if __name__ == "__main__":
#     send_gmail(
#         sender_address=gmail_address,
#         receiver_address= 'ivmv@ukr.net',
#         mail_subject='Test Subject',
#         mail_content='This is a last test email.',
#     ) 