from fastapi import APIRouter, Depends

from backend.app.core.security import require_authenticated_user

router = APIRouter(prefix="/packets", tags=["packets"], dependencies=[Depends(require_authenticated_user)])
