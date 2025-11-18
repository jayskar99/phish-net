# app.py
from fastapi import FastAPI, UploadFile, File, HTTPException
import tempfile
import os
from parser import parse_email
from gmail_fetch import fetch_recent_emails_as_json

app = FastAPI(title="PhishNet Plugin Backend")

@app.post("/upload_eml")
async def upload_eml(file: UploadFile = File(...)):
    
    # Save file temporarily
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".eml") as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name

        # Parse -> JSON structured email
        email_json = parse_email(temp_file_path)
        return email_json

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse uploaded email: {e}")

    finally:
        # Clean up temp file if it exists
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception:
                pass

@app.get("/fetch_gmail")
async def fetch_gmail_endpoint(max_messages: int = 20):
    try:
        emails = fetch_recent_emails_as_json(max_messages)
        return {"count": len(emails), "emails": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    

@app.get("/")
async def root():
    return {"message": "PhishNet backend is running", "endpoints": ["/upload_eml", "/fetch_gmail"]}

<<<<<<< HEAD
=======
    # Parse → JSON structured email
    email_json = parse_email(temp_file_path)
    return email_json

>>>>>>> 0a0d8ca8e07d35b7aa0188780499b6566f119646
