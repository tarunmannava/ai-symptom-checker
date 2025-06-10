from fastapi import FastAPI
import uvicorn
from symptoms import CORE_SYMPTOMS, CORE_CONDITIONS

app = FastAPI(title="AI Symptom Checker", version="1.0.0")

@app.get("/")
def read_root():
    return {"message": "AI Symptom Checker API is running!"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

@app.get("/symptoms")
def get_symptoms():
    return {"symptoms": CORE_SYMPTOMS}

@app.post("/analyze")
def analyze_symptoms(symptoms: list[str]):
    confidence = len(symptoms) * 10
    return {
        "symptoms": symptoms,
        "possible_conditions": CORE_CONDITIONS[:3],
        "confidence": min(confidence, 85)
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)