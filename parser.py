from mailparser import parse_from_file
from bs4 import BeautifulSoup
from urllib.parse import urlparse

def extract_links_from_html(html):
    soup = BeautifulSoup(html, "html.parser")
    links = []
    for tag in soup.find_all('a', href=True):
        url = tag['href']
        domain = urlparse(url).netloc
        links.append({
            "display_text": tag.get_text(strip=True),
            "url": url,
            "domain": domain
        })
    return links

def parse_email(file_path):
    mail = parse_from_file(file_path)

    body_text = mail.text_plain[0] if mail.text_plain else ""
    body_html = mail.text_html[0] if mail.text_html else ""
    links = extract_links_from_html(body_html)

    return {
        "message_id": mail.message_id,
        "from": {
            "name": mail.from_[0][0],
            "email": mail.from_[0][1]
        },
        "reply_to": {
            "name": mail.reply_to[0][0] if mail.reply_to else "",
            "email": mail.reply_to[0][1] if mail.reply_to else ""
        },
        "to": [email for _, email in mail.to],
        "subject": mail.subject,
        "date": str(mail.date),

        "headers": {
            "spf_pass": "pass" in (mail.spf if mail.spf else "").lower(),
            "dkim_pass": "pass" in (mail.dkim if mail.dkim else "").lower(),
            "dmarc_pass": "pass" in (mail.dmarc if mail.dmarc else "").lower(),
            "received_paths": mail.received
        },

        "body": {
            "text": body_text,
            "html": body_html
        },

        "links": links,

        "attachments": [
            {
                "filename": att["filename"],
                "filetype": att["mail_content_type"],
                "size_bytes": att["size"]
            } for att in mail.attachments
        ]
    }
