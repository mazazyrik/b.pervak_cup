import asyncio
import os
import logging
from typing import Any, Awaitable, Callable, Dict, List, Optional
import httpx
import json
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    WebAppInfo,
)
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from client import KafkaClient
from config import KAFKA_BOOTSTRAP_SERVERS

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

API_BASE_URL = os.getenv('API_BASE_URL', 'http://127.0.0.1:8000')
BOT_TOKEN = os.getenv(
    'BOT_TOKEN', '7988942895:AAGPt2AiY2jED_YiuOCWZz2QxMgyvaJuMZw')
MINI_APP_URL = 'https://b-pervak.3utilities.com/'
RANEPASPORT_CHANNEL = os.getenv('RANEPASPORT_CHANNEL', '@ranepasport')
BALBESCREW_CHANNEL = os.getenv('BALBESCREW_CHANNEL', '@balbescrew')
BDEV_CHANNEL = os.getenv('BDEV_CHANNEL', '@bdevbync')

# User Agreement Constants
USER_AGREEMENT_TEXT = """Пользовательское соглашение
Используя бота Кубок Первокурсников, вы соглашаетесь, что мы собираем ваш Telegram ID и имя профиля.
По вашему желанию вы можете загружать фото/материалы — они могут быть опубликованы в ленте и использованы для освещения Кубка.
Данные хранятся на сервере и не передаются третьим лицам, кроме случаев, предусмотренных законом.
Вы можете прекратить использование бота и запросить удаление данных в любой момент. Контакт администратора @mazazyrikbeats
"""
AGREE_CALLBACK_DATA = 'user_agreement_agree'
DISAGREE_CALLBACK_DATA = 'user_agreement_disagree'


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


@router.callback_query(F.data == DISAGREE_CALLBACK_DATA)
async def cb_disagree_agreement(cb: CallbackQuery) -> None:
    await cb.answer()
    await cb.message.edit_text(
        'Для перезапуска бота напишите /start. Чтобы использовать бота, необходимо принять пользовательское соглашение.'
    )


@router.callback_query(F.data == AGREE_CALLBACK_DATA)
async def cb_agree_agreement(cb: CallbackQuery, api: ApiClient) -> None:
    await cb.answer()
    tg_id = str(cb.from_user.id)
    token = tg_id
    try:
        users = await api.list_users(token)
        me = next((u for u in users if str(
            u.get('telegram_id')) == tg_id), None)
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
                    'fav_team_id': None,
                },
            )
        launch_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='🚀 Запустить приложение',
                    web_app=WebAppInfo(url=MINI_APP_URL),
                )],
                [InlineKeyboardButton(
                    text='✨ Титры', callback_data='credits')],
            ],
        )
        await cb.message.edit_text('Вы согласились с пользовательским соглашением. Готово, можно запускать приложение', reply_markup=launch_kb)

    except Exception:
        await cb.message.edit_text('Не удалось обработать согласие, попробуй позже')


@router.message(Command('start'))
async def cmd_start(message: Message, api: ApiClient) -> None:
    tg_id = str(message.from_user.id)
    token = tg_id
    try:
        users = await api.list_users(token)
    except Exception:
        await message.answer('Не удалось загрузить данные, попробуй позже')
        return
    me = next((u for u in users if str(u.get('telegram_id')) == tg_id), None)
    if me and me.get('fav_team_id'):
        launch_kb = InlineKeyboardMarkup(
            inline_keyboard=[
                [InlineKeyboardButton(
                    text='🚀 Запустить приложение',
                    web_app=WebAppInfo(url=MINI_APP_URL),
                )],
                [InlineKeyboardButton(
                    text='✨ Титры', callback_data='credits')],
            ],
        )
        await message.answer('Готово, можно запускать приложение', reply_markup=launch_kb)
        return
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

    agreement_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='✅ Согласен(сна)',
                callback_data=AGREE_CALLBACK_DATA,
            )],
            [InlineKeyboardButton(
                text='❌ Не согласен(сна)',
                callback_data=DISAGREE_CALLBACK_DATA,
            )],
        ],
    )
    await cb.message.edit_text(USER_AGREEMENT_TEXT, reply_markup=agreement_kb)


@router.callback_query(F.data == 'credits')
async def credits(cb: CallbackQuery) -> None:
    await cb.answer()
    text = (
        '✨ Бот разработан Никитой Чуваевым из б.студио\n'
        '🧪 б.студио\n'
        '👨‍💻 Сольный проект Никиты: b.dev by никита чуваев\n'
        '🏆 ССК Сенатор РАНХиГС'
    )
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text='б.студио',
                url='https://t.me/balbescrew',
            )],
            [InlineKeyboardButton(
                text='б.dev',
                url='https://t.me/bdevbync',
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


async def push(topic: str, bot: Bot) -> None:
    async for message in kafka_client.consume(topic):
        package = json.loads(message)
        await bot.send_message(package['tg_id'], package['res'])


async def main() -> None:
    if not BOT_TOKEN:
        raise RuntimeError('BOT_TOKEN is required')
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    api = ApiClient(API_BASE_URL)
    kafka_client = KafkaClient(KAFKA_BOOTSTRAP_SERVERS)
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
        await kafka_client.close()


if __name__ == '__main__':
    asyncio.run(main())
