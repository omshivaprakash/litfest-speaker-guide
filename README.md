# LitFest Speaker Guide

An interactive, mobile-friendly guide to literature-festival speakers: who is new, who keeps coming back, books, languages, countries and gender representation over the years.

Live site (GitHub Pages): https://omshivaprakash.github.io/litfest-speaker-guide/

## Festivals

| Festival | Status |
|---|---|
| Bangalore Literature Festival 2026 (`?f=blf`) | Live: 243 speakers |
| Samajamukhi Sahitya Sammelana, 28–29 Nov 2026 (`?f=sjm`) | Live: programme only (sessions and names, Kannada) |
| Jaipur Literature Festival 2027, 14–18 Jan (`?f=jlf`) | Live: 280 speakers announced so far; history 2018–2026 |

## Layout

```
index.html            the app (no build step, no dependencies)
festivals.json        list of festivals and their settings
festivals/<id>/       data.json, stats.json, logo.png, ph/ (photos), bk/ (book covers)
```

## Adding a festival

1. Create `festivals/<id>/` with `data.json`, `stats.json`, `logo.png`, `ph/` and `bk/`.
2. In `festivals.json`, add or edit its entry: set `status` to `live`, and fill `name`, `short`, `year`, `dates`, `venue`, `url`, `logo`, `base` (`festivals/<id>/`), `from` and `to` (archive years of speaker pages), `sched` (first year with schedule data), `partUrl` (speaker page URL with `{u}` for the slug) and `why` (optional one-line notes for the "Start here" shelf).
3. Commit and push. Pages redeploys.

### `data.json` (one object per speaker)
`n` name, `b` short bio, `f` full bio, `y` years seen, `first` first-timer flag, `g` gender (`f`/`m`/`u`, from bio pronouns only), `t` theme, `a` age if publicly documented, `l` latest work, `s` past sessions `[year, title]`, `u` slug, `ph` photo path, `bk` books `[{t, c, b}]` (`b`: 0 not named in bio, 1 in bio, 2 Open Library), `lg` languages, `role`, `nonauth`, `cc` country, `dia` diaspora flag, `city`.

### `stats.json`
`per[year] = {total, returning, inNow}`, `lead` (most frequent speakers), `hist` (editions-attended histogram).

## Notes on the data
Built from each festival's public speaker pages, bios and schedules, plus Open Library for book covers. Gender is inferred only from pronouns in bios, so it is missing for some speakers. Photos, logos and book covers belong to their owners and are used here for identification.

Run locally: `python3 -m http.server` and open http://localhost:8000/.

## Programme-type festivals
A festival entry with `"type": "programme"` uses `festivals/<id>/data.json` shaped as `{sessions:[{d,f,t,k,e,pp:[[role,name]]}], forums:[{id,k,e}], en:{name:englishName}}` and shows Programme and People tabs. Roles: `p` panel, `c` coordinator, `m` host, `r` respondent, `g` guest, `s` performer. The Samajamukhi data was transcribed by hand from the printed invitation, so please check it against the official programme.

## Jaipur data
Built by `tools/build_jlf.py` from the festival's public speakers API (the same one its website uses). The 2027 line-up is still being announced, so the list will grow; re-run the script with fresh API output to update. Only about 110 speakers have bios so far, so gender, country and role are blank for the rest, and "first-time" means not listed in 2018–2026. Books, languages and ages are not included. "Start here" lists speakers the festival flags as important.
