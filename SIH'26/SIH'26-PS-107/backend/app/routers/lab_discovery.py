# backend/app/routers/lab_discovery.py
"""Router for Lab Discovery."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from ..schemas.lab_discovery import LabSearchRequest, LabSearchResponse
from ..services.lab_discovery import search_laboratories

try:
    from ..database import get_db
except ImportError:
    async def get_db():
        yield None

router = APIRouter(prefix="/api/labs/discovery", tags=["Lab Discovery"])
logger = logging.getLogger(__name__)

@router.post("/search", response_model=LabSearchResponse)
async def search_labs_api(
    request: LabSearchRequest,
    db: AsyncSession = Depends(get_db)
):
    """Search for verified BIS testing laboratories."""
    results = await search_laboratories(db, request)
    return LabSearchResponse(results=results)
