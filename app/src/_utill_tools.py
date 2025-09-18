# flake8: noqa: E501
import os

current_file_path = os.path.abspath(__file__)
current_file_dir = os.path.dirname(current_file_path)

_ru = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
_RU = _ru.upper()
_tr = ['a', 'b', 'v', 'g', 'd', 'e', 'e', 'zh', 'z', 'i', 'y', 'k', 'l', 'm', 'n', 'o',
       'p', 'r', 's', 't', 'u', 'f', 'h', 'c', 'ch', 'sh', 'shch', '', 'y', '', 'e', 'yu', 'ya']
_map = {r: t for r, t in zip(_ru, _tr)}
_map.update({r: t.upper() for r, t in zip(_RU, _tr)})


def translit(s: str) -> str:
    out = []
    for ch in s:
        out.append(_map.get(ch, ch))
    return ''.join(out)
