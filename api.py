import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from numbers_core import ProfileInput, analyze_profile as analyze_profile_ai, build_profile
from numbers_core.intelligence.openrouter_client import OpenRouterClient

load_dotenv()

app = FastAPI()


class ProfileRequest(BaseModel):
    full_name: str
    birthdate: str


def _make_input(payload: ProfileRequest) -> ProfileInput:
    return ProfileInput(name=payload.full_name, birthdate=payload.birthdate)


def _select_ai_client():
    api_key = os.getenv("OPENROUTER_API_KEY")
    return OpenRouterClient(api_key=api_key) if api_key else None


@app.post("/profile")
def create_profile(payload: ProfileRequest):
    try:
        profile = build_profile(_make_input(payload))
    except Exception as exc:  # pragma: no cover
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return profile


@app.post("/profile/analysis")
def create_profile_with_analysis(payload: ProfileRequest):
    try:
        profile = build_profile(_make_input(payload))
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        client = _select_ai_client()
        analysis = analyze_profile_ai(profile, ai=client).get("text", "Анализ временно недоступен.")
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return {"profile": profile, "analysis": analysis}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8001)
