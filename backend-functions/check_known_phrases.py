# check known phrases
import json
import sqlite3

# local data for testing purposes (incomplete)
# test_data = ['prize', 'prizes', 'action required', 'your account will be', 'final notice', 'warning', 'payment details', 'click', 'selected', 'winner', 'urgent', 'secure download']

# database connection
def connect_db():
    conn = sqlite3.connect("phish.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def check_known_phrases(email):
    """
    email: dict of email data
    returns: (score, notes)
      - score: int (0, 1, or 2) where higher means more suspicious
      - notes: any notes
    """
    conn = connect_db()
    cur = conn.cursor()

    # load from db
    cur.execute("SELECT phrase, notes FROM suspicious_phrases")
    phrase_rows = cur.fetchall()

    # initalize variables
    score = 0 # defaults to low suspicion
    notes = []
    body = email.get("body", {})
    message = body.get("text", "").replace("\n", " ").lower()

    # count phrases
    phrase_flags = 0 
    for row in phrase_rows:
        phrase = row["phrase"].lower()
        db_note = row["notes"]

        count = message.count(phrase)
        if count > 0:
            phrase_flags += count

            # build note text
            if db_note:
                notes.append(f"matched phrase '{phrase}' ({db_note}) x{count}")
            else:
                notes.append(f"matched phrase '{phrase}' x{count}")
    
    # any phrase raises suspicion, 3 instances gives cause it is likely
    score = 2 if phrase_flags > 3 else 1 if phrase_flags > 1 else 0

    conn.close()
    return (score, notes)