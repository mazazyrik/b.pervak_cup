from fastapi import APIRouter, Depends, HTTPException
from app.src.crud import Team
from app.src.schemas.team import TeamCreate, TeamUpdate, TeamOut
from app.src.routers.auth import require_auth


router = APIRouter(prefix='/teams', tags=['teams'])


@router.get('/', response_model=list[TeamOut])
async def list_teams(
    _: str = Depends(require_auth),
) -> list[TeamOut]:
    items = await Team.all()
    return [TeamOut.model_validate(t) for t in items]


@router.post('/', response_model=TeamOut, status_code=201)
async def create_team(
    payload: TeamCreate,
    _: str = Depends(require_auth),
) -> TeamOut:
    team = await Team.create(name=payload.name)
    return TeamOut.model_validate(team)


@router.get('/{team_id}', response_model=TeamOut)
async def get_team(team_id: int, _: str = Depends(require_auth)) -> TeamOut:
    team = await Team.get_or_none(id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail='not_found')
    return TeamOut.model_validate(team)


@router.put('/{team_id}', response_model=TeamOut)
async def update_team(
    team_id: int,
    payload: TeamUpdate,
    _: str = Depends(require_auth),
) -> TeamOut:
    team = await Team.get_or_none(id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail='not_found')
    update_data = payload.model_dump(exclude_unset=True)
    if update_data:
        await Team.filter(id=team_id).update(**update_data)
        team = await Team.get(id=team_id)
    return TeamOut.model_validate(team)


@router.delete('/{team_id}', status_code=204)
async def delete_team(team_id: int, _: str = Depends(require_auth)) -> None:
    deleted = await Team.filter(id=team_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail='not_found')
    return None
