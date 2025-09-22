from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.src.routers.auth import router as auth_router
from app.src.routers.users import router as users_router
from app.src.routers.teams import router as teams_router
from app.src.routers.matches import router as matches_router
from app.src.routers.bets import router as bets_router
from app.src.routers.posts import router as posts_router
from app.src.producer import start_kafka_producer, stop_kafka_producer


app = FastAPI(
    title='Pervak Cup API',
    description='API for Pervak Cup project',
    version='0.1.0',
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
)

app.add_middleware(SessionMiddleware, secret_key='Uh4S9eFb')
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(auth_router, prefix='/api')
app.include_router(teams_router, prefix='/api')
app.include_router(users_router, prefix='/api')
app.include_router(matches_router, prefix='/api')
app.include_router(posts_router, prefix='/api')
app.include_router(bets_router, prefix='/api')

_MEDIA_ROOT = Path(__file__).resolve().parents[2] / 'media'
_MEDIA_ROOT.mkdir(parents=True, exist_ok=True)
app.mount('/media', StaticFiles(directory=str(_MEDIA_ROOT)), name='media')

register_tortoise(
    app,
    db_url='postgres://user:password@db:5432/mydatabase',
    modules={'models': ['app.src.crud']},
    generate_schemas=True,
    add_exception_handlers=True,
)


@app.on_event('startup')
async def _on_startup():
    await start_kafka_producer()


@app.on_event('shutdown')
async def _on_shutdown():
    await stop_kafka_producer()


@app.get('/health')
async def health_check():
    return {'status': 'ok'}
