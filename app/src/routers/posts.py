from fastapi import APIRouter, Depends, HTTPException
from app.src.crud import Post, User
from app.src.schemas.post import PostCreate, PostUpdate, PostOut
from app.src.routers.auth import require_auth


router = APIRouter(prefix='/posts', tags=['posts'])


@router.get('/', response_model=list[PostOut])
async def list_posts(_: str = Depends(require_auth)) -> list[PostOut]:
    items = await Post.filter(checked=True).order_by('-created_at')
    return [PostOut.model_validate(p) for p in items]


@router.post('/', response_model=PostOut, status_code=201)
async def create_post(payload: PostCreate, _: str = Depends(require_auth)) -> PostOut:
    user = await User.get_or_none(id=payload.user_id)
    if not user:
        raise HTTPException(status_code=400, detail='invalid_user')
    post = await Post.create(
        user_id=user.id,
        photo_url=payload.photo_url,
        checked=payload.checked,
    )
    return PostOut.model_validate(post)


@router.get('/{post_id}', response_model=PostOut)
async def get_post(post_id: int, _: str = Depends(require_auth)) -> PostOut:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail='not_found')
    return PostOut.model_validate(post)


@router.put('/{post_id}', response_model=PostOut)
async def update_post(post_id: int, payload: PostUpdate, _: str = Depends(require_auth)) -> PostOut:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail='not_found')
    data = payload.model_dump(exclude_unset=True)
    if data:
        await Post.filter(id=post_id).update(**data)
        post = await Post.get(id=post_id)
    return PostOut.model_validate(post)


@router.delete('/{post_id}', status_code=204)
async def delete_post(post_id: int, _: str = Depends(require_auth)) -> None:
    deleted = await Post.filter(id=post_id).delete()
    if deleted == 0:
        raise HTTPException(status_code=404, detail='not_found')
    return None
