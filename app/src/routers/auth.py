from typing import Optional
from fastapi import APIRouter, HTTPException, Request, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.src.schemas.auth import TokenIn, TokenOut


router = APIRouter(prefix='/auth', tags=['auth'])
bearer_scheme = HTTPBearer(auto_error=False)


def require_auth(
    request: Request,
    creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
) -> str:
    token = request.session.get('token')
    if not token and creds and creds.scheme.lower() == 'bearer':
        token = creds.credentials
    if not token:
        raise HTTPException(status_code=401, detail='unauthorized')
    return token


@router.post('/login', response_model=TokenOut)
async def login(data: TokenIn, request: Request) -> TokenOut:
    token = data.telegram_id
    request.session['token'] = token
    request.session['telegram_id'] = data.telegram_id
    return TokenOut(token=token)


@router.post('/logout')
async def logout(request: Request) -> dict:
    request.session.pop('token', None)
    request.session.pop('telegram_id', None)
    return {'ok': True}
