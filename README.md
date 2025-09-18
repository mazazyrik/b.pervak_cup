## b.pervak_cup backend API

### Быстрый старт
- Установка: `uv sync`
- Запуск: `uv run uvicorn app.src.main:app --reload`
- Swagger: `/docs`

### Аутентификация
- Токен = 'telegram_id'
- Варианты:
  - Сессия: `POST /auth/login` с телом `{ 'telegram_id': '123' }`
  - Bearer: заголовок `Authorization: Bearer 123`

Пример логина:
```bash
curl -X POST 'http://localhost:8000/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{ "telegram_id": "123" }'
```

### Общие примечания к моделям
- 'Match.result': счёт в формате '1:0'
- 'Bet.result': такой же формат, как у 'Match.result'
- 'Team.logo_url': автогенерация при сохранении, путь строится из транслита имени команды: '{current_file_dir}/assets/{translit(name).lower().replace(' ', '_')}.png'

### Teams
- 'GET /teams' — список
- 'POST /teams' — создать
  - Тело: `{ 'name': 'Spartak' }`
- 'GET /teams/{id}' — получить
- 'PUT /teams/{id}' — обновить
  - Тело: `{ 'name': 'Zenit' }` (любые поля опциональны)
- 'DELETE /teams/{id}' — удалить

Пример:
```bash
curl -H 'Authorization: Bearer 123' 'http://localhost:8000/teams'
```

### Users
- 'GET /users'
- 'POST /users'
  - Тело: `{ 'username': 'nick', 'telegram_id': '123', 'name': 'Nikita', 'fav_team_id': 1 }`
- 'GET /users/{id}'
- 'PUT /users/{id}'
  - Тело: `{ 'name': 'Nikita P.' }`
- 'DELETE /users/{id}'

### Matches
- Поля: 'team1_id', 'team2_id', 'date' (ISO), 'result' ('1:0'), 'stage_name'
- 'GET /matches'
- 'POST /matches'
  - Тело: `{ 'team1_id': 1, 'team2_id': 2, 'date': '2025-01-01T12:00:00Z', 'result': '0:0', 'stage_name': 'group_a' }`
- 'GET /matches/{id}'
- 'PUT /matches/{id}'
  - Любые поля опциональны, например `{ 'result': '2:1' }`
- 'DELETE /matches/{id}'

### Posts
- Поля: 'user_id', 'photo_url', 'created_at', 'checked' (флаг модерации)
- 'GET /posts'
- 'POST /posts'
  - Тело: `{ 'user_id': 1, 'photo_url': 'https://...', 'checked': false }`
- 'GET /posts/{id}'
- 'PUT /posts/{id}'
  - Тело: `{ 'photo_url': 'https://...', 'checked': true }`
- 'DELETE /posts/{id}'

Отображение на фронте:
- Пост показывается только если 'checked' == true. 'GET /posts' уже возвращает только проверенные.

### Авторизация в Swagger
- Нажать 'Authorize' и вставить токен (ваш 'telegram_id') без префикса
- Либо выполнить 'POST /auth/login' и работать по сессии

### CORS
- Открыт для всех источников: можно вызывать API с любого домена фронта

### Коды ошибок
- '401 unauthorized' — нет токена в сессии и заголовке
- '404 not_found' — ресурс не найден
- '400 invalid_*' — валидационные ошибки связей