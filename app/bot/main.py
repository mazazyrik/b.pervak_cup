import asyncio
import os
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional
import httpx
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.dispatcher.middlewares.base import BaseMiddleware

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
BOT_TOKEN = os.getenv(
    'BOT_TOKEN', '7988942895:AAGPt2AiY2jED_YiuOCWZz2QxMgyvaJuMZw')
MINI_APP_URL = os.getenv('MINI_APP_URL', 'https://example.com')
RANEPASPORT_CHANNEL = os.getenv('RANEPASPORT_CHANNEL', '@ranepasport')
BALBESCREW_CHANNEL = os.getenv('BALBESCREW_CHANNEL', '@balbescrew')
BDEV_CHANNEL = os.getenv('BDEV_CHANNEL', '@bdevbync')


def _normalize_channel(value: str) -> str:
    v = (value or '').strip()
    v = v.replace('https://t.me/', '')
    v = v.replace('http://t.me/', '')
    v = v.replace('t.me/', '')
    if v.startswith('@'):
        v = v[1:]
    return ('@' + v) if v else ''


def _channel_url(value: str) -> str:
    v = _normalize_channel(value)
    return 'https://t.me/' + v[1:] if v else 'https://t.me/'


class ApiClient:
    def __init__(self, base_url: str) -> None:
        self.base_url = base_url.rstrip('/')
        self._client = httpx.AsyncClient(base_url=self.base_url, timeout=15)

    async def close(self) -> None:
        await self._client.aclose()

    def _auth(self, token: str) -> Dict[str, str]:
        return {'Authorization': f'Bearer {token}'}

    async def list_teams(self, token: str) -> List[Dict[str, Any]]:
        r = await self._client.get('/teams/', headers=self._auth(token))
        r.raise_for_status()
        return r.json()

    async def list_users(self, token: str) -> List[Dict[str, Any]]:
        r = await self._client.get('/users/', headers=self._auth(token))
        r.raise_for_status()
        return r.json()

    async def create_user(
        self,
        token: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        r = await self._client.post(
            '/users/',
            headers=self._auth(token),
            json=payload,
        )
        r.raise_for_status()
        return r.json()

    async def update_user(
        self,
        token: str,
        user_id: int,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        r = await self._client.put(
            f'/users/{user_id}',
            headers=self._auth(token),
            json=payload,
        )
        r.raise_for_status()
        return r.json()


class StartCaptureMiddleware(BaseMiddleware):
    def __init__(self, api: ApiClient) -> None:
        super().__init__()
        self.api = api

    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message,
        data: Dict[str, Any],
    ) -> Any:
        if (
            isinstance(event, Message)
            and event.text
            and event.text.strip().startswith('/start')
        ):
            tg_id = str(event.from_user.id)
            token = tg_id
            username = event.from_user.username or ''
            full_name = (
                (event.from_user.full_name or '').strip()
                or username
                or tg_id
            )
            try:
                users = await self.api.list_users(token)
                existing = next(
                    (
                        u for u in users
                        if str(u.get('telegram_id')) == tg_id
                    ),
                    None,
                )
                if existing:
                    await self.api.update_user(
                        token,
                        existing['id'],
                        {
                            'username': username,
                            'name': full_name,
                        },
                    )
                else:
                    await self.api.create_user(
                        token,
                        {
                            'username': username,
                            'telegram_id': tg_id,
                            'name': full_name,
                            'fav_team_id': None,
                        },
                    )
            except Exception:
                pass
        return await handler(event, data)


class RanepasportSubscriptionMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[
            [Message | CallbackQuery, Dict[str, Any]],
            Awaitable[Any],
        ],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            if event.text and event.text.strip().startswith('/list'):
                return await handler(event, data)
            ok_rane = await self._is_subscribed(
                user_id,
                BDEV_CHANNEL,
            )
            if not ok_rane:
                await self._prompt_subscribe(event, prefer_edit=False)
                return
        if isinstance(event, CallbackQuery):
            if event.data and event.data.startswith('check_subs'):
                return await handler(event, data)
            user_id = event.from_user.id
            ok_rane = await self._is_subscribed(
                user_id,
                BDEV_CHANNEL,
            )
            if not ok_rane:
                await self._prompt_subscribe(event.message, prefer_edit=True)
                return
        return await handler(event, data)

    async def _is_subscribed(self, user_id: int, channel: str) -> bool:
        try:
            member = await self.bot.get_chat_member(
                chat_id=_normalize_channel(channel),
                user_id=user_id,
            )
            status = getattr(member, 'status', None)
            return status in ('member', 'administrator', 'creator')
        except Exception:
            return False

    async def _prompt_subscribe(self, message: Optional[Message], prefer_edit: bool) -> None:
        if not message:
            return
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Подписаться на @bdevbync',
                    url=_channel_url(BDEV_CHANNEL),
                )],
                [InlineKeyboardButton(
                    text='Проверить подписку',
                    callback_data='check_subs',
                )],
            ],
        )
        text = (
            'Чтобы пользоваться ботом, подпишись на каналы и '
            'нажми Проверить подписку'
        )
        if prefer_edit:
            try:
                await message.edit_text(text, reply_markup=kb)
                return
            except Exception:
                pass
        await message.answer(text, reply_markup=kb)


