from fastapi import FastAPI, UploadFile, File
import tempfile
from parser import parse_email

app = FastAPI()

@app.post("/upload_eml")
async def upload_eml(file: UploadFile = File(...)):
    # Save file temporarily
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        content = await file.read()
        temp_file.write(content)
        temp_file_path = temp_file.name

    # Parse → JSON structured email
    email_json = parse_email(temp_file_path)
    return email_json
