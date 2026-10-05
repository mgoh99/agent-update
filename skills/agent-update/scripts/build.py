#!/usr/bin/env python3
"""Render an agent update page from a JSON data file.

Usage: build.py data.json [out.html]   (default out: index.html beside data.json)

The page is static HTML with a fixed layout: header, purpose, skills,
connectors, scheduled jobs, and a closing "last two weeks" section.
See ../references/example.json for the data shape.
"""
import html
import json
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parent.parent
FONTS = ('<link rel="stylesheet" href="https://fonts.googleapis.com/css2?'
         'family=DM+Serif+Display:ital@0;1&family=Outfit:wght@300;400;500;600&display=swap">')


def esc(s):
    return html.escape(str(s if s is not None else ''), quote=True)


def need(d, key, where='data'):
    if key not in d or d[key] in (None, ''):
        sys.exit(f'build.py: missing "{key}" in {where}')
    return d[key]


def link(text, url):
    if url and str(url).startswith(('https://', 'http://')):
        return f'<a href="{esc(url)}">{esc(text)}</a>'
    return esc(text)


def k_cell(label, slug):
    return (f'<td class="k"><span class="lbl">{esc(label)}</span>'
            f'<span class="slug">{esc(slug)}</span></td>')


def section(title, sub, body):
    return (f'<section class="blk fade"><div><h2>{esc(title)}</h2><p class="sub">{esc(sub)}</p></div>'
            f'<div>{body}</div></section>')


def skill_table(items, cls='t'):
    rows = ''.join(f'<tr>{k_cell(s[1], s[0])}<td class="d">{esc(s[2])}</td></tr>' for s in items)
    return f'<table class="{cls}">{rows}</table>'


def render(a):
    for key in ('name', 'role', 'since', 'purpose', 'accomplished'):
        need(a, key)
    skills = a.get('skills', [])
    shared = a.get('shared') or {}
    conn = a.get('conn', [])
    jobs = a.get('jobs', [])
    live = a.get('live', True)
    n_skills = sum(len(g['items']) for g in skills) + len(shared.get('items', []))
    job_count = a.get('jobCount', len(jobs))
    pill = a.get('statusLabel') or ('Live' if live else 'Built · not deployed')

    h = ('<header class="head fade"><div class="row">'
         f'<h1>{esc(a["name"])}</h1><span class="tag">{esc(a["role"])}</span>'
         f'<span class="pill {"pill--good" if live else "pill--warn"}">{esc(pill)}</span></div>'
         f'<p class="kicker">{esc(a["since"])}</p>'
         '<div class="stats">'
         f'<div class="stat"><div class="n">{n_skills}</div><div class="l">skills</div></div>'
         f'<div class="stat"><div class="n">{len(conn)}</div><div class="l">connectors and CLIs</div></div>'
         f'<div class="stat"><div class="n">{job_count}</div><div class="l">scheduled jobs</div></div>'
         '</div></header>')

    bounds = ''.join(f'<li>{esc(b)}</li>' for b in a.get('bounds', []))
    h += section('Purpose', 'What it owns, and where it stops',
                 f'<div class="purpose"><p>{esc(a["purpose"])}</p><ul>{bounds}</ul></div>')

    body = ''.join(f'<div class="grp"><div class="g">{esc(g["g"])}</div>{skill_table(g["items"])}</div>'
                   for g in skills)
    if not skills:
        body += (f'<p style="color:var(--ink-2);font-size:13.5px;max-width:60ch">'
                 f'{esc(a.get("noSkillsNote", "No task skills of its own beyond the shared set."))}</p>')
    if shared.get('items'):
        body += (f'<div class="grp" style="margin-top:18px"><div class="g">'
                 f'{esc(shared.get("title", "Shared — same in every agent"))}</div>'
                 f'{skill_table(shared["items"], "t h")}</div>')
    h += section('Skills', 'Repeatable workflows, run on request or on schedule', body)

    rows = ''.join(f'<tr>{k_cell(c[1], c[0])}<td class="kind">{esc(c[2])}</td>'
                   f'<td class="d">{esc(c[3])}</td><td class="acc">{esc(c[4])}</td></tr>' for c in conn)
    h += section('Connectors and CLIs', 'How it reaches each system, and how far', f'<table class="t">{rows}</table>')

    rows = ''
    for j in jobs:
        sep = ' class="sep"' if len(j) > 4 and j[4] else ''
        note = f' <small>{esc(j[3])}</small>' if len(j) > 3 and j[3] else ''
        rows += (f'<tr{sep}><td class="c">{esc(j[0])}</td><td class="tm">{esc(j[1])}</td>'
                 f'<td class="j">{esc(j[2])}{note}</td></tr>')
    note = f'<p class="harness-note">{esc(a["jobsFootnote"])}</p>' if a.get('jobsFootnote') else ''
    h += section('Scheduled jobs', a.get('jobsNote', 'Eastern time'), f'<table class="sched">{rows}</table>{note}')

    acc = a['accomplished']
    body = ''
    if acc.get('summary'):
        body += f'<div class="purpose" style="margin-bottom:22px"><p>{esc(acc["summary"])}</p></div>'
    groups = acc.get('groups', [])
    for g in groups:
        rows = ''
        for it in g['items']:
            for key in ('date', 'title', 'detail'):
                need(it, key, f'accomplished item in "{g.get("g")}"')
            rows += (f'<tr>{k_cell(it["title"], it["date"])}<td class="d">{esc(it["detail"])}</td>'
                     f'<td class="acc">{link(it.get("result", ""), it.get("url"))}</td></tr>')
        body += f'<div class="grp"><div class="g">{esc(g["g"])}</div><table class="t done">{rows}</table></div>'
    if not groups:
        body += ('<p style="color:var(--ink-2);font-size:13.5px;max-width:60ch">'
                 'Nothing delivered in this window that I can show evidence for.</p>')
    if acc.get('footnote'):
        body += f'<p class="harness-note">{esc(acc["footnote"])}</p>'
    h += section(acc.get('title', 'The last two weeks'),
                 f'What I got done for you · {need(acc, "window", "accomplished")}', body)

    title = f'{a["name"]} · Agent update'
    css = (SKILL / 'assets' / 'style.css').read_text()
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{esc(title)}</title>{FONTS}<style>\n{css}</style></head><body>\n'
            f'<main class="content" id="content">{h}</main>\n</body></html>\n')


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    src = Path(sys.argv[1]).resolve()
    out = Path(sys.argv[2]).resolve() if len(sys.argv) > 2 else src.with_name('index.html')
    out.write_text(render(json.loads(src.read_text())))
    print(out)


if __name__ == '__main__':
    main()
