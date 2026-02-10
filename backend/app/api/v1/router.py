"""
CogniSense — Aggregated v1 API Router.

Collects all endpoint routers under the /api/v1 prefix.
"""

from fastapi import APIRouter

from app.api.v1.capture import router as capture_router
from app.api.v1.load import router as load_router
from app.api.v1.interview import router as interview_router
from app.api.v1.exam import router as exam_router

api_v1_router = APIRouter()

api_v1_router.include_router(capture_router, prefix="/capture", tags=["Capture"])
api_v1_router.include_router(load_router, prefix="/load", tags=["Cognitive Load"])
api_v1_router.include_router(interview_router, prefix="/interview", tags=["Interview"])
api_v1_router.include_router(exam_router, prefix="/exam", tags=["Exam"])
