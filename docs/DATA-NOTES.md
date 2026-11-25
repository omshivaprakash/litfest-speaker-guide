# Data notes

Festival-by-festival notes on where each festival's data came from, what is complete and what is not. This is the technical reference behind the plain-language [README](../README.md). For field meanings see the [data dictionary](DATA-DICTIONARY.md); for how to refresh a festival see [Maintaining](MAINTAINING.md).

> Counts in the tables below were true when each festival was added; the live app (and `festivals.json`'s `updated` line per festival, shown in **About**) is the source of truth.

---

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
| Neev Literature Festival 2026, 26–27 Sep (`?f=nlf`) | Live: 70 speakers for 2026 (with bios and photos), history 2017–2025 |
| Kalinga Literary Festival 2026, 8–11 Jan (`?f=klf2`) | Live: 132 speakers with bios and photos; earlier years list featured names only (2021, 2022, 2024) |
| Goa Arts and Literature Festival 2026, 12–14 Feb (`?f=galf`) | Live: 28 speakers with bios and photos; history 2023–2025 (2023 lists only a few names) |
| Dehradun Literature Festival 2026, 27–29 Nov (`?f=ddlf`) | Live, thin: 55 speakers (names and photos), 2025 history only |
| Bhopal Literature & Art Festival 2027, 8–10 Jan (`?f=bplf`) | Live: 65 speakers announced so far (with bios), history 2019–2026 |
| Mathrubhumi International Festival of Letters 2027, 28–31 Jan (`?f=mbifl`) | Live, thin: 6 speakers announced so far; history 2018–2020 and 2023–2026 |
| Wayanad Literature Festival 2026, 19–23 Dec (`?f=wlf`) | Live: 67 speakers announced so far (bios, photos), history 2022 and 2024 |
| JSW Sahitya Habba 2026, 28–29 Nov (`?f=jsw`) | Live: programme of 20 sessions and 27 photographed speakers, typed from the festival's agenda PDF |
| Jaipur Literature Festival 2027, 14–18 Jan (`?f=jlf`) | Live: 280 speakers announced so far; history 2018–2026 |

## General notes on the data
Built from each festival's public speaker pages, bios and schedules, plus Open Library for book covers. Gender is inferred only from pronouns in bios, so it is missing for some speakers. Photos, logos and book covers belong to their owners and are used here for identification.

Run locally: `python3 -m http.server` and open http://localhost:8000/.

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

## Kerala data
Built by `tools/build_klf.py` from the speakers and sessions files the festival's own site loads, plus the 2023 and 2024 programme pages in its archive; books come from titles in italics in the bios and Open Library (`tools/add_books_ol.py`). 2025 has no usable list in the archive, so history covers 2023, 2024 and 2026 and "first-time" means not seen in those years. The next edition is announced for 21–24 January 2027 with no line-up yet.

## Mumbai (Literature Live!) data
Built by `tools/build_tll.py` from litlive.in: the speakers pages for 2024–2026, each 2026 speaker page (bio, sessions) and the festival's "Books at the LitFest" lists for 2025 and 2026. The festival states each speaker's role and country, so those are not guessed. Earlier years (before 2024) are not on the site in the same form.

## Bengaluru Poetry Festival data
Built by `tools/build_bpf.py` from bengalurupoetryfestival.org: the 2026 poets page (bios, photos) and each past year's archive page (poet names). The festival was not held in 2021, so that year is absent. Language and country are read from bios; books and ages are not included.

## Kolkata data
Built by `tools/build_klm.py` from kolkatalitmeet.in (each year's site lists its speakers; the 2026 pages give bios, photos and sessions) plus books from bio titles and Open Library (`tools/add_books_ol.py`). The 2020–2022 sites use a different layout and are not included, so history starts in 2023.

## Neev data
Built by `tools/build_nlf.py` from the festival site's public WordPress API (`/wp-json/wp/v2/speaker`, tagged by event year): every speaker post for 2017–2026, with bios and photos for the 2026 edition. Speakers of the Reading Challenge are marked separately. Names are matched across years by spelling. No books are listed yet.

## Kalinga data
Built by `tools/build_kalinga.py` from the /klf-speakers/ page of kalingaliteraryfestival.com, which tags each speaker by edition. The current edition is listed in full; 2021, 2022 and 2024 list only a few featured names, so history is partial. Books come from titles in bios and Open Library (`tools/add_books_ol.py`).

## Goa data
Built by `tools/build_galf.py` from the yearly speaker pages of goaartlitfest.com (speaker-2023 to speaker-2026). The site lists a modest number of names per year and some bios sit in image captions, so counts are lower than the festival's full programme. Country and gender are guessed from those bios.

## Dehradun data
Built by `tools/build_ddlf.py` from the Wix pages of www.dehradunliteraturefestival.com: /team (2026 speakers, names and photos only) and /archives (the 2025 list; the other year tabs there load on demand and are not included). There are no bios, so gender, country and role are unknown.

## Bhopal data
Built by `tools/build_bhopal.py` from bhopalliteraturefestival.com: `/event/blf-YYYY/speakers` for 2019–2027 and the 2027 author pages for bios. The 2027 list is partial (announced so far). Gender, country and role come from the bio text only; unknown where the bio is silent. No books are listed yet.

## MBIFL data
Built by `tools/build_mbifl.py` from www.mbifl.com, assets.mbifl.com and english.mathrubhumi.com: the 2027 speaker feed (only a few announced so far; re-run to refresh), the 2026 speakers page, the 2025 feed (first 20 per Regional/National/International list, so 2025 is partial), 2024 and 2018–2020 feeds, and the 2023 page. There was no festival in 2021 or 2022. Names are matched across years by normalised spelling, so some repeat guests may be missed. Books come from Open Library (exact author-name match).

## Debuts, prize timeline and translators
`tools/fetch_debuts.py` asks Open Library for each author's earliest listed work under their exact name (`data/debut.json`, 421 of 881 authors found); Explore → Debuts groups them by decade. It can be later than a real debut or wrong for authors who share a name. Prizes → Timeline and Translators are read from bios (a prize plus a year in the same sentence; "translates from <language>"), so they only cover what bios say. A shared-bookshelf view was skipped: the few titles shared between speakers are mostly co-authors or same-title mismatches.

## Translators
`tools/build_translators.py` writes `data/translators.json`. A person counts as a translator when their role is Translator or a bio sentence says they translate (a book of theirs *being translated* does not count). 429 people qualify. Language directions come from phrases such as "translates from Kannada into English" or "Hindi-English translator" (52 people state one); for the rest the app shows the languages they write in, labelled as direction not stated. Translated books come from bio phrases such as "her translation of S Hareesh's Moustache" and from Open Library's translator credits, which are thin (85 books for 53 people). The source sentence is kept in the file so each claim can be checked. Explore → Translators shows the totals, the commonest language pairs and the people behind each.

## Professions
Each person's `role` is guessed from their bio (see `tools/pastlib.py`). The app groups roles into families for colour: Journalism, Book trade (publishing, translation), Public life (politics, diplomacy, civil service, activism), Academia (scholars, historians, economists), Science and medicine, Business, Arts and music, and Film and stage. Generic roles ("Speaker", "Author", "Poet") are not highlighted. Families are matched by words in the role text, so an unusual role may fall outside them.

## Children's strands
`tools/build_kids.py` writes `data/kids.json`. Strands come from the festivals' own pages where they publish one (Hyderabad **Dreamcatchers**, with age groups; Bengaluru Poetry Festival **Children's Fest**, with its two-day schedule and 25 facilitators) and from our own programme data (**Children's KLF** sessions, JSW **Chinnarangala**, Book Brahma **Chinnara Loka**, and Bangalore Literature Festival's **C|L|F (Children | Literature | Fun)**, read from the festival's own schedule pages for 2016 to 2019 and 2022 to 2025, about 460 sessions; 2020 and 2021 have no C|L|F page on the site. The 2016 and 2017 pages give age bands but few presenters, and the 2018 page lists two venues side by side, so some presenters are blank). Neev is listed as a children's-books festival because it describes itself that way. Most festivals publish only names, not session-level programmes, so the list is a floor. The **Children's** tag and filter on speakers marks people whose role, a session title or bio clearly points to children's or young-adult work (picture books, "writes for children", Bal Sahitya and similar); it reads text, so some people are missing and a few may be wrong.

## Prize effect
`tools/build_insights.py` writes `data/prize-effect.json`. It reads bio sentences that say a person won a named prize with a year next to it ("won the 2021 Booker Prize"), skips shortlists, longlists, juries and state-level academies, and lines the year up with the festival years in `history-all.json` (2013 to 2027). It reports how many winners spoke in the win year or the year after, and compares that with the same people's appearance rate in the years around it. This shows an association; it cannot show that a prize caused an invitation. Only people who spoke at one of these festivals are in the data, and a prize with no year in the bio is not counted.

## International festivals
Hay Festival Winter Weekend (26–29 Nov 2026) is live as a programme festival: 65 events across 5 venues, from the programme pages on hayfestival.com (`tools/build_hayww.py`; speakers are named where the listing gives names). Galle Literary Festival (17–21 Mar 2027), Edinburgh International Book Festival and Hay Festival 2027 are listed as "soon": the sites have no 2027 speaker list yet, so only dates and links are shown (Galle also appears in Upcoming). 

## Wayanad data
Built by `tools/build_wlf.py` from wlfwayanad.com's WordPress API: the 2026 speaker posts (with photos from the speakers page) and the speaker posts of the archived 2022 and 2024 sites. There was no festival in 2023 or 2025. Gender, country and role come from bios only; books are Open Library matches.

## JSW Sahitya Habba data
`tools/build_jsw.py` holds the programme typed from the festival's 8-page agenda PDF (Canva) and crops the speaker photos from its first page. The PDF gives no website, so the festival has no official-site link. English titles beside the Kannada session titles are our own translations. Evening performances and film screenings are included with the times printed in the PDF; venues for the evening programme are not stated.

**Wayanad's earlier editions** (2022 and 2024) live in `festivals/wlf/past.json`: profiles, bios and photos of everyone who spoke then but is not in the 2026 list (built by `tools/build_past_wlf.py` from the archive sites). They open in the **Past years** tab.

## Past years
Every speaker-type festival has a **Past years** tab: pick an edition (for example last year) to see who spoke that year, how it compares with the year before, and filter to first-timers, returning speakers, those back in the next edition, or those also at the current edition. People in the current list open their full profile; people who only appear in the history show by name. It reads each festival's `history.json`.

## Past speakers (`past.json`)
Each festival may have `past.json`: the same profile records as `data.json` for people who spoke in earlier editions but are not in the current one (photos in `pph/`). The Past years tab loads it so those people open the same profile sheet. `tools/pastlib.py` is the shared builder; a festival's own `tools/build_past_*.py` fills it. 'First time' only ever means no earlier appearance in the editions we have; a festival's earliest edition on record is labelled as such.

### Past-speaker coverage
Past-only people with profiles (photo, and bio where the festival published one): BLF 1,884 (2012 to 2025, bios; 1,659 with photos), JLF 2,264 (2018 to 2026), HLF 1,065 (photos; bios only for 2026), Neev 327, BPF 559 (photos only), Bhopal 488, MBIFL 443 (2026 bios and photos, 2024 photos; other years name-only), Wayanad 171, Kolkata 296, Tata Literature Live 180, Goa 79. Not available: Kerala (its archive site lists no speakers), Dehradun (names only), Kalinga (earlier editions are all in the current list), and the programme-style festivals. People who only appear in `history.json` still show by name in Past years. Builders: `tools/build_past_*.py`; then `tools/drop_placeholder_photos.py`, `tools/shrink_past.py` and `tools/build_index.py` (which flags festivals that have a `past.json`).

---

*Other topics that used to live here moved to: [User guide](USER-GUIDE.md) (features, keyboard, offline, language), [Maintaining](MAINTAINING.md) (adding festivals, checks, daily check), [Data dictionary](DATA-DICTIONARY.md) (formats, programme data) and [FAQ](FAQ.md) (disclaimer, name matching).*

## Mysuru Literature Festival
`tools/build_mysuru.py` reads mysuruliteraturefestival.com. The 10th edition (4 to 5 July 2026) comes from the site's speaker feed: 110 people with bios and photos, some bios in Kannada. The festival's official dates for the next edition are 3 to 4 July 2027; its speakers are not announced yet, so the countdown points to 2027 while the speaker list is the 2026 one. Earlier editions 2017 to 2022 are name lists read from each edition's page (2020 and 2021 were online); 2023 to 2025 pages show pictures only, so those years are not captured. Mysuru also has a separate Mysuru Literary Fest run by the Mysore Literary Association (Jan 2025 was its sixth edition), which is not covered yet.

## Koshala, Ahmedabad and Shillong
Added from the festivals' own sites. **Koshala** (`tools/build_koshala.py`): the speakers page has a tab per year (2022 to 2026) and a detail page per speaker; 2026 (27 to 30 Nov) is the current list, earlier years are history and past profiles. **Ahmedabad** (`tools/build_ailf.py`): the 11th edition (24 to 25 Oct 2026) speaker page, 66 speakers with bios; earlier editions from 2016 are not captured yet. **Shillong** (`tools/build_shillong.py`): the Edition VI page, 12 speakers with bios (12 to 14 Nov 2026); editions I to V are shown on the site only in a form we cannot read. All three are watched by the daily check.

## Listed but not yet filled in
**CLF Literati** (official dates 4 to 6 Dec 2026, Sukhna Lake): the 2026 speaker list is not out; the site's archive lists speakers back to 2013 and can be added when the festival activates. **Nalanda** (main festival Oct 2027 at Rajgir, with city dialogues beforehand) and **Khushwant Singh Literary Festival** (held 23 to 25 Oct 2026): speaker lists not captured yet. **Work in progress** (`wip` in `festivals.json`): Lit for Life, Apeejay Kolkata Literary Festival, M.S. Randhawa, Pune International Literary Festival and Times LitFest. For Pune, the address a directory listed (`pilf.in`) now redirects to an unrelated site, so it is not used.

