from fastapi import APIRouter, Query, Header, Request, HTTPException, status, Depends
from typing import List, Optional
from src.database.functions import verify_token
from src.utils.logging_helpers import build_route_log_string
from src.app.repositories.highscore import (
    PlayerHiscoreData as RepositoryPlayerHiscoreData,
)
from src.app.repositories.highscore_latest import (
    PlayerHiscoreDataLatest as RepositoryPlayerHiscoreDataLatest,
)
from src.app.schemas.highscore import PlayerHiscoreData as SchemaPlayerHiscoreData

router = APIRouter(tags=["Hiscore"])


async def verify_and_log_token(request: Request, token: str):
    """
    Verifies the token and logs the route.
    Raises HTTP 403 if the token verification fails.
    """
    try:
        await verify_token(
            token,
            verification="verify_ban",
            route=build_route_log_string(request),
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail=f"Token verification failed: {str(e)}"
        )


@router.get("/hiscore", response_model=List[SchemaPlayerHiscoreData])
async def get_highscore_data(
    request: Request,
    token: str = Header(...),
    player_name: str = Query(..., max_length=13, description="Player name to filter by."),
    page: int = Query(default=1, ge=1, description="Page number."),
    page_size: int = Query(default=10, ge=1, le=1000, description="Number of records per page."),
    _=Depends(verify_and_log_token),
):
    """
    Fetch highscore data for a specific player.
    """
    repo = RepositoryPlayerHiscoreData()
    data = await repo.read(player_name=player_name, page=page, page_size=page_size)
    return data


@router.get("/hiscore/latest", response_model=List[SchemaPlayerHiscoreData])
async def get_highscore_data_latest(
    request: Request,
    token: str = Header(...),
    gte_player_id: int = Query(
        ge=0, description="Player ID greater than or equal to this value."
    ),
    page: Optional[int] = Query(default=None, ge=1, description="Page number."),
    page_size: int = Query(default=1000, ge=1, description="Number of records per page."),
    _=Depends(verify_and_log_token),
):
    """
    Fetch the latest highscore data filtered by Player ID.
    """
    repo = RepositoryPlayerHiscoreDataLatest()
    data = await repo.read(gte_player_id=gte_player_id, page=page, page_size=page_size)
    return data


@router.post("/hiscore", status_code=status.HTTP_201_CREATED)
async def post_highscore_data(
    request: Request,
    data: List[SchemaPlayerHiscoreData],
    token: str = Header(...),
    _=Depends(verify_and_log_token),
):
    """
    Post highscore data for multiple players.
    """
    repo = RepositoryPlayerHiscoreData()
    await repo.create(data=data)
    return {"message": "Highscore data created successfully."}
