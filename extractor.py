import os
import email
import re
from datetime import datetime
from imaplib import IMAP4, IMAP4_SSL
from bs4 import BeautifulSoup

import config

# Connect to the server
if config.IMAP_SSL:
    mailbox = IMAP4_SSL(host=config.IMAP_HOST, port=config.IMAP_PORT)
else:
    mailbox = IMAP4(host=config.IMAP_HOST, port=config.IMAP_PORT)

# Log in and select the configured folder
mailbox.login(config.IMAP_USERNAME, config.IMAP_PASSWORD)
mailbox.select(config.FOLDER)

# Search for matching emails
status, messages = mailbox.search(None, '(FROM {})'.format(config.FROM_EMAIL))
if status == "OK":
    # Convert the result list to an array of message IDs
    messages = messages[0].split()

    if len(messages) < 1:
        # No matching messages, stop
        print("No matching messages found, nothing to do.")
        exit()

    # For each matching email...
    for msg_id in messages:

        # Fetch it from the server
        status, data = mailbox.fetch(msg_id, '(RFC822)')
        if status == "OK":
            # Convert it to an Email object
            msg = email.message_from_bytes(data[0][1])

            # Get the HTML body payload
            msg_html = msg.get_payload(1).get_payload(decode=True)

            # Parse the message
            msg_parsed = BeautifulSoup(msg_html, 'html.parser')

            # Find the code
            code = msg_parsed.select('span[class*="claim-code"] > span')[0].contents[1]

            # Print out the details to the console
            print(code)
        else:
            print("ERROR: Unable to fetch message {}, skipping.".format(msg_id.decode('UTF-8')))


else:
    print("FATAL ERROR: Unable to fetch list of messages from server.")
    exit(1)