class BalbescrewSubscriptionMiddleware(BaseMiddleware):
    def __init__(self, bot: Bot) -> None:
        super().__init__()
        self.bot = bot

    async def __call__(
        self,
        handler: Callable[
            [Message | CallbackQuery, Dict[str, Any]],
            Awaitable[Any],
        ],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user_id = event.from_user.id
            if event.text and event.text.strip().startswith('/list'):
                return await handler(event, data)
            ok_balb = await self._is_subscribed(
                user_id,
                BDEV_CHANNEL,
            )
            if not ok_balb:
                await self._prompt_subscribe(event, prefer_edit=False)
                return
        if isinstance(event, CallbackQuery):
            if event.data and event.data.startswith('check_subs'):
                return await handler(event, data)
            user_id = event.from_user.id
            ok_balb = await self._is_subscribed(
                user_id,
                BDEV_CHANNEL,
            )
            if not ok_balb:
                await self._prompt_subscribe(event.message, prefer_edit=True)
                return
        return await handler(event, data)

    async def _is_subscribed(self, user_id: int, channel: str) -> bool:
        try:
            member = await self.bot.get_chat_member(
                chat_id=_normalize_channel(channel),
                user_id=user_id,
            )
            status = getattr(member, 'status', None)
            return status in ('member', 'administrator', 'creator')
        except Exception:
            return False

    async def _prompt_subscribe(self, message: Optional[Message], prefer_edit: bool) -> None:
        if not message:
            return
        kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='Подписаться на @bdevbync',
                    url=_channel_url(BDEV_CHANNEL),
                )],
                [InlineKeyboardButton(
                    text='Проверить подписку',
                    callback_data='check_subs',
                )],
            ],
        )
        text = 'Подпишись и нажми Проверить подписку'
        if prefer_edit:
            try:
                await message.edit_text(text, reply_markup=kb)
                return
            except Exception:
                pass
        await message.answer(text, reply_markup=kb)


router = Router()


@router.callback_query(F.data == 'check_subs')
async def cb_check_subs(cb: CallbackQuery) -> None:
    await cb.answer()
    bot = cb.message.bot
    uid = cb.from_user.id

    async def _is_sub(chan: str) -> bool:
        try:
            m = await bot.get_chat_member(
                chat_id=_normalize_channel(chan),
                user_id=uid,
            )
            s = getattr(m, 'status', None)
            return s in ('member', 'administrator', 'creator')
        except Exception:
            return False

    ok_r = await _is_sub(BDEV_CHANNEL)
    ok_b = True

    if ok_r and ok_b:
        try:
            await cb.message.edit_text('Подписки подтверждены, отправь /start')
        except Exception:
            await cb.message.answer('Подписки подтверждены, отправь /start')
        return

    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='Подписаться на @bdevbync',
                url=_channel_url(BDEV_CHANNEL),
            )],
            [InlineKeyboardButton(
                text='Проверить подписку',
                callback_data='check_subs',
            )],
        ],
    )
    try:
        await cb.message.edit_text(
            'Подписки не найдены. Подпишись и нажми Проверить подписку',
            reply_markup=kb,
        )
    except Exception:
        await cb.message.answer(
            'Подписки не найдены. Подпишись и нажми Проверить подписку',
            reply_markup=kb,
        )


