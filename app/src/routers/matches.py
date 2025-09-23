from fastapi import APIRouter, Depends, HTTPException
from app.src.crud import Match, Team, Bet, User
from app.src.schemas.match import MatchCreate, MatchUpdate, MatchOut
from app.src.routers.auth import require_auth
from app.src.producer import logger, send_message_to_kafka


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


@router.get('/user/{telegram_id}', response_model=list[MatchOut])
async def get_user_fav_team_matches(
    telegram_id: int,
    _: str = Depends(require_auth),
) -> list[MatchOut]:
    user = await User.get_or_none(telegram_id=telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail='not_found')
    matches = await Match.filter(team1_id=user.fav_team_id)
    matches2 = await Match.filter(team2_id=user.fav_team_id)
    return [MatchOut.model_validate(m) for m in matches + matches2]


@router.get('/user/{telegram_id}/recent', response_model=list[MatchOut])
async def show_recent_matche_by_fav_team(
    telegram_id: int,
    _: str = Depends(require_auth),
) -> list[MatchOut]:
    user = await User.get_or_none(telegram_id=telegram_id)
    if not user:
        raise HTTPException(status_code=404, detail='not_found')
    left = await Match.filter(
        team1_id=user.fav_team_id,
        result__isnull=False,
    ).exclude(result='Null').order_by('-date')
    right = await Match.filter(
        team2_id=user.fav_team_id,
        result__isnull=False,
    ).exclude(result='Null').order_by('-date')
    matches = list(left) + list(right)
    matches.sort(key=lambda m: m.date, reverse=True)
    matches_list = [MatchOut.model_validate(m) for m in matches[:2]]
    return matches_list


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

    new_result = update_data.get('result') if 'result' in update_data else None
    if 'result' in update_data:
        logger.info(f'Updating match {match_id} with result {new_result}')
        bets = await Bet.filter(match_id=match_id)
        team1 = await Team.get(id=match.team1_id)
        team2 = await Team.get(id=match.team2_id)
        for bet in bets:
            logger.info(f'Checking bet {bet.id} for match {match_id}')
            if new_result is not None and bet.result == new_result:
                user = await User.get(id=bet.user_id)
                res = (
                    f'{user.name} угадал результат матча '
                    f'{team1.name} {new_result} {team2.name}'
                )
                package = {
                    'tg_id': user.telegram_id,
                    'res': res,
                }
                logger.info(f'Sending message to Kafka: {package}')
                await send_message_to_kafka(package, 'push')

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
