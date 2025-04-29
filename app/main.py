import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import os

from app.routes.newsletters import router as newsletter_router
from app.services.database_service import init_db
from app.config import APP_HOST, APP_PORT, APP_DEBUG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Newsletter Viewer Service",
    description="Service for viewing newsletter content",
    version="1.0.0"
)

app.include_router(newsletter_router)

@app.exception_handler(404)
async def not_found_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=404,
        content={"message": "The requested resource was not found"}
    )

@app.exception_handler(500)
async def server_error_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

@app.get("/", response_class=HTMLResponse)
async def root():
    return """
    <html>
        <head>
            <title>Newsletter Viewer Service</title>
        </head>
        <body>
            <h1>Newsletter Viewer Service</h1>
            <p>Service is up and running!</p>
            <p>Use the /newsletters/{newsletter_id}?email={email} endpoint to view newsletters.</p>
        </body>
    </html>
    """

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Startup event
@app.on_event("startup")
async def startup_event():
    logger.info("Starting Newsletter Viewer Service")

    # Initialize database
    init_db()

    logger.info("Newsletter Viewer Service started successfully")

def main():
    uvicorn.run(
        "app.main:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=APP_DEBUG
    )

if __name__ == "__main__":
    main()
