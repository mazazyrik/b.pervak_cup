import asyncio
from tortoise import Tortoise
from app.src.crud import Team


async def create_team(name: str, logo_url: str = None):

    team = Team(name=name, logo_url=logo_url)
    await team.save()
    return team


async def load_teams():
    teams_data = [
        {
            'name': 'ЭМИТ',
            'logo_url': (
                'https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/.logos/'
                '%D1%8D%D0%BC%D0%B8%D1%82.png'
            )
        },
        {
            'name': 'ИГСУ',
            'logo_url': (
                'https://raw.githubusercontent.com/mazazyrik/b.pervak_cup/refs/heads/main/.logos/'
                '%D0%B8%D0%B3%D1%81%D1%83.png'
            )
        },
        {
            'name': 'Ресурс России',
            'logo_url': (
                'https://github.com/mazazyrik/b.pervak_cup/blob/main/.logos/'
                '%D1%80%D0%B5%D1%81%D1%83%D1%80%D1%81.png'
            )
        },
        {
            'name': 'ИНУП',
            'logo_url': (
                'https://github.com/mazazyrik/b.pervak_cup/blob/main/.logos/'
                '%D0%BD%D0%BE%D0%B2%D0%B0.png'
            )
        },
        {
            'name': 'МОФ',
            'logo_url': (
                'https://github.com/mazazyrik/b.pervak_cup/blob/main/.logos/'
                '%D0%BC%D0%BE%D1%84.png'
            )
        },
        {
            'name': 'КМПО',
            'logo_url': (
                'https://github.com/mazazyrik/b.pervak_cup/blob/main/.logos/'
                '%D0%BA%D0%BC%D0%BF%D0%BE.png'
            )
        },
        {
            'name': 'ИПНБ',
            'logo_url': (
                'https://github.com/mazazyrik/b.pervak_cup/blob/main/.logos/'
                '%D0%B8%D0%BF%D0%BD%D0%B1.png'
            )
        },
        {
            'name': 'ИОН',
            'logo_url': (
                'https://github.com/mazazyrik/b.pervak_cup/blob/main/.logos/'
                '%D0%B8%D0%BE%D0%BD.png'
            )
        }
    ]

    for team_data in teams_data:
        team = await create_team(team_data['name'], team_data['logo_url'])
        print(f'Создана команда: {team.name} с ID: {team.id}')


if __name__ == '__main__':
    async def _main():
        await Tortoise.init(
            db_url='sqlite://database.db',
            modules={'models': ['app.src.crud']}
        )
        await Tortoise.generate_schemas()
        await load_teams()
        await Tortoise.close_connections()

    asyncio.run(_main())
