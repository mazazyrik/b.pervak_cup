from fastapi import APIRouter, Depends, HTTPException
from app.src.crud import User, Team
from app.src.schemas.user import UserCreate, UserUpdate, UserOut
from app.src.routers.auth import require_auth


router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', response_model=list[UserOut])
async def list_users(
    _: str = Depends(require_auth),
) -> list[UserOut]:
    items = await User.all()
    return [UserOut.model_validate(u) for u in items]


@router.post('/', response_model=UserOut, status_code=201)
async def create_user(
    payload: UserCreate,
    _: str = Depends(require_auth),
) -> UserOut:
    fav_team = None
    if payload.fav_team_id is not None:
        fav_team = await Team.get_or_none(id=payload.fav_team_id)
        if not fav_team:
            raise HTTPException(status_code=400, detail='invalid_fav_team')
    user = await User.create(
        username=payload.username,
        telegram_id=payload.telegram_id,
        name=payload.name,
        fav_team_id=fav_team.id if fav_team else None,
    )
    return UserOut.model_validate(user)


@router.get('/{user_id}', response_model=UserOut)
async def get_user(user_id: int, _: str = Depends(require_auth)) -> UserOut:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='not_found')
    return UserOut.model_validate(user)


@router.put('/{user_id}', response_model=UserOut)
async def update_user(
    user_id: int,
    payload: UserUpdate,
    _: str = Depends(require_auth),
) -> UserOut:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail='not_found')
    update_data = payload.model_dump(exclude_unset=True)
    if 'fav_team_id' in update_data and update_data['fav_team_id'] is not None:
        fav_team = await Team.get_or_none(id=update_data['fav_team_id'])
        if not fav_team:
            raise HTTPException(status_code=400, detail='invalid_fav_team')
    if update_data:
        await User.filter(id=user_id).update(**update_data)
        user = await User.get(id=user_id)
    return UserOut.model_validate(user)


@router.delete('/{user_id}', status_code=204)
async def delete_user(user_id: int, _: str = Depends(require_auth)) -> None:
    deleted = await User.filter(id=user_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail='not_found')
    return None
