from fastapi import FastAPI

app = FastAPI(title="VeriBorder AI")


@app.get("/")
def home():
    return {
        "project": "VeriBorder AI",
        "status": "running",
        "problem_statement": "26188"
    }