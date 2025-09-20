from tortoise import fields
from tortoise.models import Model
from app.src._utill_tools import current_file_dir, translit
import re


class Team(Model):
    id = fields.IntField(pk=True)
    name = fields.CharField(max_length=255)
    logo_url = fields.CharField(max_length=1024)

    async def save(self, *args, **kwargs):
        if not self.logo_url:
            name_slug = translit(self.name).lower().replace(' ', '_')
            self.logo_url = f'{current_file_dir}/assets/{name_slug}.png'
        await super().save(*args, **kwargs)


class User(Model):
    id = fields.IntField(pk=True)
    username = fields.CharField(max_length=255)
    telegram_id = fields.CharField(max_length=255)
    name = fields.CharField(max_length=255)
    fav_team = fields.ForeignKeyField(
        'models.Team', related_name='users', null=True)


class Match(Model):
    id = fields.IntField(pk=True)
    team1 = fields.ForeignKeyField(
        'models.Team', related_name='matches_as_team1')
    team2 = fields.ForeignKeyField(
        'models.Team', related_name='matches_as_team2')
    stage_name = fields.CharField(max_length=255)
    date = fields.DatetimeField()
    result = fields.CharField(max_length=255)

    async def save(self, *args, **kwargs):
        if self.result is not None:
            if not _is_valid_score(self.result):
                raise ValueError('invalid_result')
        await super().save(*args, **kwargs)


class Bet(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        'models.User', related_name='bets')
    match = fields.ForeignKeyField(
        'models.Match', related_name='bets')
    result = fields.CharField(max_length=255)

    async def save(self, *args, **kwargs):
        if self.result is not None:
            if not _is_valid_score(self.result):
                raise ValueError('invalid_result')
        await super().save(*args, **kwargs)


class Post(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        'models.User', related_name='posts')
    photo_url = fields.CharField(max_length=1024)
    created_at = fields.DatetimeField(auto_now_add=True)
    checked = fields.BooleanField(default=False)


__all__ = ['Team', 'User', 'Match', 'Bet', 'Post']

_score_re = re.compile(r'^[0-9]{1,2}:[0-9]{1,2}$')


def _is_valid_score(value: str) -> bool:
    if not isinstance(value, str):
        return False
    if not _score_re.match(value):
        return False
    left, right = value.split(':', 1)
    try:
        a = int(left)
        b = int(right)
    except ValueError:
        return False
    return 0 <= a <= 99 and 0 <= b <= 99
