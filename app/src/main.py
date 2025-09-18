from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from app.src.routers.auth import router as auth_router
from app.src.routers.teams import router as teams_router
from app.src.routers.users import router as users_router
from app.src.routers.matches import router as matches_router
from app.src.routers.posts import router as posts_router


app = FastAPI(name='b.pervak_cup')
app.add_middleware(SessionMiddleware, secret_key='Uh4S9eFb')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router)
app.include_router(teams_router)
app.include_router(users_router)
app.include_router(matches_router)
app.include_router(posts_router)

_MEDIA_ROOT = Path(__file__).resolve().parents[2] / 'media'
_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount('/media', StaticFiles(directory=str(_MEDIA_ROOT)), name='media')

register_tortoise(
    app,
    db_url='sqlite://database.db',
    modules={'models': ['app.src.crud']},
    generate_schemas=True,
    add_exception_handlers=True,
)
