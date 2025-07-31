from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, validator
from url_scraper import intelligent_scrape
import uvicorn
from urllib.parse import urlparse

app = FastAPI(title="URL Analyzer API", version="1.0.0")

class URLRequest(BaseModel):
    url: str
    
    @validator('url')
    def validate_url(cls, v):
        if not v or not v.strip():
            raise ValueError('URL cannot be empty')
        
        # Add http:// if no scheme
        if not v.startswith(('http://', 'https://')):
            v = 'https://' + v
            
        # Basic URL validation
        try:
            parsed = urlparse(v)
            if not parsed.netloc:
                raise ValueError('Invalid URL format')
        except Exception:
            raise ValueError('Invalid URL format')
            
        return v

@app.post("/analyze")
async def analyze_url(request: URLRequest):
    try:
        result = intelligent_scrape(request.url)
        return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
async def root():
    return {"message": "URL Analyzer API", "docs": "/docs"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)