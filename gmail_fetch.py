# gmail_fetch.py
import base64
import tempfile
import os
from typing import List
from googleapiclient.errors import HttpError
from gmail_oauth import get_gmail_service
from parser import parse_email   # your existing parser that accepts a file path

def fetch_recent_emails_as_json(max_messages: int = 20) -> List[dict]:
   
    service = get_gmail_service()
    parsed_emails = []

    try:
        # List message IDs from INBOX
        res = service.users().messages().list(userId="me", maxResults=max_messages, q="in:inbox").execute()
        messages = res.get("messages", []) or []
        if not messages:
            return []

        for m in messages:
            msg_id = m.get("id")
            try:
                msg = service.users().messages().get(userId="me", id=msg_id, format="raw").execute()
            except HttpError as e:
                # skip a single message if it fails
                print(f"Warning: failed to fetch message {msg_id}: {e}")
                continue

            raw_b64 = msg.get("raw")
            if not raw_b64:
                # If raw is missing, skip (you could fetch format='full' as fallback)
                print(f"Warning: message {msg_id} has no 'raw' field; skipping")
                continue

            try:
                raw_bytes = base64.urlsafe_b64decode(raw_b64.encode("utf-8"))
            except Exception as e:
                print(f"Warning: failed to base64-decode message {msg_id}: {e}")
                continue

            # write to temp file and parse
            tmp_path = None
            try:
                with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as tmp:
                    tmp.write(raw_bytes)
                    tmp_path = tmp.name

                parsed = parse_email(tmp_path)
                # add lightweight gmail metadata to help trace in UI/debug
                parsed["_gmail_message_id"] = msg_id
                parsed["_gmail_thread_id"] = msg.get("threadId")
                parsed_emails.append(parsed)

            except Exception as e:
                print(f"Warning: failed to parse message {msg_id}: {e}")
                # continue to next message

            finally:
                if tmp_path and os.path.exists(tmp_path):
                    try:
                        os.unlink(tmp_path)
                    except Exception:
                        pass

    except HttpError as e:
        raise RuntimeError(f"Gmail API error: {e}")

    return parsed_emails

if __name__ == "__main__":
    emails = fetch_recent_emails_as_json(10)
    print(f"Fetched {len(emails)} parsed emails")
