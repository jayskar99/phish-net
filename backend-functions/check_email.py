# check the email
import sqlite3

def connect_db():
    conn = sqlite3.connect("phish.db")
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn

def check_email(email):
    """
    email: dict of email data
    returns: (score, notes)
      - score: int (0, 1, or 2) where higher means more suspicious
      - notes: any notes
    """
    conn = connect_db()
    cur = conn.cursor()
    
    # initalize variables
    sender_email = email.get("from").get("email").lower() # emails are not case sensitive
    sender_domain = sender_email.split("@")[1]
    score = 1 # defaults to medium suspicion
    notes = []

    # error case
    if not sender_email or "@" not in sender_email:
        notes.append("missing or malformed sender email")
        return (score, notes)

    # check domain
    cur.execute("SELECT reputation_score, notes FROM domains WHERE domain = ?", (sender_domain,))
    row = cur.fetchone()
    if row:
        score = int(row["reputation_score"])
        if row["notes"] != "":
            notes.append(row["notes"])

    # check email second because specific addresses should overwrite domains
    cur.execute("SELECT reputation_score, notes FROM emails WHERE email = ?", (sender_email,))
    row = cur.fetchone()
    if row:
        score = int(row["reputation_score"])
        if row["notes"] != "":
            notes.append(row["notes"])

    conn.close()
    return (score, notes)

''' add funtionality for checking one or two characters off of a known safe email 
consider using intersection, dict of transformations, etc. '''