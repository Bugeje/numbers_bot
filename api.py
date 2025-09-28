from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from numbers_core.calc.profile import calculate_core_profile

app = FastAPI()


class ProfileRequest(BaseModel):
    full_name: str
    birthdate: str


@app.post("/profile")
def create_profile(payload: ProfileRequest):
    try:
        profile = calculate_core_profile(payload.full_name, payload.birthdate)
    except Exception as exc:  # pragma: no cover - safety net for invalid input
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    try:
        return {
            "life_path": profile["life_path"],
            "birthday": profile["birthday"],
            "expression": profile["expression"],
            "soul": profile["soul"],
            "personality": profile["personality"],
        }
    except (TypeError, KeyError) as exc:
        raise HTTPException(status_code=500, detail="Invalid profile structure") from exc


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
