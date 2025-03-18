from fastapi import FastAPI, HTTPException, Depends, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
import random
import string
from datetime import datetime
from fastapi.responses import HTMLResponse

from database import SessionLocal, create_tables, URL

app = FastAPI()

create_tables()

@app.get("/", response_class=HTMLResponse)
def home():
    return """
    <html>
        <head><title>FastAPI URL Shortener</title></head>
        <body>
            <h1>Welcome to the FastAPI URL Shortener</h1>
            <p><a href="/docs">Click here to access the API documentation</a></p>
        </body>
    </html>
    """

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

class URLRequest(BaseModel):
    url: str

def generate_short_code(db: Session, length=6):
    while True:
        short_code = ''.join(random.choices(string.ascii_letters + string.digits, k=length))
        if not db.query(URL).filter(URL.short_code == short_code).first():
            return short_code

@app.post("/shorten", status_code=status.HTTP_201_CREATED)
def shorten_url(request: URLRequest, db: Session = Depends(get_db)):
    short_code = generate_short_code(db)
    new_url = URL(url=request.url, short_code=short_code)
    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return {
        "id": new_url.id,
        "url": new_url.url,
        "shortCode": new_url.short_code,
        "createdAt": new_url.created_at,
        "updatedAt": new_url.updated_at
    }

@app.get("/shorten/{short_code}")
def get_original_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Not Found")

    return {
        "id": url_entry.id,
        "url": url_entry.url,
        "shortCode": url_entry.short_code,
        "createdAt": url_entry.created_at,
        "updatedAt": url_entry.updated_at
    }

@app.put("/shorten/{short_code}")
def update_short_url(short_code: str, request: URLRequest, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Not Found")

    url_entry.url = request.url
    url_entry.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(url_entry)

    return {
        "id": url_entry.id,
        "url": url_entry.url,
        "shortCode": url_entry.short_code,
        "createdAt": url_entry.created_at,
        "updatedAt": url_entry.updated_at
    }

@app.delete("/shorten/{short_code}", status_code=status.HTTP_204_NO_CONTENT)
def delete_shortened_url(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Not Found")

    db.delete(url_entry)
    db.commit()
    return

@app.get("/shorten/{short_code}/stats")
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    url_entry = db.query(URL).filter(URL.short_code == short_code).first()
    if not url_entry:
        raise HTTPException(status_code=404, detail="Not Found")

    return {
        "id": url_entry.id,
        "url": url_entry.url,
        "shortCode": url_entry.short_code,
        "createdAt": url_entry.created_at,
        "updatedAt": url_entry.updated_at
    }