from tortoise import fields
from tortoise.models import Model
from app.src._utill_tools import current_file_dir, translit


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
    # 1:0 или как-то так, такой стандарт, чтобы не было путаницы
    result = fields.CharField(max_length=255)


class Bet(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        'models.User', related_name='bets')
    match = fields.ForeignKeyField(
        'models.Match', related_name='bets')
    # также как и в матче
    result = fields.CharField(max_length=255)


class Post(Model):
    id = fields.IntField(pk=True)
    user = fields.ForeignKeyField(
        'models.User', related_name='posts')
    photo_url = fields.CharField(max_length=1024)
    created_at = fields.DatetimeField(auto_now_add=True)
    checked = fields.BooleanField(default=False)


__all__ = ['Team', 'User', 'Match', 'Bet', 'Post']
