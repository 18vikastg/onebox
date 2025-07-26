import imaplib, csv, sys, os
from email import message_from_bytes
from email.header import decode_header
from datetime import datetime
import re
from dotenv import load_dotenv

load_dotenv()

# Usage: python get_messages.py "<subject>" <total> <from_date> <to_date> <output_csv>
subject = sys.argv[1]
total = int(sys.argv[2])
from_date = datetime.strptime(sys.argv[3], "%Y-%m-%d").strftime("%d-%b-%Y")
to_date = datetime.strptime(sys.argv[4], "%Y-%m-%d").strftime("%d-%b-%Y")
output_csv = sys.argv[5]

# Configure login
M = imaplib.IMAP4_SSL("imap.gmail.com")
# Use environment variables for credentials
M.login(os.getenv("GMAIL_PRIMARY_EMAIL"), os.getenv("GMAIL_PRIMARY_PASSWORD"))
M.select("INBOX")

# Search Gmail inbox within date range and subject
criteria = f'(SINCE "{from_date}" BEFORE "{to_date}" SUBJECT "{subject}")'
status, data = M.search(None, criteria)
ids = data[0].split()[:total]

# Fetch and decode messages
rows = [["UID", "Subject", "From", "Date"]]
for uid in ids:
    status, msg_data = M.fetch(uid, "(RFC822)")
    msg = message_from_bytes(msg_data[0][1])
    hdr = msg["Subject"]
    if hdr:
        subject_decoded = decode_header(hdr)[0][0]
        if isinstance(subject_decoded, bytes):
            subject_decoded = subject_decoded.decode('utf-8', errors='replace')
    else:
        subject_decoded = "No Subject"
    frm = msg.get("From")
    date = msg.get("Date")
    
    # Clean up the data to avoid CSV parsing issues
    uid_clean = uid.decode() if isinstance(uid, bytes) else str(uid)
    subject_clean = str(subject_decoded).replace('\n', ' ').replace('\r', ' ').strip()
    frm_clean = str(frm).replace('\n', ' ').replace('\r', ' ').strip() if frm else "Unknown"
    date_clean = str(date).replace('\n', ' ').replace('\r', ' ').strip() if date else "Unknown"
    
    rows.append([uid_clean, subject_clean, frm_clean, date_clean])

# Write CSV
with open(output_csv, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerows(rows)

# Print payload so Node.js can detect completion
print("DONE")
