# Data dictionary

What every field in the data files means. Useful if you want to reuse the data, fix an entry by hand, or add a festival.

All data files are plain **JSON** (text files that any program can read).

---

## 1. `festivals.json`

```json
{ "default": "blf", "festivals": [ { ...one object per festival... } ] }
```

| Field | Meaning |
|---|---|
| `id` | Short code used in web addresses, e.g. `blf` → `?f=blf` |
| `status` | `live` (has data) or `soon` (only dates and a link) |
| `type` | Omitted for speaker-type festivals; `programme` for festivals with a schedule |
| `name`, `short`, `ab` | Full name, short name for buttons, and a 3-4 letter code for the Across grid |
| `year`, `dates`, `venue` | Edition year, human-readable dates, place |
| `start`, `end` | The edition's dates as `YYYY-MM-DD` (drives countdowns and calendar files) |
| `tbc` | `1` if the dates are not confirmed yet |
| `country`, `state`, `city` | Where the festival is held (state is the Indian state, or the nation within the UK such as Wales). Drives the India / International filters on the home page |
| `url` | Official website |
| `logo`, `base` | Logo path, and the festival's data folder (`festivals/<id>/`) |
| `from`, `to`, `years` | The years of history we have: first year, last earlier year, or an explicit list |
| `sched` | First year with schedule data |
| `partUrl` | Pattern for a speaker's page on the festival site; `{u}` is replaced with the speaker's slug |
| `why` | Optional one-line reasons for the "Start here" cards |
| `updated` | A sentence on how fresh and how complete the data is (shown in About) |
| `past` | `1` if the folder has a `past.json` (set automatically by `tools/build_index.py`) |
| `archive` | `true` hides a festival from Search, Across and Explore (used for old, duplicate editions) |
| `note` | Text shown on a "soon" page |
| `wip` | `1` marks a festival we know of but have no official portal or data for yet. Its page says "Work in progress" and invites organisers to get in touch |
| `sub`, `themeLabel`, `forumLabel` | Programme festivals: subtitle, and what to call a session's category and venue |

---

## 2. A speaker: `data.json` and `past.json`

Both files are a list of objects with the same shape. `past.json` adds `"past": 1` and sometimes `url`.

| Field | Meaning |
|---|---|
| `n` | Name |
| `b` | Short bio (first ~220 characters) |
| `f` | Full bio (empty if the festival published none) |
| `y` | Years we found this person at this festival |
| `first` | `1` = no earlier appearance in our lists; `0` = has appeared before |
| `pre` | Reserved (earlier-appearance detail); usually empty |
| `g` | Gender: `f`, `m` or `u` (unknown). Only from pronouns in the bio. |
| `role` | Role guessed from keywords ("Author", "Journalist", "Poet", …) |
| `nonauth` | `1` if the person is not mainly an author (used for labels) |
| `t` | The theme group they are shown under |
| `p`, `r` | `p` = a "pick" for the Who-to-hear list; `r` = its rank |
| `a` | Age, only if publicly documented (rarely filled) |
| `l` | Latest work, if stated |
| `s` | Past sessions as `[year, title]` pairs (where the festival lists them) |
| `u` | Slug: the person's address on the festival site, also used for the photo file name |
| `cc`, `cb` | Country, and the basis (`named in bio`) |
| `dia` | `1` if described as diaspora |
| `city` | City, where the bio names one |
| `lg`, `le` | Languages (a list) and a free-text language note |
| `ph` | Photo path inside the festival folder; empty if none |
| `bk` | Books: a list of `{ "t": title, "c": cover file, "b": 0/1/2 }` where `b` says where it came from: `1` in the bio, `2` Open Library, `0` not in bio |
| `url` | (`past.json` only) a link to the person's own page, where one exists |

---

## 3. `history.json`

```json
{ "2018": ["Name One", "Name Two"], "2019": [ ... ] }
```
Just names per year. This is what powers Search, Across, the **Past years** list and the year charts.

## 4. `stats.json`

| Field | Meaning |
|---|---|
| `per[year]` | `{ total, returning, inNow }`: speakers that year, how many had spoken before, how many are also in the current edition |
| `lead` | The most frequent speakers |
| `hist` | A histogram: how many speakers have been to 0, 1, 2… earlier editions |

---

## 5. Programme-style festivals (`"type": "programme"`)

`data.json` is an object:

```json
{
  "sessions": [ { "d": 28, "f": 1, "t": "11:00–11:50", "k": "Title", "e": "English title",
                  "th": "Panel", "pp": [["p","Name"],["c","Moderator"]] } ],
  "forums":   [ { "id": 1, "k": "Chavadi (OPJ Museum)", "e": "…" } ],
  "days":     [ { "d": 28, "l": "Sat 28 Nov" } ],
  "bios":     { "Name": { "b": "short bio", "ph": "ph/name.webp" } },
  "places":   { "Name": { "d": "Ballari", "w": "ಬಳ್ಳಾರಿ" } }
}
```

| Field | Meaning |
|---|---|
| `d`, `t` | Day of the month and the time range (`PM` is understood, plain numbers like `2:00` mean afternoon) |
| `f` | Venue/stage id (0 = main) |
| `k`, `e` | Title as published, and an English title if different |
| `th` | Category (Panel, Performance, Workshop…) |
| `pp` | People as `[role, name]`. Roles: `p` speaker, `c` moderator, `m` host, `g` guest, `s` performer, `h` chair, `v` poet, `r` respondent, `k` keynote |
| `places` | Optional: where people are based, for the Karnataka map |

---

## 6. Files the daily check writes (`data/`)

| File | Meaning |
|---|---|
| `data/snapshots/<id>.json` | The last list of names seen on each festival's live page |
| `data/updates.json` | The latest run: counts, who was added or removed, names live but not yet in the app, any fetch problems |
| `data/updates-log.json` | Every change ever recorded, newest first |
| `data/last-changes.md` | A short summary, only present when something changed (used for the GitHub issue) |
| `data/history-all.json` | All festivals' `history.json` files joined, so Search loads one small file |
| `data/debut.json` | Each author's earliest listed work year from Open Library (for the Debuts tab) |

---

## 7. Where the data comes from

| Source | Used for |
|---|---|
| Each festival's own website or public data feed | Names, bios, photos, sessions, dates |
| [Open Library](https://openlibrary.org) | Book titles, covers, earliest-work years |
| Printed invitations and agendas (typed by hand) | Samajamukhi, Jananudi, JSW Sahitya Habba |

Per-festival details and gaps are in [DATA-NOTES.md](DATA-NOTES.md).
