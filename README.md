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
| Kerala Literature Festival 2026 (`?f=klf`) | Live: 495 speakers with bios, photos and 2026 sessions; history 2023–2024 only |
| Literature Live! The Mumbai LitFest 2026, 23–25 Oct (`?f=tll`) | Live: 103 speakers with bios, photos and sessions; history 2024–2025; books from the festival's own list |
| Bengaluru Poetry Festival 2026, 1–2 Aug (`?f=bpf`) | Live: 71 poets with bios and photos; history 2016–2025 (no 2021) |
| Kolkata Literary Meet 2026, 22–26 Jan (`?f=klm`) | Live: 171 speakers with bios, photos, sessions and books; history 2023–2025 |
| Neev Literature Festival 2026, 26–27 Sep (`?f=nlf`) | Live, small: the featured speakers only (about ten a year), history 2023–2025 |
| Kalinga Literary Festival 2026, 8–11 Jan (`?f=klf2`) | Live: 132 speakers with bios and photos; earlier years list featured names only (2021, 2022, 2024) |
| Goa Arts and Literature Festival 2026, 12–14 Feb (`?f=galf`) | Live: 28 speakers with bios and photos; history 2023–2025 (2023 lists only a few names) |
| Dehradun Literature Festival 2026, 27–29 Nov (`?f=ddlf`) | Live, thin: 55 speakers (names and photos), 2025 history only |
| Bhopal Literature & Art Festival 2027, 8–10 Jan (`?f=bplf`) | Live: 65 speakers announced so far (with bios), history 2019–2026 |
| Mathrubhumi International Festival of Letters 2027, 28–31 Jan (`?f=mbifl`) | Live, thin: 6 speakers announced so far; history 2018–2020 and 2023–2026 |
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
Built by `tools/build_hlf.py` from hydlitfest.org: the 2027 speakers and moderators pages (with profile pages and photos) and the past-speakers pages for 2021–2026. The site does not yet state the 2027 dates, so none are shown. 2022 combines the two small events that year (Anuvaad and Kaavya Dhaara), so its count is low. Names are matched across years by spelling, so a person listed under a different spelling counts as new. Roles and countries are guessed from bio keywords. Books come from Open Library on an exact author-name match (`tools/add_books_ol.py`); speakers with no bio only get books when at least three titles have covers, so coverage is partial and a same-name author can slip in. Languages and ages are not included.

## Search all festivals
The "Search all" button searches every festival's speaker list for every year (`festivals/<id>/history.json`, built by `tools/build_history.py` and `tools/build_hlf.py`) and shows which festivals and years a person appeared in. Tapping a result opens that festival filtered to the person.

