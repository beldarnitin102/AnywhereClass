
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(
    title="AI Moodle Operator",
    version="0.1.0",
    description="An AI-powered platform for safely executing approved tasks.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE"],
    allow_headers=["Content-Type", "Authorization"],
)


@app.get("/")
def root():
    return {"message": "AI Moodle Operator API is running"}


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy",
        "application": "AI Moodle Operator",
        "phase": "platform-foundation",
    }
