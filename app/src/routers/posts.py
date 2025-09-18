from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    UploadFile,
    File,
    Form,
    Request,
)
from app.src.crud import Post, User
from app.src.schemas.post import PostUpdate, PostOut
from app.src.routers.auth import require_auth
from pathlib import Path
from uuid import uuid4


router = APIRouter(prefix='/posts', tags=['posts'])


@router.get('/', response_model=list[PostOut])
async def list_posts(_: str = Depends(require_auth)) -> list[PostOut]:
    items = await Post.filter(checked=True).order_by('-created_at')
    return [PostOut.model_validate(p) for p in items]


@router.get('/unchecked', response_model=list[PostOut])
async def list_unchecked_posts(
    _: str = Depends(require_auth)
) -> list[PostOut]:
    items = await Post.filter(checked=False).order_by('-created_at')
    return [PostOut.model_validate(p) for p in items]


@router.post('/', response_model=PostOut, status_code=201)
async def create_post(
    request: Request,
    user_id: int = Form(...),
    file: UploadFile = File(...),
    checked: bool = Form(False),
    _: str = Depends(require_auth),
) -> PostOut:
    user = await User.get_or_none(id=user_id)
    if not user:
        raise HTTPException(status_code=400, detail='invalid_user')
    media_root = Path(__file__).resolve().parents[3] / 'media'
    media_root.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or '').suffix or '.jpg'
    name = f'{uuid4().hex}{suffix}'
    save_path = media_root / name
    content = await file.read()
    save_path.write_bytes(content)
    base = str(request.base_url).rstrip('/')
    public_url = f'{base}/media/{name}'
    post = await Post.create(
        user_id=user.id,
        photo_url=public_url,
        checked=checked,
    )
    return PostOut.model_validate(post)


@router.get('/{post_id}', response_model=PostOut)
async def get_post(post_id: int, _: str = Depends(require_auth)) -> PostOut:
    post = await Post.get_or_none(id=post_id)
    if not post:
        raise HTTPException(status_code=404, detail='not_found')
    return PostOut.model_validate(post)


@router.put('/{post_id}', response_model=PostOut)
async def update_post(
    post_id: int, payload: PostUpdate, _: str = Depends(require_auth)
) -> PostOut:
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