@router.message(Command('start'))
async def cmd_start(message: Message, api: ApiClient) -> None:
    tg_id = str(message.from_user.id)
    token = tg_id
    try:
        teams = await api.list_teams(token)
    except Exception:
        await message.answer('Не удалось загрузить команды, попробуй позже')
        return
    if not teams:
        await message.answer('Список команд пуст')
        return
    rows: List[List[InlineKeyboardButton]] = []
    for team in teams:
        rows.append([
            InlineKeyboardButton(
                text=team.get('name', 'Команда'),
                callback_data='fav_team:' + str(team.get('id')),
            )
        ])
    kb = InlineKeyboardMarkup(inline_keyboard=rows)
    await message.answer('Выбери любимую команду', reply_markup=kb)


@router.callback_query(F.data.startswith('fav_team:'))
async def choose_team(cb: CallbackQuery, api: ApiClient) -> None:
    await cb.answer()
    tg_id = str(cb.from_user.id)
    token = tg_id
    team_id = int(cb.data.split(':', 1)[1])
    try:
        users = await api.list_users(token)
        me = next(
            (
                u for u in users
                if str(u.get('telegram_id')) == tg_id
            ),
            None,
        )
        if not me:
            username = cb.from_user.username or ''
            full_name = (
                (cb.from_user.full_name or '').strip()
                or username
                or tg_id
            )
            me = await api.create_user(
                token,
                {
                    'username': username,
                    'telegram_id': tg_id,
                    'name': full_name,
                    'fav_team_id': team_id,
                },
            )
        else:
            me = await api.update_user(
                token,
                me['id'],
                {'fav_team_id': team_id},
            )
    except Exception:
        await cb.message.answer('Не удалось сохранить выбор, попробуй позже')
        return
    launch_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='🚀 Запустить приложение',
                url=MINI_APP_URL,
            )],
            [InlineKeyboardButton(text='✨ Титры', callback_data='credits')],
        ],
    )
    await cb.message.answer('Регистрация завершена', reply_markup=launch_kb)


@router.callback_query(F.data == 'credits')
async def credits(cb: CallbackQuery) -> None:
    await cb.answer()
    text = (
        '✨ Бот разработан Никитой Чуваевым из б.студио\n'
        '🧪 б.студио: t.me/balbescrew\n'
        '👨‍💻 Сольный проект Никиты: @bdevbync\n'
        '🏫 ССК ЭМИТ: @ssk_emit\n'
        '🏆 ССК Сенатор РАНХиГС: https://t.me/ranepasport'
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='б.студио',
                url='https://t.me/balbescrew',
            )],
            [InlineKeyboardButton(
                text='@bdevbync',
                url='https://t.me/bdevbync',
            )],
            [InlineKeyboardButton(
                text='@ssk_emit',
                url='https://t.me/ssk_emit',
            )],
            [InlineKeyboardButton(
                text='ССК Сенатор РАНХиГС',
                url='https://t.me/ranepasport',
            )],
        ],
    )
    await cb.message.answer(text, reply_markup=kb)


@router.message(Command('list'))
async def cmd_list(message: Message, api: ApiClient) -> None:
    tg_id = str(message.from_user.id)
    token = tg_id
    try:
        users = await api.list_users(token)
    except Exception:
        await message.answer('Не удалось получить список')
        return
    usernames = []
    for u in users:
        uname = u.get('username') or ''
        if uname:
            if not uname.startswith('@'):
                uname = '@' + uname
            usernames.append(uname)
    if not usernames:
        await message.answer('Нет пользователей')
        return
    await message.answer('\n'.join(sorted(set(usernames))))


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError('BOT_TOKEN is required')
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    api = ApiClient(API_BASE_URL)
    dp.message.middleware(StartCaptureMiddleware(api))
    dp.message.middleware(RanepasportSubscriptionMiddleware(bot))
    dp.message.middleware(BalbescrewSubscriptionMiddleware(bot))
    dp.callback_query.middleware(RanepasportSubscriptionMiddleware(bot))
    dp.callback_query.middleware(BalbescrewSubscriptionMiddleware(bot))
    dp['api'] = api
    dp.include_router(router)

    async def api_injector(handler, event, data):
        data['api'] = api
        return await handler(event, data)
    dp.message.outer_middleware.register(api_injector)
    dp.callback_query.outer_middleware.register(api_injector)
    try:
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types(),
        )
    finally:
        await api.close()


if __name__ == '__main__':
    asyncio.run(main())
