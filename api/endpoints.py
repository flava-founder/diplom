from fastapi import APIRouter
from pydantic import BaseModel

from api.gpt import analyze_message


class DetectRequest(BaseModel):
    text: str


class DetectResponse(BaseModel):
    leak_detected: bool
    leak_volume: str | None
    leak_object: str | None
    company: str | None
    details: str | None



router = APIRouter()


@router.post('/detect')
async def detect(form: DetectRequest):
    return analyze_message(form.text)
