import logging
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import GameServer
from app.schemas import ServerCreate, ServerResponse, ServerUpdate
from app.security import require_api_key

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/v1/servers", tags=["servers"])
DatabaseSession = Annotated[Session, Depends(get_db)]


def get_server_or_404(server_id: UUID, db: Session) -> GameServer:
    server = db.get(GameServer, str(server_id))
    if server is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Server not found")
    return server


@router.get("", response_model=list[ServerResponse])
def list_servers(db: DatabaseSession) -> list[GameServer]:
    return list(db.scalars(select(GameServer).order_by(GameServer.created_at)))


@router.post(
    "",
    response_model=ServerResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_api_key)],
)
def create_server(payload: ServerCreate, db: DatabaseSession) -> GameServer:
    server = GameServer(**payload.model_dump())
    db.add(server)
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        logger.warning(
            "Server creation rejected because name already exists",
            extra={"server_name": payload.name},
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Server name already exists"
        ) from exc
    db.refresh(server)
    logger.info("Server created", extra={"server_id": server.id, "server_name": server.name})
    return server


@router.get("/{server_id}", response_model=ServerResponse)
def get_server(server_id: UUID, db: DatabaseSession) -> GameServer:
    return get_server_or_404(server_id, db)


@router.patch(
    "/{server_id}",
    response_model=ServerResponse,
    dependencies=[Depends(require_api_key)],
)
def update_server(server_id: UUID, payload: ServerUpdate, db: DatabaseSession) -> GameServer:
    server = get_server_or_404(server_id, db)
    changes = payload.model_dump(exclude_none=True)
    if "players" in changes and changes["players"] > server.max_players:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="players must not exceed max_players",
        )
    for field, value in changes.items():
        setattr(server, field, value.value if hasattr(value, "value") else value)
    db.commit()
    db.refresh(server)
    logger.info(
        "Server status updated",
        extra={"server_id": server.id, "changed_fields": sorted(changes)},
    )
    return server


@router.delete(
    "/{server_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_api_key)],
)
def delete_server(server_id: UUID, db: DatabaseSession) -> Response:
    server = get_server_or_404(server_id, db)
    db.delete(server)
    db.commit()
    logger.info("Server deleted", extra={"server_id": str(server_id), "server_name": server.name})
    return Response(status_code=status.HTTP_204_NO_CONTENT)
