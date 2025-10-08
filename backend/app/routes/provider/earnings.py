from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_db
from app.dependencies import get_current_user
from app.services.provider_service import calculate_provider_total_earnings


class EarningsResponse(BaseModel):
    total_earnings: float
    currency: str = "USD"  # TBD: make configurable when integrating payments


provider_earnings_router = APIRouter(prefix="/provider/earnings", tags=["provider-earnings"])


@provider_earnings_router.get("/total", response_model=EarningsResponse)
async def get_total_earnings(
    *,
    db: AsyncSession = Depends(get_db),
    current_user_id: int = Depends(get_current_user),
):
    try:
        total = await calculate_provider_total_earnings(db, provider_id=current_user_id)
    except Exception as e:
        # Generic fallback; adjust error handling if needed
        raise HTTPException(status_code=500, detail=str(e))
    return EarningsResponse(total_earnings=total)
