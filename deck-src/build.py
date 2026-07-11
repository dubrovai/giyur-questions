import json, pathlib, re, sys

SCRATCH = pathlib.Path(__file__).resolve().parent
PROJECT = SCRATCH.parent

deck = []
for n in (1, 2, 3):
    part = json.loads((SCRATCH / f'deck{n}.json').read_text(encoding='utf-8'))
    deck.extend(part)

ids = [c['id'] for c in deck]
assert len(ids) == len(set(ids)), 'duplicate ids'
for c in deck:
    for f in ('id', 'sec', 'topic', 'q', 'a', 'd'):
        assert f in c and c[f], f'missing {f} in {c.get("id")}'
    if 'he' in c:
        for l in c['he']:
            assert all(k in l for k in ('h', 't', 'r')), f'bad he in {c["id"]}'

secs = []
for c in deck:
    if c['sec'] not in secs:
        secs.append(c['sec'])

template = (SCRATCH / 'template.html').read_text(encoding='utf-8')
deck_js = json.dumps(deck, ensure_ascii=False, separators=(',', ':')).replace('</', '<\\/')
body = template.replace('/*__DECK__*/[]', deck_js)
assert deck_js in body, 'placeholder not replaced'

title = 'Гиюр · Итоговые вопросы курса'
(SCRATCH / 'giyur-cards-artifact.html').write_text(f'<title>{title}</title>\n' + body, encoding='utf-8')

local = (
    '<!doctype html>\n<html lang="ru">\n<head>\n<meta charset="utf-8">\n'
    '<meta name="viewport" content="width=device-width, initial-scale=1">\n'
    f'<title>{title}</title>\n</head>\n<body>\n' + body + '\n</body>\n</html>\n'
)
(PROJECT / 'index.html').write_text(local, encoding='utf-8')

md = ['# Гиюр — итоговые вопросы и ответы', '',
      'Ответы даны с позиций реформистского (прогрессивного) иудаизма, община в Израиле.',
      'Вопросы, помеченные **[личный ответ]**, требуют вашей собственной формулировки — дана канва.', '']
for sec in secs:
    md.append(f'## {sec}')
    md.append('')
    cur_topic = None
    for c in deck:
        if c['sec'] != sec:
            continue
        if c['topic'] != cur_topic:
            cur_topic = c['topic']
            md.append(f'### {cur_topic}')
            md.append('')
        p = ' **[личный ответ]**' if c.get('p') else ''
        md.append(f'**{c["q"]}**{p}')
        md.append('')
        md.append(c['a'])
        md.append('')
        for l in c.get('he', []):
            md.append(f'> {l["h"]}')
            md.append(f'> *{l["t"]}*')
            md.append(f'> {l["r"]}')
            md.append('')
        md.append(f'*{c["d"]}*')
        md.append('')
(PROJECT / 'giyur-answers.md').write_text('\n'.join(md), encoding='utf-8')

per_sec = {s: sum(1 for c in deck if c['sec'] == s) for s in secs}
print(f'cards: {len(deck)}')
print(f'sections: {per_sec}')
print(f'personal: {sum(1 for c in deck if c.get("p"))}, hebrew: {sum(1 for c in deck if "he" in c)}')
print(f'html: {(PROJECT / "index.html").stat().st_size // 1024} KB')
