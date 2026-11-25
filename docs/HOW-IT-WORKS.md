# How it works (without jargon)

This page explains how LitFest Guide is put together. You do not need to be a programmer to follow it.

## The big idea

> A website can be just **files**: a page, some lists, some pictures. If nothing needs to be calculated on a computer somewhere, you do not need a server, and it costs nothing to keep running.

LitFest Guide is exactly that. When you open it, your own phone or laptop reads the files and draws the screens. Nothing is sent back.

```
 Festival websites            Our tools (scripts)             The repo (this folder)            You
 ───────────────────         ─────────────────────         ────────────────────────       ───────────────
 each publishes its   ──►    read the public pages    ──►   data files + photos     ──►    your phone or
 own speaker list            and tidy them up               + one web page                  laptop shows it

        ▲                                                                                       │
        └──────────  every day a check looks for changes and writes a report  ─────────────────┘
```

## The pieces

### 1. The page: `index.html`
One file holds the whole app: the screens, the colours, the logic. It has no outside dependencies. (A second small file, `explore.js`, holds the Explore screens and loads only when you open Explore. `i18n.js` holds the Kannada and Hindi labels.)

### 2. The list of festivals: `festivals.json`
One entry per festival: name, dates, venue, official website, logo, and which years we have. Add an entry and a new festival appears.

### 3. The data: `festivals/<festival>/`
Each festival has a folder containing:

| File | What it is |
|---|---|
| `data.json` | The **current** edition's speakers: name, bio, photo, role, country, books and so on |
| `history.json` | Just **names, by year**: who spoke in each past edition |
| `past.json` | Full **profiles of people who spoke in earlier years** but are not in this year's list |
| `stats.json` | Pre-counted numbers for the charts |
| `logo.png` | The festival's logo |
| `ph/`, `pph/` | Photos: current speakers (`ph`) and earlier speakers (`pph`) |
| `bk/` | Book covers |

### 4. The tools: `tools/`
Small Python scripts that collect the data. For each festival there is a `build_<festival>.py` that reads that festival's public pages (or the same data feed its own website uses) and writes the files above. Other tools check quality, shrink photos, and run the daily check. They are only needed when updating data, never to *use* the site.

### 5. The offline copy: `sw.js`
A small helper (a "service worker") that saves the site on your device after your first visit, so it opens without internet.

### 6. The checks: `tests/` and `.github/`
- `tests/run.js` opens every festival, tab and window on a small phone and a laptop, and fails if anything scrolls the wrong way or throws an error.
- `tools/validate.py` checks that every photo, logo and date in the data actually exists and makes sense.
- GitHub runs both on every change, so a mistake is caught before visitors see it.
- A **daily check** (`tools/check_updates.py`) looks at each festival's live speaker page.

## How the guesses are made

A festival page gives us a name, a photo and a bio. Everything else is read from the bio text by simple rules, never by an AI that makes things up:

| Field | Rule |
|---|---|
| **Gender** | Counts *she/her* against *he/his* in the bio. Left unknown if the bio is silent or mixed. |
| **Country** | The first country or city named in the bio, or what the festival itself states. |
| **Role** | Keywords such as "journalist", "poet", "director". |
| **Language** | Phrases like "writes in Tamil" or "Hindi poet", or what the festival states. |
| **First time** | The name is not in any earlier list we have. |
| **Books** | Titles in the bio, or Open Library works whose author name matches exactly. |
| **Same person across festivals** | Names are compared after removing titles, accents, dots and spacing in initials, plus a short hand-checked list of spelling variants. |

Because they are guesses, every one of them can be wrong, and the app shows "not stated" rather than inventing an answer.

## Why photos and fonts are inside the repository

So that the site makes **no requests to outside companies** when it loads. It is faster, works offline, and cannot leak your visit to anyone.

## Where it is hosted

On **GitHub Pages**, a free service that publishes a folder of files as a website. Every time the maintainer pushes a change, the site updates itself.

## What it deliberately does *not* do

- No accounts, no sign-up, no comments.
- No tracking or analytics.
- No server that could go down or be hacked.
- No selling of anything.
