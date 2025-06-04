from fastapi import APIRouter

from app.api.v1.endpoints import github, status


api_router = APIRouter()

# Include the export router directly with empty dependencies to bypass auth
api_router.include_router(
    status.router,
    prefix="/status",
    tags=["Status"],
    dependencies=[],  # Empty dependencies list to bypass auth
)

api_router.include_router(
    github.router,
    prefix="",
    tags=["Github"],
)
