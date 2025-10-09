"""
API v1 aggregator: mounts all versioned routers.
"""
from fastapi import APIRouter

from backend.app.api.routes.attribution import router as attribution_router
from backend.app.api.routes.agent import router as agent_router

api_router = APIRouter()
api_router.include_router(attribution_router)
api_router.include_router(agent_router)
