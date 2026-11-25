# Maintaining LitFest Guide

For the person who keeps the data fresh. Each section says **when** and **how**.

> You need Python 3 (with the `Pillow` package) for the tools, and Node.js with `playwright` for the tests. Nothing is needed just to *view* the site.

---

## The daily routine (mostly automatic)

Every day at **02:23 UTC** (about 07:53 IST), GitHub runs `.github/workflows/daily-check.yml`. It:

1. Runs `tools/check_updates.py`: reads each festival's live speaker page, compares with the last copy, and records changes.
2. Runs `tools/check_dates.py`: lists festivals whose dates are stale or whose sites stopped answering.
3. Commits the report to `data/`.
4. **Opens a GitHub issue** called *"Speaker list changes <date>"* when a list changed.

You can also run it by hand from the **Actions** tab (*daily-check → Run workflow*) or locally:

```
python3 tools/check_updates.py
```

Read the result in **About → Daily check** on the site, or in `data/updates.json`. Look for:
- `added` / `removed`: what changed on the festival's site.
- `not_in_app`: names live on the site that the app does not have yet. **This is your to-do list.**
- `status: fetch problem`: the site layout probably changed. The old copy was kept; the scraper for that festival needs a look.

---

## When a festival announces more speakers (refresh its data)

1. Run that festival's builder, e.g. `python3 tools/build_hlf.py RAWDIR`. (Some builders need saved pages; the top of each file says exactly what it needs.)
2. If it also has earlier-years profiles, run its `build_past_<id>.py`.
3. Post-process:
   ```
   python3 tools/add_books_ol.py festivals/<id>      # books from Open Library (optional)
   python3 tools/to_webp.py                          # photos to WebP
   python3 tools/drop_placeholder_photos.py          # remove shared placeholder images
   python3 tools/shrink_past.py                      # keep past photos small
   python3 tools/build_index.py                      # rebuild the combined history, flag past.json
   python3 tools/build_kids.py                       # children's strands and people (reads two official pages)
   python3 tools/build_insights.py                   # prize effect: win year against festival appearances
   ```
4. Validate and test (see below), then re-run `python3 tools/check_updates.py` so the snapshot matches.
5. Stamp and publish:
   ```
   python3 tools/stamp.py
   git add -A && git commit -m "Refresh <festival>" && git push
   ```

`tools/stamp.py` gives the files a new build id so visitors' browsers and installed copies refresh.

---

## Adding a new festival

1. **Look for a data feed first.** Many festival sites are WordPress and expose speakers at `/wp-json/wp/v2/...`; others have a JSON API their own page calls. A feed beats scraping HTML.
2. Copy the nearest existing builder (for example `tools/build_nlf.py` for a WordPress site) to `tools/build_<id>.py` and adapt it. It must write `festivals/<id>/data.json`, `stats.json` and `history.json`, and photos to `ph/`.
3. Save a logo as `festivals/<id>/logo.png` (use the festival's real logo; check it is not blank or white on white).
4. Add an entry to `festivals.json` (see the [data dictionary](DATA-DICTIONARY.md)). Include `start`, `end`, and `country`, `state` and `city` (they drive the home-page region filters).
5. Add the festival to `PROBES` in `tools/check_updates.py` so it is watched daily.
6. Run the post-processing steps above, then `python3 tools/validate.py` and the tests.

**Festivals with only a printed schedule** (no website list): make a programme-type entry. See `tools/build_jsw.py` for a worked example typed from a PDF.

**Festivals with no list published yet:** add an entry with `"status": "soon"`, dates and a `note`. It appears on the home page and in Upcoming.

---

## Checking quality before you publish

```
python3 tools/validate.py          # data: files, photos, dates
python3 -m http.server 8765 &      # a local server
npm i playwright axe-core          # once
node tests/run.js                  # layout and errors on every festival, tab, window; accessibility
```

The tests fail if any page scrolls where it should not, any script errors, any file is missing, or an accessibility rule is broken. GitHub runs the same checks on every push (`.github/workflows/check.yml`).

---

## Tool reference

| Tool | Purpose |
|---|---|
| `build_<id>.py` | Build one festival's current edition |
| `build_past_<id>.py`, `pastlib.py` | Build profiles of earlier-edition speakers |
| `build_history.py`, `build_index.py` | Combine histories; mark festivals with past profiles |
| `add_books_ol.py`, `add_jlf_books.py`, `fetch_debuts.py` | Books and earliest-work years from Open Library |
| `to_webp.py`, `shrink_past.py`, `drop_placeholder_photos.py` | Photo clean-up |
| `place_names.py`, `tag_themes.py` | Map places and themes for the Karnataka programme festivals |
| `validate.py` | Data checks |
| `check_dates.py`, `check_updates.py` | Date and speaker-list monitoring |
| `stamp.py` | New build id for cache refresh |

---

## Changing the app itself

- Screens and behaviour: `index.html` (main), `explore.js` (Explore window), `i18n.js` (Kannada/Hindi labels).
- After any change, run `python3 tools/stamp.py` so installed copies refresh.
- Keep the rule that **no screen scrolls the page**: each tab fits one screen and pages through its content. `tests/run.js` enforces this at three sizes.

---

## Housekeeping notes

- **Photos:** all images live in the repo (WebP). The repo is roughly 115 MB, which is fine for GitHub Pages (limit 1 GB).
- **Bot commits:** the daily check commits as "litfest-check".
- **Git history:** old JPEGs were removed from history once to keep the clone small. Avoid committing large uncompressed images.
- **Hosting:** GitHub Pages, branch `main`, folder `/ (root)`.
