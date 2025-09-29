from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from backend.api.print_media_routes import router as print_media_router

# Initialize FastAPI app
app = FastAPI(
    title="Multi-Channel Sentiment Analysis",
    description="API for analyzing sentiment across various channels including social media, print media, calls, and emails",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(print_media_router)

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "Multi-Channel Sentiment Analysis API",
        "status": "active",
        "version": "1.0.0"
    }

# Health check endpoint
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "services": {
            "social_media": "ready",
            "print_media": "ready",
            "call_records": "ready",
            "email_processor": "ready"
        }
    }

if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)