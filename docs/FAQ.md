# Frequently asked questions

## About the project

**Who made this, and why?**
A reader who got tired of opening a dozen festival websites to work out who was speaking where, and who had been there before. It is built as a free tool for other readers, and as an open, reusable record of Indian literature festivals.

**Is it official? Is it run by a festival?**
No. It is independent and not affiliated with, endorsed by or sponsored by any festival. Each festival's own site is the final word on its programme.

**Does it cost anything? Will it?**
No, and no. There are no ads, no accounts and nothing for sale. It runs on free hosting because it is just a folder of files.

**Why is it called a "guide" and not a "database"?**
Because the goal is to help you *decide* which festival to attend and who to see, not just to store lists.

**Can I use the data?**
Yes. The code and the data files we made are MIT licensed. Names, photos, bios and logos belong to their owners and come from the festivals' public pages; please respect that and credit the festival when you reuse them.

---

## About accuracy

**Why does it say "Country not stated" or "gender not stated" for some people?**
Because the bio does not say, and we do not guess beyond the text. Gender comes only from *she/her* or *he/his* in the bio; country from a place or nationality named there. Better blank than wrong.

**What does "First-time" really mean?**
That we did not find the name in the earlier lists we have. If a festival's history only goes back two years, "first-time" is a weaker statement. The Past years tab says "earliest edition on record" for the first year we have.

**Someone is listed as first-time but has definitely been before.**
Probably our earlier lists do not cover that year, or the name was spelled differently. Tap **Report an error** on their sheet.

**Why do some people appear twice?**
Spelling variants. The app already treats "K S Nair" = "KS Nair" and ignores a lone middle initial, plus a short hand-checked list. Others (like "Ananth" vs "Anantha") are kept apart on purpose, because merging two real people is worse.

**Are the books always right?**
Almost always, but books are matched by author name on Open Library, so a same-name author could slip in. Where a book came from the speaker's own bio, that is marked.

**The prize / debut / translator lists look incomplete.**
They only know what bios say, and Open Library's earliest listed work. They are leads for browsing, not a record of awards. Check the awarding body for facts.

**A festival's list is much smaller than I expected.**
Many festivals announce speakers in stages, so a list can be partial for months. The **Daily check** notices when a festival adds names. See [Data notes](DATA-NOTES.md) for what each festival has.

**Why does a past speaker have no bio or photo?**
Because the festival's archive never published one. We still list the person and say so.

---

## About privacy and fairness

**What do you store about me?**
Nothing. Your stars, bookmarks, reminders and language are saved in your own browser only.

**Does it track me or use cookies?**
No tracking, no analytics, and no third-party requests when a page loads.

**I am an author and want my information corrected or removed.**
Please [open an issue](https://github.com/omshivaprakash/litfest-speaker-guide/issues/new) with your name, the festival and what to change. Requests from the people and festivals listed here are welcome and taken seriously.

**Is the gender chart judging people?**
It is a simple count to show how festival line-ups change over time. It covers only people whose gender is stated in their bio, and the chart says how many that is.

---

## Using the site

**Does it work without internet?**
Yes, after you have opened it once. Photos and covers appear offline once you have viewed them.

**How do I install it?**
Open **About → Install app**, or use your browser's *Install* / *Add to Home Screen* option.

**Can I open it by double-clicking `index.html`?**
No. Browsers block loading the data files that way. Use a web address, or run `python3 -m http.server` in the folder and visit `http://localhost:8000`.

**How do I get a reminder for a festival?**
**Explore → Upcoming → Remind me**, or **Add to calendar** to download a calendar file with a reminder the day before. Reminders show as a banner when you open the site, because the site has no server to message you while it is closed.

**What is the "Daily check"?**
An automatic job that compares each festival's live speaker page with the last copy and records changes. See **About → Daily check**.

---

## For the technically curious

**Why no server or database?**
Cheaper, faster, safer, works offline, and nothing to maintain or hack.

**Why plain JavaScript, no framework?**
So there is nothing to install or rebuild: open the folder and it runs. It also keeps the page small.

**How do I add a festival?**
See [Maintaining](MAINTAINING.md).

**How do I know it isn't broken?**
Tests open every festival, tab and window on a phone and a laptop on every change, and a data check confirms every photo, logo and date. See [How it works](HOW-IT-WORKS.md).
