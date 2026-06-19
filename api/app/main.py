from fastapi import FastAPI

app = FastAPI(
    title="SecOpsAI API",
    version="1.0.0"
)

@app.get("/")
def root():
    return {"message": "SecOpsAI API is running"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}
