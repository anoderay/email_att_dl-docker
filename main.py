# script for downloading email-attachments via IMAP and deleting the processed emails afterwards - created to consume files with paperless via sent emails. Tested on Python3.10
from imap_tools import MailBox, OR, NOT
import logging
import os
import config #load config file

# Logging Setup
logging.basicConfig(filename="/log/att_dl.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)


host = config.host 
user =  config.user 
secret = config.secret 

out_dir = "/output/"
msg_processed = []
msg_unknown = []
trusted_senders = "adress@one.com", "adress@two.com", "adress@three.com"", 

# connecting to host
try:
    logging.info("connecting to %s",host)
    mailbox = MailBox(host).login(user, secret)
except:
    logging.error("Could not connect to host %s with user %s, check credentials or connection", host, user)
    exit(1)

# getting messages from trusted senders
for msg in mailbox.fetch(OR(from_=trusted_senders)):
    logging.info("processing email with uid '%s' and title '%s' from '%s'", msg.uid, msg.subject, msg.from_)
    att_count = len(msg.attachments)    #count attachments to decide how to proceed
    att_index = 1
    msg_title = ''.join(e for e in msg.subject if e.isalnum() or e.isspace()) # sanitize msg title for later use
    for att in msg.attachments:
        att_name, att_ext = os.path.splitext(att.filename)
        if att_count == 1:
            with open(out_dir + "/" + msg_title + att_ext, 'wb') as f: 
                f.write(att.payload)
                logging.debug("saved file '"+ msg_title + att_ext + "'")
        elif att_count > 1:
            with open(out_dir + "/" + msg_title + " "+ str(att_index) + att_ext, 'wb') as f: 
                f.write(att.payload)
                att_index = att_index + 1
                logging.debug("saved file '"+ msg_title + " " + str(att_index) + att_ext + "'")
        elif att_count == 0:
            logging.debug("email with uid '%s' from '%s' with title '%s' did not include an attachment", msg.uid, msg.from_, msg.subject)
    msg_processed.append(msg.uid) #collect the processed emails

#delete processed emails
if len(msg_processed) != 0:
    mailbox.delete(msg_processed) #deleting the processed emails
    logging.info("processed and deleted messages with UIDs "+", ".join(msg_processed))
else:
    logging.info("no messages from trusted senders found")

#deleting messages from non trusted senders
for msg in mailbox.fetch(NOT(OR(from_=trusted_senders))):
    logging.info("email with uid '%s' and title '%s' from '%s' was not in the list of trusted senders and will be deleted", msg.uid, msg.subject, msg.from_)
    msg_unknown.append(msg.uid)
if len(msg_unknown) != 0:
    mailbox.delete(msg_unknown) #deleting the processed emails
