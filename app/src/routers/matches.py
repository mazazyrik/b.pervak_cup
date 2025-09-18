from fastapi import APIRouter, Depends, HTTPException
from app.src.crud import Match, Team, Bet
from app.src.schemas.match import MatchCreate, MatchUpdate, MatchOut
from app.src.routers.auth import require_auth


router = APIRouter(prefix='/matches', tags=['matches'])


@router.get('/', response_model=list[MatchOut])
async def list_matches(
    _: str = Depends(require_auth),
) -> list[MatchOut]:
    items = await Match.all()
    return [MatchOut.model_validate(m) for m in items]


@router.post('/', response_model=MatchOut, status_code=201)
async def create_match(
    payload: MatchCreate,
    _: str = Depends(require_auth),
) -> MatchOut:
    t1 = await Team.get_or_none(id=payload.team1_id)
    t2 = await Team.get_or_none(id=payload.team2_id)
    if not t1 or not t2:
        raise HTTPException(status_code=400, detail='invalid_team')
    match = await Match.create(
        team1_id=t1.id,
        team2_id=t2.id,
        date=payload.date,
        result=payload.result,
        stage_name=payload.stage_name,
    )
    return MatchOut.model_validate(match)


@router.get('/{match_id}', response_model=MatchOut)
async def get_match(match_id: int, _: str = Depends(require_auth)) -> MatchOut:
    match = await Match.get_or_none(id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail='not_found')
    return MatchOut.model_validate(match)


@router.put('/{match_id}', response_model=MatchOut)
async def update_match(
    match_id: int,
    payload: MatchUpdate,
    _: str = Depends(require_auth),
) -> MatchOut:
    match = await Match.get_or_none(id=match_id)
    if not match:
        raise HTTPException(status_code=404, detail='not_found')
    update_data = payload.model_dump(exclude_unset=True)
    if 'team1_id' in update_data:
        t1 = await Team.get_or_none(id=update_data['team1_id'])
        if not t1:
            raise HTTPException(status_code=400, detail='invalid_team1')
        update_data['team1_id'] = t1.id
    if 'team2_id' in update_data:
        t2 = await Team.get_or_none(id=update_data['team2_id'])
        if not t2:
            raise HTTPException(status_code=400, detail='invalid_team2')
        update_data['team2_id'] = t2.id

    if 'stage_name' in update_data:
        update_data['stage_name'] = update_data['stage_name']
        update_data.pop('stage_name', None)

    if 'result' in update_data:
        update_data['result'] = update_data['result']
        update_data.pop('result', None)
        bets = await Bet.filter(match_id=match_id)
        for bet in bets:
            if bet.result == update_data['result']:
                pass  # кидаем пуш в бота

    if update_data:
        await Match.filter(id=match_id).update(**update_data)
        match = await Match.get(id=match_id)
    return MatchOut.model_validate(match)


@router.delete('/{match_id}', status_code=204)
async def delete_match(match_id: int, _: str = Depends(require_auth)) -> None:
    deleted = await Match.filter(id=match_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail='not_found')
    return None
