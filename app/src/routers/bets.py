from fastapi import APIRouter, Depends, HTTPException
from app.src.crud import Bet, User, Match
from app.src.schemas.bet import BetCreate, BetUpdate, BetOut
from app.src.routers.auth import require_auth


router = APIRouter(prefix='/bets', tags=['bets'])


@router.get('/', response_model=list[BetOut])
async def list_bets(_: str = Depends(require_auth)) -> list[BetOut]:
    items = await Bet.all()
    return [BetOut.model_validate(b) for b in items]


@router.post('/', response_model=BetOut, status_code=201)
async def create_bet(
    payload: BetCreate, _: str = Depends(require_auth)
) -> BetOut:
    user = await User.get_or_none(id=payload.user_id)
    match = await Match.get_or_none(id=payload.match_id)
    if not user or not match:
        raise HTTPException(status_code=400, detail='invalid_relations')
    existing = await Bet.get_or_none(user_id=user.id, match_id=match.id)
    if existing:
        await Bet.filter(id=existing.id).update(result=payload.result)
        existing = await Bet.get(id=existing.id)
        return BetOut.model_validate(existing)
    bet = await Bet.create(
        user_id=user.id,
        match_id=match.id,
        result=payload.result,
    )
    return BetOut.model_validate(bet)


@router.get('/{bet_id}', response_model=BetOut)
async def get_bet(bet_id: int, _: str = Depends(require_auth)) -> BetOut:
    bet = await Bet.get_or_none(id=bet_id)
    if not bet:
        raise HTTPException(status_code=404, detail='not_found')
    return BetOut.model_validate(bet)


@router.put('/{bet_id}', response_model=BetOut)
async def update_bet(
    bet_id: int, payload: BetUpdate, _: str = Depends(require_auth)
) -> BetOut:
    bet = await Bet.get_or_none(id=bet_id)
    if not bet:
        raise HTTPException(status_code=404, detail='not_found')
    data = payload.model_dump(exclude_unset=True)
    if data:
        await Bet.filter(id=bet_id).update(**data)
        bet = await Bet.get(id=bet_id)
    return BetOut.model_validate(bet)


@router.delete('/{bet_id}', status_code=204)
async def delete_bet(bet_id: int, _: str = Depends(require_auth)) -> None:
    deleted = await Bet.filter(id=bet_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail='not_found')
    return None
