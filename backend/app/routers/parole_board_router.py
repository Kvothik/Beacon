from fastapi import APIRouter, Depends

from backend.app.core.security import require_authenticated_user

router = APIRouter(prefix="/parole-board-office", tags=["parole-board"], dependencies=[Depends(require_authenticated_user)])
