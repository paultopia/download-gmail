import email 
import imaplib 
import os
import itertools
n = None 
def get_inbox():
    global n
    n = imaplib.IMAP4_SSL("imap.gmail.com")
    n.login('ADDRESS','PASSWORD')
    n.select("inbox")
    result, data = n.search(None, "ALL")
    ids = data[0] # data is a list.
    return ids.split()

def get_all_emails(inbox):
    return [n.fetch(x, "(RFC822)")[1] for x in inbox]

def parse_email(em):
    msg = em[0][1]
    emailstring = msg.decode('utf-8')
    return email.message_from_string(emailstring)

def parse_all_emails(emails):
    return [parse_email(x) for x in emails]

def list_sender(em):  # must be parsed
    return email.utils.parseaddr(em['From'])

inbox = parse_all_emails(get_all_emails(get_inbox()))

df = os.getcwd() + "/downloads"
def save_attachment(msg, download_folder=df):
    """
    Given a message, save its attachments to the specified
    download folder (default is /tmp) 
    
    return: file path to attachment
        """
    att_path = "No attachment found."
    for part in msg.walk():
        if part.get_content_maintype() == 'multipart':
            continue
        if part.get('Content-Disposition') is None:
            continue

        filename = part.get_filename()
        att_path = os.path.join(download_folder, filename)

        if not os.path.isfile(att_path):
            fp = open(att_path, 'wb')
            fp.write(part.get_payload(decode=True))
            fp.close()
    return att_path

def dl_all_atts(parsed_inbox):
    for x in parsed_inbox:
        save_attachment(x)

# works: dl_all_atts(inbox) 

def get_all_payloads(em):
    maintype = em.get_content_maintype()
    if maintype == 'multipart':
        payload = []
        for part in em.get_payload():
            # This includes mail body AND text file attachments.
            if part.get_content_maintype() == 'text':
                payload.append(part.get_payload())
        # No text at all. This is also happens
        return payload
    elif maintype == 'text':
        return em.get_payload()
    else:
        return ""

payloads = [get_all_payloads(x) for x in inbox]

def flatten(nested_list):
    return list(itertools.chain.from_iterable(nested_list))

# so basically I can detect real text content as opposed to BS text content in multipart messages by seeing if they have a space in them?

texts = filter(lambda x: " " in x, flatten(payloads))
stexts = list(texts)

import uuid 
tf = os.getcwd() + "/texts"
for x in stexts:
    filename = str(uuid.uuid4()) + ".html"
    path = os.path.join(tf, filename)
    with open(path, "w") as f:
        f.write(x)

# also works.

# need to write some simple functions to parse everything & c and then I can just 
# cron this and get text from html with bs4.