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
    test_data = [row["phrase"].lower() for row in phrase_rows]

    # initalize variables
    score = 1 # defaults to medium suspicion
    notes = []
    body = email.get("body", {})
    message = body.get("text", "").replace("\n", " ").lower()

    # count phrases
    phrase_flags = 0 
    for phrase in test_data:
        phrase_flags += message.count(phrase)
    
    # any phrase raises suspicion, 3 instances gives cause it is likely
    return 2 if phrase_flags > 3 else 1 if phrase_flags > 1 else 0