from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from starlette.middleware.sessions import SessionMiddleware
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from tortoise import connections
from app.src.routers.auth import router as auth_router
from app.src.routers.teams import router as teams_router
from app.src.routers.users import router as users_router
from app.src.routers.matches import router as matches_router
from app.src.routers.posts import router as posts_router
from app.src.routers.bets import router as bets_router


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
app.include_router(bets_router)

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


@app.on_event('startup')
async def migrate_match_result_nullable():
    conn = connections.get('default')
    info = await conn.execute_query_dict('PRAGMA table_info("match")')
    result_col = next((c for c in info if c.get('name') == 'result'), None)
    if result_col and result_col.get('notnull') == 1:
        await conn.execute_script('PRAGMA foreign_keys=OFF;')
        ddl_row = await conn.execute_query_dict(
            'SELECT sql FROM sqlite_master '
            'WHERE type="table" AND name="match"'
        )
        create_sql = ddl_row[0]['sql'] if ddl_row else None
        if create_sql:
            import re as _re
            new_sql = create_sql.replace(
                'CREATE TABLE "match"',
                'CREATE TABLE "match_new"'
            )
            new_sql = _re.sub(
                r'"result"\s+[^,\)]*NOT NULL',
                '"result" TEXT',
                new_sql
            )
            await conn.execute_query(new_sql)
            await conn.execute_query(
                (
                    'INSERT INTO "match_new" '
                    '(id, team1_id, team2_id, stage_name, date, result) '
                    'SELECT id, team1_id, team2_id, stage_name, date, '
                    'NULLIF(result, \"Null\") FROM "match"'
                )
            )
            await conn.execute_query('DROP TABLE "match"')
            await conn.execute_query(
                'ALTER TABLE "match_new" RENAME TO "match"'
            )
        # Drop leftover match_old if it exists from previous runs
        await conn.execute_query(
            'DROP TABLE IF EXISTS "match_old"'
        )
        # Rebuild bet table if it references match_old
        bet_row = await conn.execute_query_dict(
            'SELECT sql FROM sqlite_master '
            'WHERE type="table" AND name="bet"'
        )
        bet_sql = bet_row[0]['sql'] if bet_row else None
        if bet_sql and 'REFERENCES "match_old"' in bet_sql:
            bet_new_sql = bet_sql.replace(
                'CREATE TABLE "bet"',
                'CREATE TABLE "bet_new"'
            ).replace('REFERENCES "match_old"', 'REFERENCES "match"')
            await conn.execute_query(bet_new_sql)
            await conn.execute_query(
                (
                    'INSERT INTO "bet_new" '
                    '(id, user_id, match_id, result) '
                    'SELECT id, user_id, match_id, result FROM "bet"'
                )
            )
            await conn.execute_query('DROP TABLE "bet"')
            await conn.execute_query(
                'ALTER TABLE "bet_new" RENAME TO "bet"'
            )
        await conn.execute_script('PRAGMA foreign_keys=ON;')
