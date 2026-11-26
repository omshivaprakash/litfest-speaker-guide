# LitFest Guide open dataset

Facts about literature festivals and the people who speak at them, as plain CSV files with stable IDs. Licence: **CC BY 4.0** (see `../LICENSE-DATA.md`).
Attribution: *LitFest Guide (omshivaprakash), https://omshivaprakash.github.io/litfest-speaker-guide/, CC BY 4.0, version `<version>`.*

## Where to get it
| What | Address |
|---|---|
| Latest release | `https://omshivaprakash.github.io/litfest-speaker-guide/dataset/latest/` (for example `.../people.csv`) |
| A fixed version (use this in papers and products) | `https://omshivaprakash.github.io/litfest-speaker-guide/dataset/releases/<version>/` |
| Everything in the repository | `dataset/` on GitHub; each release is also a git tag `data-<version>` and a GitHub release with a zip |
| What changed | [`CHANGELOG.md`](CHANGELOG.md) |

## Versions
Versions are **dates**: `2026.11.26`, and `2026.11.26.2` if the data changes again the same day. A new version is made only when a file's content changes.
Old versions are never edited. `latest/manifest.json` lists the version, the record counts and a SHA-256 checksum for every file, so you can check what you downloaded.
`datapackage.json` describes the files in the Frictionless Data format.

## Files
| File | One row per | Columns |
|---|---|---|
| `festivals.csv` | festival | `festival_id`, `name`, `short_name`, `status` (live or soon), `city`, `state`, `country`, `official_site`, `next_edition_start`, `next_edition_end`, `first_year_in_data`, `latest_year_in_data` |
| `people.csv` | person | `person_id`, `name`, `profession_guess`, `country_from_bio`, `first_year`, `last_year`, `festival_count`, `appearance_count` |
| `appearances.csv` | person at a festival in a year | `person_id`, `festival_id`, `year` |
| `prize_wins.csv` | dated prize win read from a bio | `person_id`, `prize`, `year`, `source` |
| `translators.csv` | person who translates | `person_id`, `translates_from`, `translates_into`, `language_pairs`, `translated_books_named` |
| `childrens_strands.csv` | children's session | `festival_id`, `strand`, `edition_year`, `session`, `presenter`, `time_or_age_note` |
| `press_coverage.csv` | press link listed by a festival | `festival_id`, `year`, `outlet`, `language`, `headline`, `url`, `topics` |

## Stable IDs
- `festival_id` is the short code used in the app (`blf`, `jlf`, `hlf`…) and does not change.
- `person_id` is the person's name, lower-cased, without titles or accents, with spaces turned into dashes (`abhijit-banerjee`). People who appear under different spellings are joined using a small alias list. If two people share a name they share an ID: this is a known limit. IDs can change only when a spelling is corrected, and the changelog says so.

## Read this before you rely on it
- **Names and appearances** come from each festival's own public pages. A festival that stops listing someone removes them from later versions.
- **Derived fields are guesses**: `profession_guess` and `country_from_bio` are read from bios; prize years and translator language pairs are read from sentences in bios; press topics come from headline words. Gender is deliberately not included.
- **History is uneven**: some festivals have ten years, some one. "First time" only means not found in the lists we hold.
- Not included: photographs, logos, covers, biographies and article text (see `../LICENSE-DATA.md`).

## Rebuilding
`python3 tools/build_release.py` makes a new release from the repository's data; `--auto` makes one only if something changed.
