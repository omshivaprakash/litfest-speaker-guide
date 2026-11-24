# LitFest Speaker Guide

An interactive, mobile-friendly guide to literature-festival speakers: who is new, who keeps coming back, books, languages, countries and gender representation over the years.

Live site (GitHub Pages): https://omshivaprakash.github.io/litfest-speaker-guide/

## Festivals

| Festival | Status |
|---|---|
| Bangalore Literature Festival 2026 (`?f=blf`) | Live: 243 speakers |
| Samajamukhi Sahitya Sammelana, 28–29 Nov 2026 (`?f=sjm`) | Live: programme only (sessions and names, Kannada) |
| Jananudi 2026, 28–29 Nov, Mangaluru (`?f=jn`) | Live: programme only (sessions and names, Kannada) |
| Book Brahma Literature Festival 2026, 14–23 Aug (`?f=bbl`) | Live: 212 sessions, 400 speakers with bios and photos (no earlier editions) |
| Hyderabad Literary Festival 2027 (`?f=hlf`) | Live: 135 announced so far (speakers and moderators); history 2021–2026 |
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
Built by `tools/build_jlf.py` from the festival's public speakers API (the same one its website uses). The 2027 line-up is still being announced, so the list will grow; re-run the script with fresh API output to update. Only about 110 speakers have bios so far, so gender, country and role are blank for the rest, and "first-time" means not listed in 2018–2026. Books come from titles in italics in the bios and from Open Library (exact author-name match only; for speakers with no bio, only when at least three titles have covers, so some real authors are missing). Library of Congress and Amazon were not used: the first sits behind a bot check and the second has no free public lookup. Languages and ages are not included. "Start here" lists speakers the festival flags as important.

The Samajamukhi and Jananudi programmes were transcribed by hand from their printed invitations; please check names against the official programmes.

## Map (programme festivals)
The Samajamukhi and Jananudi pages have a "Map" tab: a schematic Karnataka map with people placed by district. `tools/place_names.py` places a person only when the invitation gives a place next to them or their printed name carries a Karnataka town or village. That covers a minority of names (14 of 210 for Samajamukhi, 19 of 73 for Jananudi), and it is an inference from names, not where people live. Edit the `PLACE` and `MANUAL` tables in that script and re-run it to correct or extend it.

## Insights (programme festivals)
An "Insights" tab shows a day-by-day timeline, sessions by theme, appearances by role, panel sizes and repeat names. Themes come from `tools/tag_themes.py`, which tags each session from its English title with simple keyword rules, so treat them as a rough guide.

The programme festivals page through content (Prev / Next) so nothing scrolls, like the Bangalore pages. Insights are three screens: a theme-coloured timeline, themes and roles, and panel sizes.

## Book Brahma data
Built by `tools/fetch_bblf.py` (speaker pages) and `tools/build_bblf.py` (the festival's published schedule PDF). A person is listed in a session only if their name in the schedule matches the official speakers page, so about 100 of the 400 speakers have no session shown. Earlier editions (2024, 2025) have only photo galleries on the festival site, so there is no history, first-time flag or trend for this festival. Languages shown are the session language printed in the schedule; many sessions do not print one.

## Hyderabad data
Built by `tools/build_hlf.py` from hydlitfest.org: the 2027 speakers and moderators pages (with profile pages and photos) and the past-speakers pages for 2021–2026. The site does not yet state the 2027 dates, so none are shown. 2022 combines the two small events that year (Anuvaad and Kaavya Dhaara), so its count is low. Names are matched across years by spelling, so a person listed under a different spelling counts as new. Roles and countries are guessed from bio keywords; books, languages and ages are not included.