## Disclaimer and contact
This is an independent, non-commercial project for education and research. It is not affiliated with any festival. Names, photos, logos and book covers belong to their owners and are shown to identify people and festivals. Gender, country, role and language are inferred from public bios and can be wrong. To report a mistake or ask for a name, photo or festival to be changed or removed, [open an issue](https://github.com/omshivaprakash/litfest-speaker-guide/issues/new).

## Kerala data
Built by `tools/build_klf.py` from the speakers and sessions files the festival's own site loads, plus the 2023 and 2024 programme pages in its archive; books come from titles in italics in the bios and Open Library (`tools/add_books_ol.py`). 2025 has no usable list in the archive, so history covers 2023, 2024 and 2026 and "first-time" means not seen in those years. The next edition is announced for 21–24 January 2027 with no line-up yet.

## Mumbai (Literature Live!) data
Built by `tools/build_tll.py` from litlive.in: the speakers pages for 2024–2026, each 2026 speaker page (bio, sessions) and the festival's "Books at the LitFest" lists for 2025 and 2026. The festival states each speaker's role and country, so those are not guessed. Earlier years (before 2024) are not on the site in the same form.

## Bengaluru Poetry Festival data
Built by `tools/build_bpf.py` from bengalurupoetryfestival.org: the 2026 poets page (bios, photos) and each past year's archive page (poet names). The festival was not held in 2021, so that year is absent. Language and country are read from bios; books and ages are not included.

## Kolkata data
Built by `tools/build_klm.py` from kolkatalitmeet.in (each year's site lists its speakers; the 2026 pages give bios, photos and sessions) plus books from bio titles and Open Library (`tools/add_books_ol.py`). The 2020–2022 sites use a different layout and are not included, so history starts in 2023.

## Neev data
Built by `tools/build_nlf.py` from the speakers page of neevliteraturefestival.org, which lists only the featured speakers for each year (about ten, selected with `?y=`). The site's full events and speakers listings load through scripts, so the guest list is incomplete and 2022 is left out (its filter returns the unfiltered page).

## License
The code is released under the [MIT License](LICENSE). The MIT license covers the code only. Speaker names, bios, photos, festival logos and book covers belong to their owners and are included for identification, education and research; they are not covered by this license.

## Kalinga data
Built by `tools/build_kalinga.py` from the /klf-speakers/ page of kalingaliteraryfestival.com, which tags each speaker by edition. The current edition is listed in full; 2021, 2022 and 2024 list only a few featured names, so history is partial. Books come from titles in bios and Open Library (`tools/add_books_ol.py`).

## Goa data
Built by `tools/build_galf.py` from the yearly speaker pages of goaartlitfest.com (speaker-2023 to speaker-2026). The site lists a modest number of names per year and some bios sit in image captions, so counts are lower than the festival's full programme. Country and gender are guessed from those bios.

## Across festivals
The "Across" button opens an overlap grid (people named at both of two festivals, tap a square to list them) and a list of the most-travelled people. It uses the same per-festival `history.json` files as the search and matches people by spelling of their name. Festivals cover different years and some lists are partial, so the numbers are indicative.

## Dehradun data
Built by `tools/build_ddlf.py` from the Wix pages of www.dehradunliteraturefestival.com: /team (2026 speakers, names and photos only) and /archives (the 2025 list; the other year tabs there load on demand and are not included). There are no bios, so gender, country and role are unknown.

## Bhopal data
Built by `tools/build_bhopal.py` from bhopalliteraturefestival.com: `/event/blf-YYYY/speakers` for 2019–2027 and the 2027 author pages for bios. The 2027 list is partial (announced so far). Gender, country and role come from the bio text only; unknown where the bio is silent. No books are listed yet.

## MBIFL data
Built by `tools/build_mbifl.py` from www.mbifl.com, assets.mbifl.com and english.mathrubhumi.com: the 2027 speaker feed (only a few announced so far; re-run to refresh), the 2026 speakers page, the 2025 feed (first 20 per Regional/National/International list, so 2025 is partial), 2024 and 2018–2020 feeds, and the 2023 page. There was no festival in 2021 or 2022. Names are matched across years by normalised spelling, so some repeat guests may be missed. No books listed yet.

## Self-contained
Everything the site displays is served from this repository: speaker photos, book covers, festival logos, data and the Fraunces and Inter fonts (`fonts/`). The only outbound links are ones you click (official festival sites, GitHub issues, the builder's page); no third-party requests are made when a page loads.

## Explore
The Explore button opens five one-screen views built from every festival's data: **Shelf** (book spines, with covers), **Prizes** (prizes named in bios), **Trails** (people by interest, most-travelled first), **Languages** (where a bio states them) and **My list** (starred people with books to read, copyable). Prizes and trails come from keyword matches in bios, so treat them as leads, not facts. Not built: debut-year cohorts, prize-year timelines and translation chains, because the data does not hold publication years, award years or translators.

## Name matching
Cross-festival matching (Search, Across, Explore) ignores titles, accents, dots and spacing in initials ("K S Nair" = "KS Nair") and a lone middle initial ("Abhijit V. Banerjee" = "Abhijit Banerjee"), plus a short hand-checked alias list (`GALIAS` in `index.html`). Other spelling variants still count as two people.

## Upcoming alerts
Explore → Upcoming lists every festival with a countdown, an "Add to calendar" file (.ics, with a reminder the day before) and a "Remind me" switch. Reminders are stored in your browser only: when a starred festival is within a week, a banner appears under the title the next time you open the site (and a browser notification if you allow it). The site has no server, so nothing is pushed to you while it is closed. Dates are in `festivals.json` (`start`, `end`, `tbc`); update them when a festival announces new dates.

## Debuts, prize timeline and translators
`tools/fetch_debuts.py` asks Open Library for each author's earliest listed work under their exact name (`data/debut.json`, 421 of 881 authors found); Explore → Debuts groups them by decade. It can be later than a real debut or wrong for authors who share a name. Prizes → Timeline and Translators are read from bios (a prize plus a year in the same sentence; "translates from <language>"), so they only cover what bios say. A shared-bookshelf view was skipped: the few titles shared between speakers are mostly co-authors or same-title mismatches.

## International festivals
Galle Literary Festival (17–21 Mar 2027) and Edinburgh International Book Festival are listed as "soon": the sites have no 2027 speaker list yet, so only dates and links are shown (Galle also appears in Upcoming). Hay Festival redirects to a host not yet allowed here.

## App and offline use
The site is only static files (HTML, JSON, images, fonts): there is no server code, database or build step. Host the folder on any static host (GitHub Pages works) and open it over https. It is also an installable app (`manifest.webmanifest`, `sw.js`): after the first visit the page, every festival's data and the pages and photos you have viewed work offline, and About → Install app (or the browser's "Add to Home screen") puts it on your phone. Opening `index.html` straight from a folder (file://) will not work, because browsers block loading the JSON files that way; run `python3 -m http.server` in the folder instead. Bookmarks: star speakers, and tap ☆ on a festival's title line to bookmark it; both appear in Explore → Bookmarks and are kept in your browser. Bump `VERSION` in `sw.js` when changing `index.html`.
