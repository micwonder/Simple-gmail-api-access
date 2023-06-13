import os
import base64
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.transport.requests import Request


import re

# Define the necessary scopes
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def get_latest_messages() -> str:
    # Load the client secret file downloaded from the Google API Console
    print ("Get Latest messages request")
    links = []
    try:
        credentials = None
        if os.path.exists('token.json'):
            credentials = Credentials.from_authorized_user_file('token.json', SCOPES)

        # If there are no (valid) credentials available, let the user log in.
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
                credentials = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open('token.json', 'w') as token:
                token.write(credentials.to_json())

        # Create a Gmail service object
        service = build('gmail', 'v1', credentials=credentials)

        # Get the latest messages
        results = service.users().messages().list(userId='me', labelIds=['INBOX'], maxResults=3).execute()
        messages = results.get('messages', [])

        if not messages:
            print('No messages found')
        else:
            print('Latest Messages:')
            for message in messages:
                msg = service.users().messages().get(userId='me', id=message['id']).execute()
                msg_data = msg['payload']['headers']
                is_matching_message = False
                for values in msg_data:
                    name = values['name']
                    if name == 'Subject' and 'Verify your email address' in values['value']:
                        is_matching_message = True
                        break
                    # if name == 'From':
                    #     sender = values['value']
                    # elif name == 'Subject':
                    #     subject = values['value']
                if not is_matching_message:
                    continue
                snippet = msg['snippet']
                # print (snippet)
                
                msg_payload = msg['payload']
                parts = msg_payload['parts']
                link = None
                for part in parts:
                    if part['mimeType'] == 'text/html':
                        data = part['body']['data']
                        decoded_data = base64.urlsafe_b64decode(data).decode('utf-8')
                        link_match = re.search(r'https://~~~~~~~~put_any_string_here~~~~~~~~~~/\w+\?\w+\=\w+', decoded_data)
                        # link_match = re.search(r'(https://www.upwork.com/nx/signup/verify-email/\w+)', decoded_data)
                        if link_match:
                            link = link_match.group(0)
                            break

                if link:
                    # sender = msg['payload']['headers'][20]['value']
                    # subject = msg['payload']['headers'][15]['value']
                    # print(f'From: {sender}')
                    # print(f'Subject: {subject}')
                    links.append({
                        "recipient": msg['payload']['headers'][0]['value'],
                        "link": link,
                    })
                    return links

                # print (msg.items())
                # print(f'From: {sender}')
                # print(f'Subject: {subject}')
                # print(f'Snippet: {snippet}')
                print('---------------------------------------------------')
    except Exception as e:
        print ("Something went wrong, try yourself")
        print (e.args[0])
    print ("Get Latest messages request")
    return links

# Call the function to retrieve the latest messages
if __name__ == '__main__':
    links = get_latest_messages()
    print(f'Link: {links}')